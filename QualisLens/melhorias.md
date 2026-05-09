Implemente melhorias no sistema de fuzzy matching do projeto QualisLens para aumentar a robustez na correspondência de títulos de artigos, periódicos e conferências, especialmente em casos com:

* abreviações
* palavras truncadas
* pequenas diferenças de escrita
* ordem diferente de palavras
* pontuação inconsistente
* siglas/acrônimos

Objetivo:
Evitar depender excessivamente de LLM para resolver correspondências simples.

Requisitos técnicos:

1. Normalização textual
   Implementar uma etapa de normalização antes do matching:

* lowercase
* remoção de acentos
* remoção de pontuação
* remoção de espaços duplicados
* trimming

2. Acronym extraction
   Implementar geração automática de acrônimos/siglas a partir do título.

Exemplo:
"International Conference on Computer Vision"
→ ICCV

Ignorar stopwords comuns:

* on
* of
* the
* and
* for
* in

O acrônimo deve ser utilizado como parte do score final.

3. Melhorar fuzzy matching
   Migrar ou padronizar uso para RapidFuzz.

Priorizar:

* token_set_ratio
* partial_ratio

Evitar depender apenas de Levenshtein puro.

4. Token-level fuzzy comparison
   Adicionar comparação token-a-token para lidar com:

* palavras truncadas
* abreviações naturais
* pequenas variações

Exemplos:

* international ↔ intl
* comput ↔ computer
* vis ↔ vision

Pode utilizar:

* partial_ratio
* Jaro-Winkler
* ratio simples

5. Score híbrido simples
   Criar score final combinando:

* token_set_ratio
* acronym similarity
* token-level fuzzy similarity

Manter implementação simples e interpretável.

6. Thresholds
   Separar claramente:

* alta confiança → match automático
* média confiança → fallback opcional para LLM
* baixa confiança → rejeitar

7. Performance
   Evitar soluções pesadas:

* não usar embeddings
* não usar TF-IDF
* não usar pipelines complexos
* não usar dicionários hardcoded gigantes

A solução deve continuar leve e rápida.

8. README
   Adicionar breve documentação no README do QualisLens contendo:

* visão geral da estratégia de matching
* etapas do pipeline
* rationale técnico
* exemplos simples
* explicação do fallback para LLM

A documentação deve ser curta, objetiva e técnica.
