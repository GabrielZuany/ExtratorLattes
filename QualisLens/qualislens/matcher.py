"""
Módulo de matching para o pipeline QualisLens.

Implementa:
- Busca exata por sigla e nome normalizado (via QualisDB)
- Fuzzy matching com rapidfuzz.token_sort_ratio, retornando top-N candidatos
- Resultado unificado com status intermediário (antes de passar pelo LLM)
"""

import json
import logging
from typing import Optional

from rapidfuzz import fuzz, process

from constants import (
    STATUS_AUTO_FUZZY,
    STATUS_EXATO,
    STATUS_LLM_MISS,
    THRESHOLD_AUTO,
    THRESHOLD_CANDIDATOS_RUINS,
    THRESHOLD_LLM,
    TOP_N_CANDIDATOS,
)
from preprocessor import preprocessar_linha, extrair_acronimo
from qualis_db import QualisDB, get_db

logger = logging.getLogger(__name__)

# Colunas internas do subset usado no fuzzy
_COL_NOME_NORM = "nome_norm"
_COL_SIGLA_NORM = "sigla_norm"


def _token_level_fuzzy(query: str, candidato: str) -> float:
    """
    Compara tokens individualmente via ``partial_ratio``.

    Lida com tokens abreviados ou truncados (ex: "comp" ≈ "computing",
    "des" ≈ "design", "vis" ≈ "vision") pois ``partial_ratio`` detecta
    substrings.

    Parameters
    ----------
    query:
        Texto de consulta normalizado.
    candidato:
        Texto do candidato normalizado.

    Returns
    -------
    float
        Score ponderado pelo comprimento dos tokens da query (0–100).
    """
    q_tokens = query.split()
    c_tokens = candidato.split()
    if not q_tokens or not c_tokens:
        return 0.0
    scores_pesos: list[tuple[float, int]] = []
    for qt in q_tokens:
        if len(qt) < 2:   # letras soltas são ruído
            continue
        best = max(fuzz.partial_ratio(qt, ct) for ct in c_tokens)
        scores_pesos.append((best, len(qt)))
    if not scores_pesos:
        return 0.0
    total_peso = sum(w for _, w in scores_pesos)
    return sum(s * w for s, w in scores_pesos) / total_peso


def _score_hibrido(
    query: str,
    candidato: str,
    acr_query: str,
    acr_candidato: str,
) -> float:
    """
    Score composto combinando quatro sinais de similaridade.

    Sinais (em ordem de confiabilidade decrescente):

    1. ``token_set_ratio``   — robusto a reordenação e subconjuntos de tokens
    2. ``token_sort_ratio``  — bom para frases com palavras na ordem diferente
    3. ``_token_level_fuzzy`` — detecta tokens abreviados/truncados (via partial_ratio)
    4. Acrônimo               — sinal secundário quando ambos têm acrônimo útil

    O score final é o máximo ponderado dos quatro sinais, preservando sempre
    o melhor sinal sem penalizar os demais.

    Parameters
    ----------
    query:
        Nome normalizado da entrada.
    candidato:
        Nome normalizado do candidato no banco.
    acr_query:
        Acrônimo extraído da entrada original.
    acr_candidato:
        Acrônimo pré-computado do candidato.

    Returns
    -------
    float
        Score entre 0 e 100.
    """
    s_tset = fuzz.token_set_ratio(query, candidato)    # melhor para subsets
    s_tsort = fuzz.token_sort_ratio(query, candidato)  # melhor para reordenação
    s_tok = _token_level_fuzzy(query, candidato)        # melhor para abreviações

    # Acrônimo: útil quando ambos têm comprimento compatível
    s_acr = 0.0
    if acr_query and acr_candidato and len(acr_query) >= 3 and len(acr_candidato) >= 3:
        s_acr = fuzz.ratio(acr_query, acr_candidato)

    return round(max(
        s_tset,
        s_tsort,
        s_tok * 0.95,   # leve penalidade: partial_ratio pode ser liberal
        s_acr * 0.88,   # sinal secundário
    ), 1)


def _candidatos_para_json(candidatos: list[dict]) -> str:
    """
    Serializa a lista de candidatos fuzzy como JSON string.

    Parameters
    ----------
    candidatos:
        Lista de dicts com chaves: sigla, nome, estrato, score.

    Returns
    -------
    str
        JSON compacto.
    """
    return json.dumps(candidatos, ensure_ascii=False)


