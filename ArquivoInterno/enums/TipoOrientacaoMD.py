from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class TipoOrientacaoMD(Enum):
    ORIENTACAO_MESTRADO = "MESTRADO"
    ORIENTACAO_DOUTORADO = "DOUTORADO"

    @classmethod
    def by_tag(cls, value: str):
        return cls(value)