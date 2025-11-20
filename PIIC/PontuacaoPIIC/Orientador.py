from ArquivoInterno.PessoaLATTES import PessoaLATTES

class Orientador(PessoaLATTES):

    def __init__(self, cpf: str, caminho: str, ano_inicio: int = None, ano_fim: int = None):
        self._cpf = cpf

        self.carrega_curriculo(caminho, ano_inicio, ano_fim)

        self._submissoes = []
    
    def get_cpf(self):
        return self._cpf

    def get_submissoes(self):
        return self._submissoes

    def add_submissao(self, area: int, ano_inicio: int, ano_fim: int, json_table_path: str, qualis_path: str):
        """
        Adiciona a submissão ao orientador com a nota da submissão já calculada.

        Para o cálculo da pontuação serão consideradas as produções que estão entre 
        ano_inicio(ano mais antigo) e ano_fim(ano mais próximo), a depender das regras 
        de recém-doutor e mãe pesquisadora.
        """
        # Para evitar import circular
        from PontuacaoPIIC.Submissao import Submissao
        
        submissao = Submissao(self, area)
        submissao.add_pontuacao(ano_inicio, ano_fim,json_table_path, qualis_path)
        self._submissoes.append(submissao)

class MaePesquisadora(Orientador):
    
    def __init__(self, cpf: str, caminho: str, quantidade_anos: int, ano_inicio: int = None, ano_fim: int = None):
        super().__init__(cpf, caminho, ano_inicio, ano_fim)
        self._quantidade_anos = quantidade_anos
    
    def get_qtd_anos(self):
        return self._quantidade_anos