def _busca_fuzzy(
    nome_norm: str,
    sigla_norm: Optional[str],
    acr_nome: str,
    db: QualisDB,
    ano: int,
) -> list[dict]:
    """
    Executa fuzzy matching híbrido contra o subset do quadriênio correto.

    Estratégia:
    1. Pré-filtro amplo via ``token_set_ratio`` para não perder candidatos
       que o ``token_sort_ratio`` isolado descartaria.
    2. Re-pontuação com ``_score_hibrido``: combina token_set_ratio,
       token_sort_ratio, token-level fuzzy (abreviações) e acrônimo.
    3. Matching por sigla normalizada como sinal adicional.

    Parameters
    ----------
    nome_norm:
        Nome da conferência já normalizado.
    sigla_norm:
        Sigla normalizada (pode ser None).
    acr_nome:
        Acrônimo extraído do nome original.
    db:
        Instância QualisDB.
    ano:
        Ano de publicação — define o subset do quadriênio.

    Returns
    -------
    list[dict]
        Lista de candidatos, cada um com: sigla, nome, estrato, quadrienio, score.
    """
    subset = db.get_subset_quadrienio(ano)
    if subset.empty:
        return []

    nomes_norm = subset["nome_norm"].tolist()
    acrs_candidato = subset["acronimo"].tolist() if "acronimo" in subset.columns else [""] * len(subset)

    # Pré-filtro: token_set_ratio (mais permissivo) para recolher candidatos
    pre_filtro = process.extract(
        nome_norm,
        nomes_norm,
        scorer=fuzz.token_set_ratio,
        limit=TOP_N_CANDIDATOS * 5,
    )

    # Re-pontuar com score híbrido
    candidatos_idx: dict[int, float] = {}
    for _match_str, _pre_score, idx in pre_filtro:
        score = _score_hibrido(nome_norm, nomes_norm[idx], acr_nome, acrs_candidato[idx])
        candidatos_idx[idx] = score

    # Se tiver sigla, adicionar candidatos por sigla também
    if sigla_norm:
        siglas_norm = subset["sigla_norm"].tolist()
        resultados_sigla = process.extract(
            sigla_norm,
            siglas_norm,
            scorer=fuzz.token_sort_ratio,
            limit=TOP_N_CANDIDATOS * 3,
        )
        for _match_str, score_sigla, idx in resultados_sigla:
            candidatos_idx[idx] = max(candidatos_idx.get(idx, 0.0), score_sigla)

    # Ordenar por score desc e pegar top N
    top_indices = sorted(candidatos_idx.items(), key=lambda x: x[1], reverse=True)[
        :TOP_N_CANDIDATOS
    ]

    candidatos = []
    for idx, score in top_indices:
        row = subset.iloc[idx]
        candidatos.append(
            {
                "sigla": row["sigla"],
                "nome": row["nome"],
                "estrato": row["estrato"],
                "quadrienio": row["quadrienio"],
                "score": score,
            }
        )

    return candidatos


