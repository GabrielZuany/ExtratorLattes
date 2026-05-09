"""
Módulo de pré-processamento de texto para o pipeline QualisLens.

Responsável por:
- Normalização de texto (lowercase, remoção de pontuação, acentos)
- Expansão de abreviações acadêmicas comuns
- Remoção de stopwords irrelevantes
- Separação de sigla + nome quando escritos juntos (ex: "SBRC - Simpósio...")
"""

import re
import unicodedata
from typing import Optional

# ── Mapa de abreviações → forma completa ─────────────────────────────────────
# Ordenado do mais longo para o mais curto para evitar substituições parciais.
_ABREVIACOES: list[tuple[str, str]] = [
    # (r"\bint'l\b", "international"),
    # (r"\bintl\b", "international"),
    # (r"\bconf\b", "conference"),
    # (r"\bc\b", "conference"),        # "C." isolado (ex: "Int'l C. on X")
    # (r"\bsymp\b", "symposium"),
    # (r"\beng\b", "engineering"),
    # (r"\bwksp\b", "workshop"),
    # (r"\bwkshp\b", "workshop"),
    # (r"\bwksh\b", "workshop"),
    # (r"\bproc\b", "processing"),
    # (r"\bj\b", "journal"),           # apenas quando isolado
    # (r"\btrans\b", "transactions"),
    # (r"\bsyst\b", "systems"),
    # (r"\bsys\b", "systems"),
    # (r"\bcomput\b", "computing"),
    # (r"\bcomp\b", "computing"),      # "Comp." (ex: "Theory of Comp.")
    # (r"\bcomm\b", "communications"),
    # (r"\bann\b", "annual"),
    # (r"\bintell\b", "intelligent"),
    # (r"\bappl\b", "applications"),
    # (r"\bmanag\b", "management"),
    # (r"\bnet\b", "network"),
    # (r"\bnets\b", "networks"),
    # (r"\barch\b", "architecture"),
    # (r"\barchit\b", "architecture"),
    # (r"\bdist\b", "distributed"),
    # (r"\bsec\b", "security"),
    # (r"\binfo\b", "information"),
    # (r"\bprog\b", "programming"),
    # (r"\bautom\b", "automation"),
    # (r"\btech\b", "technology"),
    # (r"\btechnol\b", "technology"),
    # (r"\badv\b", "advances"),
    # (r"\bres\b", "research"),
    # # Adicionais
    # (r"\bdes\b", "design"),
    # (r"\bsw\b", "software"),
    # (r"\bemb\b", "embedded"),
    # (r"\balg\b", "algorithms"),
    # (r"\bvis\b", "vision"),
    # (r"\bviz\b", "visualization"),
    # (r"\bsig\b", "signal"),
    # (r"\bsimul\b", "simulation"),
    # (r"\bsim\b", "simulation"),
    # (r"\bmod\b", "modeling"),
    # (r"\bpract\b", "practical"),
    # (r"\bparal\b", "parallel"),
    # (r"\bcap\b", "capability"),
    # (r"\bdet\b", "determination"),
    # (r"\bimpr\b", "improvement"),
    # (r"\bimag\b", "imaging"),
    # (r"\brecog\b", "recognition"),
    # (r"\bdetect\b", "detection"),
]

# Stopwords a remover (palavras isoladas apenas)
_STOPWORDS: frozenset[str] = frozenset({
    "on", "of", "the", "in", "and", "for", "a", "an",
    "with", "to", "at", "by", "from",
})

# Stopwords extras para extracão de acrônimo (organizadoras não entram no acrônimo)
_STOPWORDS_ACR: frozenset[str] = _STOPWORDS | frozenset({"ieee", "acm", "springer", "elsevier"})

# Padrão para detectar "SIGLA - Nome completo" ou "SIGLA: Nome completo"
# Captura siglas de 2-8 letras maiúsculas/dígitos seguidas de separador
_RE_SIGLA_NOME = re.compile(
    r"^([A-Z0-9]{2,8})\s*[-–:]\s*(.+)$",
    re.UNICODE,
)


