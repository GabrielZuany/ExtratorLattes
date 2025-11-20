import sys
import PontuacaoPPGI.Tabela  as tb
from PontuacaoPPGI import PessoaPPGI
from PontuacaoPPGI.Journal import Journal
from PontuacaoPPGI.NotaInfo import NotaInfo
from PontuacaoPPGI.Conference import Conference
from ArquivoInterno.enums.NaturezaTrabalho import NaturezaTrabalho

class Pontuacao():

    def __init__(self, docente: PessoaPPGI, nota_info: NotaInfo):
        self.info = nota_info
        self.docente = docente

    def processa_pontuacao(self):
        tabela = tb.Tabela(self.info.get_prod_min_tag())
        
        for producao in self.docente.get_producoes():
            # Só considera Journal e Conference
            if not (isinstance(producao, Conference) or isinstance(producao, Journal)):
                continue

            if isinstance(producao, Conference):
                # Apenas Trabalho Completo pode ser aceito
                if producao.get_natureza() != NaturezaTrabalho.COMPLETO:
                    continue
            
            tag = tb.producao_tag_padrao(producao)
            if self.info.prod_valida_para_nota(producao.get_ano()):
                tabela.add_qtd_by_tag(tag, 1)
            if self.info.is_prod_min(tag, producao.get_ano()):
                tabela.add_qtd_prod_min(1)
        
        self.tabela = tabela

    def calcula_nota(self):
        self.nota = 0.0
        
        for tag in self.tabela.get_all_tags():
            self.nota += self.tabela.get_qtd_by_tag(tag) * self.info.valor_qualis(tag)
    
    def is_recredencia(self):
        if self.info.alcancou_nota_min(self.nota) and self.info.alcancou_prod_min(self.tabela.get_prod_min()[1]):
            return True

        return False

    def write_csv_line(self, sep = ';', file = sys.stdout):
        line = self.docente.get_nome() + sep
        line += '0' + sep
        line += str(self.nota) + sep
        line += str(self.tabela.get_prod_min()[1]) + sep
        line += str(self.is_recredencia())

        print(line, file=file)