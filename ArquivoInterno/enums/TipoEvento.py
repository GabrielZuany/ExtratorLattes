from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class TipoEvento(Enum):
    CONCERTO = "CONCERTO"
    CONCURSO = "CONCURSO"
    CONGRESSO = "CONGRESSO"
    EXPOSICAO = "EXPOSICAO"
    FESTIVAL = "FESTIVAL"
    FEIRA = "FEIRA"
    OLIMPIADA = "OLIMPIADA"
    OUTRO = "OUTRO"
    NAO_INFORMADO = "NAO_INFORMADO"

    @classmethod
    def by_tag(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            raise cls.NAO_INFORMADO