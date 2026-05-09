# QualisLens

Associação automática de conferências científicas à base Qualis CAPES, com fallback para LLM local (Ollama).

---

## Uso rápido

```bash
# Apenas fuzzy matching
python qualislens/main.py --entrada data/lista.csv

# Com LLM (modelo único)
python qualislens/main.py --entrada data/lista.csv --modelo llama3.2:3b

# Com dupla verificação (2 modelos)
python qualislens/main.py --entrada data/lista.csv --modelo llama3.2:3b mistral:7b
```

**CSV de entrada** — colunas obrigatórias: `titulo_artigo`, `nome_conferencia`, `ano_publicacao`.  
Coluna opcional: `sigla_conferencia`.

---

## Estratégia de matching

O pipeline aplica três camadas em ordem de custo crescente:

```
Entrada
  │
  ▼
[1] Busca exata (sigla / nome normalizado)
      ↓ hit → EXATO
  │
  ▼
[2] Fuzzy matching híbrido
      ↓ score ≥ 75 → AUTO_FUZZY
      ↓ score ≥ 68 → encaminha para LLM
      ↓ score < 68 → LLM_MISS (ruído, revisão humana)
  │
  ▼
[3] LLM (Ollama local)  [opcional]
      ↓ confirma candidato → LLM_OK / LLM_DUPLO_OK
      ↓ rejeita           → LLM_MISS / LLM_DUPLO_DIVERGE
```

---

## Etapas do pipeline

### 1. Pré-processamento (`preprocessor.py`)

Aplicado ao nome e à sigla da conferência antes de qualquer busca:

1. **Lowercase + remoção de acentos**
2. **Expansão de abreviações** — lista curada de ~50 padrões acadêmicos comuns:
   - `int'l` / `intl` → `international`
   - `conf` / `c` → `conference`
   - `symp` → `symposium`
   - `comp` / `comput` → `computing`
   - `des` → `design`, `emb` → `embedded`, `sw` → `software`, …
3. **Remoção de pontuação**, stopwords (`on`, `of`, `the`, …) e espaços extras
4. **Separação de sigla embutida**: `"SBRC - Simpósio Brasileiro…"` → sigla `SBRC` + nome separado

### 2. Busca exata (`qualis_db.py`)

Compara sigla e nome normalizados com a base Qualis do quadriênio correspondente ao ano.  
Faz fallback automático para o quadriênio alternativo caso a conferência só apareça em um deles (marcado como `extrapolado`).

### 3. Fuzzy matching híbrido (`matcher.py`)

Quando a busca exata falha, combina quatro sinais em um **score híbrido**:

| Sinal | Métrica | O que captura |
|---|---|---|
| `token_set_ratio` | RapidFuzz | Reordenação de palavras, subconjuntos de tokens |
| `token_sort_ratio` | RapidFuzz | Ordem diferente de palavras |
| Token-level fuzzy | `partial_ratio` por token | Tokens **abreviados** (ex: `comp` ≈ `computing`, `des` ≈ `design`) |
| Acrônimo | `ratio` entre acrônimos | Nomes escritos por sigla |

Score final = `max(token_set, token_sort, token_level × 0.95, acronym × 0.88)`

**Exemplo — `"IEEE/ACM Int'l C. on Comp.-Aided Des."` → ICCAD:**
- Após expansão: `"ieee acm international conference computing aided design"`
- `token_set_ratio` já captura a maioria dos tokens corretos
- `partial_ratio("comp", "computing")` = 100 %, `partial_ratio("des", "design")` = 100 %
- Score híbrido >> limiar automático → `AUTO_FUZZY` sem precisar de LLM

### 4. Fallback para LLM (`llm_reviewer.py`)

Ativado quando o score fuzzy está entre 68 e 90 (inclusive). Envia os top-5 candidatos do fuzzy ao Ollama com um prompt estruturado pedindo:
1. Expansão semântica do nome abreviado
2. Escolha do candidato mais plausível (ou `null` se nenhum serve)
3. Nível de confiança (`alta` / `media` / `baixa`) e justificativa

Com **dois modelos**: só aceita resultado se ambos concordarem; caso contrário, marca como `LLM_DUPLO_DIVERGE` para revisão humana.

---

## Thresholds

| Constante | Valor padrão | Significado |
|---|---|---|
| `THRESHOLD_AUTO` | 75 | Score ≥ 75 → aceitar automaticamente |
| `THRESHOLD_LLM` | 60 | Score < 60 → score baixo demais; LLM opina mas humano decide |
| `THRESHOLD_CANDIDATOS_RUINS` | 68 | Score < 68 → candidatos considerados ruído; pula LLM |

---

## Coluna `confiabilidade` (no CSV de saída)

| Rótulo | Quando |
|---|---|
| *(vazio)* | EXATO ou AUTO_FUZZY — sem necessidade de revisão |
| `Alta probabilidade de acerto pela LLM` | LLM com confiança `alta` |
| `Aceitável — vale a revisão` | LLM com confiança `media`, **ou** fuzzy ≥ 80 % + ao menos um modelo com `alta` |
| `Resultado pouco confiável` | LLM com confiança `baixa` / sem resposta |