def match(
    nome_conferencia: str,
    ano: int,
    sigla_conferencia: Optional[str] = None,
    db: Optional[QualisDB] = None,
) -> dict:
    """
    Executa o pipeline de matching para um único artigo.

    Fluxo:
    1. Pré-processamento (normalização + separação sigla/nome)
    2. Busca exata por sigla e nome
    3. Se não encontrou: fuzzy matching

    O resultado inclui sempre ``qualis_candidatos`` (top-3 do fuzzy) para
    rastreabilidade, mesmo nos casos de match exato.

    Parameters
    ----------
    nome_conferencia:
        Valor bruto do campo ``nome_conferencia``.
    ano:
        Ano de publicação.
    sigla_conferencia:
        Valor bruto do campo ``sigla_conferencia`` (pode ser None).
    db:
        Instância QualisDB (usa singleton se None).

    Returns
    -------
    dict
        Dicionário com as chaves de saída do pipeline:
        - qualis_estrato, qualis_nome_oficial, qualis_quadrienio
        - qualis_score_fuzzy, qualis_status
        - qualis_candidatos  (JSON string)
        - qualis_obs
        - _pre  (dict interno com dados do pré-processamento — usado pelo LLM)
        - _candidatos_lista  (lista interna — usada pelo LLM)
    """
    if db is None:
        db = get_db()

    # 1. Pré-processamento
    pre = preprocessar_linha(nome_conferencia, sigla_conferencia)
    sigla_norm = pre["sigla_norm"]
    nome_norm = pre["nome_norm"]
    sigla_original = pre["sigla_original"]
    acr_nome = extrair_acronimo(pre["nome_original"])

    logger.debug(
        "match | nome_norm=%r  sigla_norm=%r  ano=%s",
        nome_norm,
        sigla_norm,
        ano,
    )

    # 2. Busca exata
    exato = db.buscar_por_sigla_e_nome(sigla_original, pre["nome_original"], ano)

    # Calcular fuzzy candidatos sempre (para rastreabilidade e uso pelo LLM)
    candidatos = _busca_fuzzy(nome_norm, sigla_norm, acr_nome, db, ano)
    candidatos_json = _candidatos_para_json(candidatos)
    score_top = candidatos[0]["score"] if candidatos else 0.0

    # Flag de diferença de estrato entre quadriênios
    obs_parts: list[str] = []
    if exato and exato.get("extrapolado"):
        obs_parts.append("extrapolado")
    if sigla_original:
        ambos = db.estrato_em_ambos_quadrienios(sigla_original)
        if ambos and len(set(ambos.values())) > 1:
            detalhes = "; ".join(f"{q}={e}" for q, e in sorted(ambos.items()))
            obs_parts.append(f"estrato_diferente_entre_quadrienios: {detalhes}")

    # Detecção de sigla ambígua (mesma sigla → mais de uma conferência diferente)
    ambigua = exato.get("ambiguo", False) if exato else False

    if exato and not ambigua:
        logger.info(
            "match EXATO | sigla=%r  estrato=%s  quadrienio=%s",
            exato["sigla"],
            exato["estrato"],
            exato["quadrienio"],
        )
        return {
            "qualis_estrato": exato["estrato"],
            "qualis_nome_oficial": exato["nome"],
            "qualis_quadrienio": exato["quadrienio"],
            "qualis_score_fuzzy": 100.0,
            "qualis_score_llm": None,
            "qualis_status": STATUS_EXATO,
            "qualis_candidatos": candidatos_json,
            "qualis_llm_motivo": None,
            "qualis_obs": "; ".join(obs_parts) if obs_parts else None,
            "_pre": pre,
            "_candidatos_lista": candidatos,
        }

    # 3. Fuzzy — determinar status intermediário
    if score_top >= THRESHOLD_AUTO:
        melhor = candidatos[0]
        logger.info(
            "match AUTO_FUZZY | score=%.1f  sigla=%r  estrato=%s",
            score_top,
            melhor["sigla"],
            melhor["estrato"],
        )
        if melhor.get("extrapolado") or (exato and exato.get("extrapolado")):
            obs_parts.append("extrapolado")
        return {
            "qualis_estrato": melhor["estrato"],
            "qualis_nome_oficial": melhor["nome"],
            "qualis_quadrienio": melhor["quadrienio"],
            "qualis_score_fuzzy": score_top,
            "qualis_score_llm": None,
            "qualis_status": STATUS_AUTO_FUZZY,
            "qualis_candidatos": candidatos_json,
            "qualis_llm_motivo": None,
            "qualis_obs": "; ".join(obs_parts) if obs_parts else None,
            "_pre": pre,
            "_candidatos_lista": candidatos,
        }

    # Score < THRESHOLD_AUTO → candidatos ruins ou precisa de LLM
    if score_top < THRESHOLD_CANDIDATOS_RUINS:
        # Candidatos com score tão baixo são apenas ruído do token_sort_ratio.
        # Não adianta chamar o LLM — os candidatos não são semânticamente relevantes.
        logger.info(
            "match SEM_CANDIDATOS | score=%.1f < %d → direto para revisão",
            score_top,
            THRESHOLD_CANDIDATOS_RUINS,
        )
        return {
            "qualis_estrato": None,
            "qualis_nome_oficial": None,
            "qualis_quadrienio": None,
            "qualis_score_fuzzy": score_top,
            "qualis_score_llm": None,
            "qualis_status": STATUS_LLM_MISS,
            "qualis_candidatos": candidatos_json,
            "qualis_llm_motivo": f"Score fuzzy {score_top} abaixo do mínimo {THRESHOLD_CANDIDATOS_RUINS} — candidatos considerados ruído",
            "qualis_obs": "; ".join(obs_parts) if obs_parts else None,
            "_pre": pre,
            "_candidatos_lista": candidatos,
            "_precisa_llm": False,
        }

    # Score entre THRESHOLD_CANDIDATOS_RUINS e THRESHOLD_AUTO → encaminhar para LLM
    logger.info(
        "match FUZZY_PENDENTE | score=%.1f → encaminhar para LLM",
        score_top,
    )
    return {
        "qualis_estrato": None,
        "qualis_nome_oficial": None,
        "qualis_quadrienio": None,
        "qualis_score_fuzzy": score_top,
        "qualis_score_llm": None,
        "qualis_status": None,   # resolvido pelo LLM
        "qualis_candidatos": candidatos_json,
        "qualis_llm_motivo": None,
        "qualis_obs": "; ".join(obs_parts) if obs_parts else None,
        "_pre": pre,
        "_candidatos_lista": candidatos,
        "_precisa_llm": True,
    }
