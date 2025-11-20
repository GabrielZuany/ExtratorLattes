from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class TipoOrientacaoMTI(Enum):
    ORIENTACAO_MONOGRAFIA = "MONOGRAFIA"
    ORIENTACAO_TCC = "TCC"
    ORIENTACAO_INICIACAO_CIENTIFICA = "INICIACAO_CIENTIFICA"

    @classmethod
    def by_tag(cls, value: str):
        return cls(value)