from ArquivoInterno.Producao import TrabalhoEvento
from ArquivoInterno.enums import ClassificacaoEvento, NaturezaTrabalho


class Conference(TrabalhoEvento):

    def __init__(self, ano: int, pais: str, natureza: NaturezaTrabalho, classificacao: ClassificacaoEvento, titulo: str, venue: str, autores: list, estrato: str):
        super().__init__(ano, pais, natureza, classificacao, titulo, venue, autores)
        self._estrato = estrato

    def by_trabalho_evento(conf: TrabalhoEvento, estrato: str):
        return Conference(conf.get_ano(), conf.get_pais(), conf.get_natureza(), conf.get_classificacao(), conf.get_titulo(), conf.get_venue(), conf.get_autores(), estrato)

    def get_estrato(self):
        return self._estrato
    
    def set_estrato(self, estrato):
        self._estrato = estrato
    