from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class NaturezaTrabalho(Enum):
    COMPLETO = "COMPLETO"
    RESUMO = "RESUMO"
    RESUMO_EXPANDIDO = "RESUMO_EXPANDIDO"
    NAO_INFORMADO = "NAO_INFORMADO"

    @classmethod
    def by_tag(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            return cls.NAO_INFORMADO