def _strip_accents(text: str) -> str:
    """Remove acentos de uma string Unicode via decomposição NFD.

    Parameters
    ----------
    text:
        Texto de entrada.

    Returns
    -------
    str
        Texto sem acentos.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def extrair_acronimo(texto: str) -> str:
    """
    Gera acrônimo a partir do nome de uma conferência.

    Usa a primeira letra de cada token significativo (não-stopword).
    Opera sobre o texto bruto (apenas lowercase + sem acentos) para preservar
    os tokens originais antes da expansão de abreviações.

    Exemplos
    --------
    ``"International Conference on Computer Vision"`` → ``"ICCV"``
    ``"ACM Symposium on Theory of Computing"``         → ``"STC"``

    Parameters
    ----------
    texto:
        Nome da conferência em formato livre.

    Returns
    -------
    str
        Acrônimo em maiúsculas.
    """
    if not texto or not isinstance(texto, str):
        return ""
    clean = _strip_accents(texto.lower())
    tokens = re.findall(r"[a-z0-9]+", clean)
    return "".join(t[0] for t in tokens if t and t not in _STOPWORDS_ACR).upper()


def separar_sigla_nome(texto: str) -> tuple[Optional[str], str]:
    """
    Separa sigla e nome quando escritos juntos no campo `nome_conferencia`.

    Exemplos:
    - ``"SBRC - Simpósio Brasileiro de Redes"`` → ``("SBRC", "Simpósio Brasileiro de Redes")``
    - ``"ICSE: International Conf. on Software Eng."`` → ``("ICSE", "International Conf. on Software Eng.")``
    - ``"International Conference on X"`` → ``(None, "International Conference on X")``

    Parameters
    ----------
    texto:
        Valor bruto do campo `nome_conferencia`.

    Returns
    -------
    tuple[Optional[str], str]
        (sigla, nome) — sigla é None quando não detectada no texto.
    """
    if not texto or not isinstance(texto, str):
        return None, str(texto) if texto else ""

    texto = texto.strip()
    m = _RE_SIGLA_NOME.match(texto)
    if m:
        sigla = m.group(1).strip()
        nome = m.group(2).strip()
        return sigla, nome
    return None, texto


def normalizar(texto: str) -> str:
    """
    Aplica o pipeline completo de normalização a um nome de conferência.

    Etapas (nesta ordem):
    1. Lowercase
    2. Remoção de acentos
    3. Expansão de abreviações comuns
    4. Remoção de pontuação e caracteres especiais
    5. Remoção de stopwords isoladas
    6. Colapso de espaços extras

    Parameters
    ----------
    texto:
        Nome da conferência em formato livre.

    Returns
    -------
    str
        Texto normalizado.
    """
    if not texto or not isinstance(texto, str):
        return ""

    resultado = texto.lower().strip()
    resultado = _strip_accents(resultado)

    # Expandir abreviações antes de remover pontuação
    for padrao, expansao in _ABREVIACOES:
        resultado = re.sub(padrao, expansao, resultado)

    # Remover pontuação (exceto espaços)
    resultado = re.sub(r"[^\w\s]", " ", resultado)

    # Remover stopwords isoladas
    tokens = resultado.split()
    tokens = [t for t in tokens if t not in _STOPWORDS]
    resultado = " ".join(tokens)

    # Colapsar espaços
    resultado = re.sub(r"\s+", " ", resultado).strip()
    return resultado


def preprocessar_linha(
    nome_conferencia: str,
    sigla_entrada: Optional[str] = None,
) -> dict:
    """
    Pré-processa uma linha de entrada, extraindo e normalizando sigla e nome.

    Se `sigla_entrada` for fornecida, ela é usada diretamente (normalizada).
    Caso contrário, tenta extrair a sigla do próprio campo `nome_conferencia`
    via ``separar_sigla_nome``.

    Parameters
    ----------
    nome_conferencia:
        Valor bruto do campo `nome_conferencia` da planilha de entrada.
    sigla_entrada:
        Valor bruto do campo `sigla_conferencia` (pode ser None ou vazio).

    Returns
    -------
    dict
        Dicionário com as chaves:
        - ``sigla_original``: sigla fornecida pelo pesquisador (ou extraída)
        - ``nome_original``: nome limpo (sem sigla prefixada)
        - ``sigla_norm``: sigla normalizada para busca
        - ``nome_norm``: nome normalizado para busca
    """
    # Separar sigla embutida no campo nome (ex: "SBRC - Simpósio...")
    sigla_extraida, nome_limpo = separar_sigla_nome(nome_conferencia)

    # Prioridade: sigla_entrada > sigla extraída do nome
    sigla_original: Optional[str]
    if sigla_entrada and str(sigla_entrada).strip():
        sigla_original = str(sigla_entrada).strip()
    else:
        sigla_original = sigla_extraida

    return {
        "sigla_original": sigla_original,
        "nome_original": nome_limpo,
        "sigla_norm": normalizar(sigla_original) if sigla_original else None,
        "nome_norm": normalizar(nome_limpo),
    }
