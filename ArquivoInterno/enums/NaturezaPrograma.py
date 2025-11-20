from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class NaturezaPrograma(Enum):
    ENTREVISTA = "ENTREVISTA"
    MESA_REDONDA = "MESA_REDONDA"
    COMENTARIO = "COMENTARIO"
    PROGRAMA = "PROGRAMA"
    OUTRA = "OUTRA"
    NAO_INFORMADO = "NAO_INFORMADO"

    @classmethod
    def by_tag(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            raise cls.NAO_INFORMADO