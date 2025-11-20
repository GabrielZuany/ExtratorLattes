from enum import Enum

# Configurado no __init__.py para uma importação mais limpa
# Valores baseados no schema XML da plataforma lattes
class NaturezaLivro(Enum):
    COLETANEA = "COLETANEA"
    TEXTO_INTEGRAL = "TEXTO_INTEGRAL"
    VERBETE = "VERBETE"
    ANAIS = "ANAIS"
    CATAGOLO = "CATAGOLO"
    ENCICLOPEDIA = "ENCICLOPEDIA"
    LIVRO = "LIVRO"
    OUTRA =  "OUTRA"
    PERIODICO = "PERIODICO"
    NAO_INFORMADO = "NAO_INFORMADO"

    @classmethod
    def by_tag(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            return cls.NAO_INFORMADO