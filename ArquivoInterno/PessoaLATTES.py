from ArquivoInterno.enums.NivelAcademico import NivelAcademico
from datetime import datetime
import ArquivoInterno.CurriculoXML as CXML

class PessoaLATTES():

    def carrega_curriculo(self, caminho: str, ano_inicio: int = None, ano_fim: int = None):
        """
        Carrega o nome, o nível acadêmico, o ano de conclusão e as produções da pessoa a partir do
        currículo LATTES.

        Obs: São carregadas as produções que estão dentro do intervalo de ano_inicio(ano mais antigo) 
        e ano_fim(ano mais próximo).
        """
        if ano_fim == None:
            ano_fim = datetime.today().year()

        if ano_inicio == None:
            ano_inicio = ano_fim - 5

        curriculo = CXML.CurriculoXML(caminho)

        self._nome = curriculo.get_nome()
         
        self._ano_conclusao, nivel_academico = curriculo.get_nivel_academico()
        
        self._nivel_academico = NivelAcademico(nivel_academico)

        self._producoes = curriculo.get_all_producoes(ano_inicio, ano_fim)

    def get_nome(self):
        return self._nome

    def get_ano_conclusao(self):
        return self._ano_conclusao
    
    def get_nivel_academico(self):
        return self._nivel_academico

    def carrega_curriculo_artigo_trabalho(self, caminho: str, ano_inicio: int = None, ano_fim: int = None):
        if ano_fim == None:
            ano_fim = datetime.today().year()

        if ano_inicio == None:
            ano_inicio = ano_fim - 5

        curriculo = CXML.CurriculoXML(caminho)

        self.nome = curriculo.get_nome()
         
        self.ano_conclusao, nivel_academico = curriculo.get_nivel_academico()
        
        self.nivel_academico = NivelAcademico(nivel_academico)

        self.producoes = curriculo.get_artigo(ano_inicio, ano_fim)

        self.producoes += curriculo.get_trabalho_evento(ano_inicio, ano_fim)

    def get_producoes(self):
        """
        Retorna a lista de todas as produções da pessoa.
        """
        return self._producoes