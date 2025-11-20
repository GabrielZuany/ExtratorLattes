from PontuacaoPIIC.Orientador import Orientador

class Submissao():

    def __init__(self, orientador: Orientador, area: int):
        self._area = area
        self._orientador = orientador
        self._pontuacao = None
    
    def get_area(self):
        return self._area()
    
    def get_orientador(self):
        return self._orientador
    
    def get_pontuacao(self):
        return self._pontuacao
    
    def add_pontuacao(self, ano_inicio: int, ano_fim: int, json_table_path: str, qualis_path: str):
        # Para evitar import circular
        from PontuacaoPIIC.Pontuacao import Pontuacao

        self._pontuacao = Pontuacao(self, json_table_path, qualis_path)
        self._pontuacao.calcula_nota(ano_inicio, ano_fim)