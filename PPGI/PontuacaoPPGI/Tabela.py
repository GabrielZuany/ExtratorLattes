import pandas as pd

from PontuacaoPPGI.Journal import Journal
from PontuacaoPPGI.Conference import Conference

def producao_tag_padrao(producao: Journal | Conference):
    if isinstance(producao, Journal):
        return 'Periódico ' + estrato_tag_padrao(producao.get_estrato())
    elif isinstance(producao, Conference):
        return 'Conferência ' + estrato_tag_padrao(producao.get_estrato())

def estrato_tag_padrao(estrato: str):
    if estrato == None:
        return 'Qualis não identificado'
    
    # Garente que fique em maiúsculo
    estrato = estrato.upper()
    # Caso o estrato tenha mais que 2 caracteres pode ser considerado 
    # como não identificado, pois não está no padrão LN ou L, 
    # sendo L uma letra e N um número.
    if len(estrato) > 2:
        return 'Qualis não identificado'
    return estrato

class Tabela():

    def __init__(self, prod_min_tag:str):
        self._inicializa_itens(prod_min_tag)
        self.prod_min = [prod_min_tag, 0]

    def _inicializa_itens(self, prod_min_descricao):
        tipos = 'Conferência,Periódico'.split(',')
        notas_qualis = 'A1,A2,A3,A4,B1,B2,B3,B4,C,Qualis não identificado'.split(',')
        self.itens = pd.DataFrame()
        
        for tipo in tipos:
            for nota in notas_qualis:
                self.itens[tipo + ' ' + nota] = [0]
                self.itens[tipo + ' ' + nota].astype(int)

    def add_qtd_prod_min(self, qtd: int):
        self.prod_min[1] += qtd

    def get_prod_min(self):
        """
            Retorna uma tupla(tag, quantidade) com as informações da produção mínima.
        """
        return (self.prod_min[0], self.prod_min[1])

    def add_qtd_by_tag(self, tag: str, qtd: int):
        if tag in self.itens:
            self.itens.loc[0, tag] += qtd

    def get_qtd_by_tag(self, tag: str):
        if tag in self.itens:
            return self.itens[tag][0]
        
    def get_all_tags(self):
        return self.itens.columns.to_list()
    
    def get_data_frame(self):
        return self.itens