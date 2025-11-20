from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class TipoOrientador(Enum):
    ORIENTADOR_PRINCIPAL = "ORIENTADOR_PRINCIPAL"
    CO_ORIENTADOR = "CO_ORIENTADOR"

    @classmethod
    def by_tag(cls, value: str):
        return cls(value)