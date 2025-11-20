import PontuacaoPIIC.Orientador as ori
import ArquivoInterno.Producao as prod
from PontuacaoPIIC.Tabela import Tabela
from PontuacaoPIIC.enums import TipoNotaPIIC
from PontuacaoPIIC.Submissao import Submissao
from Classificador.Qualis import Qualis

class Pontuacao():
    
    def __init__(self, submissao: Submissao, tabela_config: str | Tabela, qualis: str | Qualis):
        self._submissao = submissao
        self._pontuacao_total = 0

        if isinstance(qualis, Qualis):
            self._qualis = qualis
        else:
            self._qualis = Qualis(qualis)

        self._tabela = Tabela(tabela_config)
    
    def get_submissao(self):
        return self._submissao

    def get_pontuacao_total(self):
        return self._pontuacao_total
    
    def get_tabela(self):
        return self._tabela
    
    def get_tipo_nota(self):
        return self._tipo_nota

    def get_media(self):
        return self._media
    
    def get_qtd_anos(self):
        return self._qtd_anos

    def _insere_artigo(self, artigo: prod.Artigo):
        if artigo.get_natureza() != prod.NaturezaArtigo.COMPLETO:
            return
        
        estrato = self._qualis.get_estrato(artigo.get_issn())
        
        if estrato is not None:
            if estrato == "A1":
                self._tabela.add_producao("artigo_a1")
            elif estrato == "A2":
                self._tabela.add_producao("artigo_a2")
            elif estrato == "A3":
                self._tabela.add_producao("artigo_a3")
            elif estrato == "A4":
                self._tabela.add_producao("artigo_a4")
            elif estrato == "B1":
                self._tabela.add_producao("artigo_b1")
            elif estrato == "B2":
                self._tabela.add_producao("artigo_b2")
            elif estrato == "B3":
                self._tabela.add_producao("artigo_b3")
            elif estrato == "B4":
                self._tabela.add_producao("artigo_b4")
            elif estrato == "C":
                self._tabela.add_producao("artigo_c")
            else:
                self._tabela.add_producao("artigo_nc")
        else:
            self._tabela.add_producao("artigo_nc")

    def _insere_trabalho(self, trabalho: prod.TrabalhoEvento):
        if trabalho.get_natureza() == prod.NaturezaTrabalho.COMPLETO:    
            if trabalho.get_classificacao() == prod.ClassificacaoEvento.INTERNACIONAL:
                self._tabela.add_producao("trabalho_inter")
            else:
                self._tabela.add_producao("trabalho_nac")

        elif trabalho.get_natureza() == prod.NaturezaTrabalho.RESUMO or trabalho.get_natureza() == prod.NaturezaTrabalho.RESUMO_EXPANDIDO:
            if trabalho.get_classificacao() == prod.ClassificacaoEvento.INTERNACIONAL:
                self._tabela.add_producao("resumo_inter")
            else:
                self._tabela.add_producao("resumo_nac")

    def _insere_orientacaoMD(self, orientacao: prod.OrientacaoMD):
        if orientacao.get_tipo_orientacao() == prod.TipoOrientacaoMD.ORIENTACAO_DOUTORADO:
            if orientacao.get_tipo_orientador() == prod.TipoOrientador.ORIENTADOR_PRINCIPAL:
                self._tabela.add_producao("orientacao_doutorado")
            elif orientacao.get_tipo_orientador() == prod.TipoOrientador.CO_ORIENTADOR:
                self._tabela.add_producao("coorientacao_doutorado")

        elif orientacao.get_tipo_orientacao() == prod.TipoOrientacaoMD.ORIENTACAO_MESTRADO:
            if orientacao.get_tipo_orientador() == prod.TipoOrientador.ORIENTADOR_PRINCIPAL:
                self._tabela.add_producao("orientacao_mestrado")
            elif orientacao.get_tipo_orientador() == prod.TipoOrientador.CO_ORIENTADOR:
                self._tabela.add_producao("coorientacao_mestrado")

    def _insere_orientacaoMTI(self, orientacao: prod.OrientacaoMTI):
        if orientacao.get_tipo_orientacao() == prod.TipoOrientacaoMTI.ORIENTACAO_MONOGRAFIA:
            self._tabela.add_producao("orientacao_monografia")
        elif orientacao.get_tipo_orientacao() == prod.TipoOrientacaoMTI.ORIENTACAO_TCC:
            self._tabela.add_producao("orientacao_tcc")
        elif orientacao.get_tipo_orientacao() == prod.TipoOrientacaoMTI.ORIENTACAO_INICIACAO_CIENTIFICA:
            self._tabela.add_producao("orientacao_ic")

    def _insere_traducao(self, traducao: prod.Traducao):
        if traducao.get_natureza() == prod.NaturezaTraducao.LIVRO:
            if len(traducao.get_issn_isbn().strip()) > 0:
                self._tabela.add_producao("traducao_livro")

    def _insere_artistica_cultural(self, artisticacultural: prod.ArtisticaCultural):
        if isinstance(artisticacultural, prod.Musica):
            self._tabela.add_producao("musica")            
        if isinstance(artisticacultural, prod.ArtesCenicas):
            self._tabela.add_producao("artes_cenicas")
        if isinstance(artisticacultural, prod.ArtesVisuais):
            self._tabela.add_producao("artes_visuais")
        else:
            self._tabela.add_producao("outra_artistica")  
             
    def _insere_organizacao_evento(self, producao_evento: prod.OrganizacaoEvento):
        if producao_evento.get_tipo() in (
            prod.TipoEvento.CONGRESSO,
            prod.TipoEvento.EXPOSICAO,
            prod.TipoEvento.FEIRA,
            prod.TipoEvento.OLIMPIADA
        ):
            self._tabela.add_producao("organizacao_evento")

    def _insere_programa_radio_tv(self, producao: prod.ProgramaRadioTV):
        if producao.get_natureza() in (
            prod.NaturezaPrograma.ENTREVISTA,
            prod.NaturezaPrograma.MESA_REDONDA,
            prod.NaturezaPrograma.COMENTARIO,
            prod.NaturezaPrograma.PROGRAMA
        ):
            self._tabela.add_producao("programa_radio_tv")

    def _insere_organizacao_livro(self, producao: prod.OrganizacaoLivro):
        if producao.get_natureza() == prod.NaturezaLivro.LIVRO:
            if len(producao.get_isbn().strip()) > 0:
                self._tabela.add_producao("organizacao_livro")
    
    def _insere_livro(self, producao: prod.Livro):
        if len(producao.get_isbn().strip()) > 0:
            self._tabela.add_producao("livro")

    def _insere_capitulo_livro(self, producao: prod.CapituloLivro):
        if len(producao.get_isbn().strip()) > 0:
            self._tabela.add_producao("cap_livro")

    def _insere_producoes(self, ano_inicio: int, ano_fim: int):
        """
        Percorre todas as produções do orientador e adiciona na tabela usando a tag correspondente.

        Considera apenas as produções que estão entre o ano_inicio(ano mais antigo) e 
        o ano_fim(ano mais próximo).
        """ 
        producoes = self.get_submissao().get_orientador().get_producoes()

        for producao in producoes:
            if producao.get_ano() >= ano_inicio and producao.get_ano() <= ano_fim:
                if isinstance(producao, prod.Livro):
                    self._insere_livro(producao)        
                elif isinstance(producao, prod.CapituloLivro):
                    self._insere_capitulo_livro(producao)
                elif isinstance(producao, prod.Artigo):
                    self._insere_artigo(producao)
                elif isinstance(producao, prod.TrabalhoEvento):
                    self._insere_trabalho(producao)
                elif isinstance(producao, prod.OrganizacaoLivro):
                    self._insere_organizacao_livro(producao)     
                elif isinstance(producao, prod.OrganizacaoEvento):
                    self._insere_organizacao_evento(producao)          
                elif isinstance(producao, prod.Traducao):
                    self._insere_traducao(producao)
                elif isinstance(producao, prod.RegistroPatente):
                    self._tabela.add_producao("prod_tecnica")
                elif isinstance(producao, prod.ArtisticaCultural):
                    self._insere_artistica_cultural(producao)
                elif isinstance(producao, prod.OrientacaoMD):
                    self._insere_orientacaoMD(producao)
                elif isinstance(producao, prod.OrientacaoMTI):
                    self._insere_orientacaoMTI(producao)
                elif isinstance(producao, prod.ProgramaRadioTV):
                    self._insere_programa_radio_tv(producao)

    def calcula_nota(self, ano_inicio: int, ano_fim: int):
        """
        Calcula a pontuação considerando as produções publicadas.

        Considera apenas as produções publicadas entre o ano_inicio(ano mais antigo) e 
        o ano_fim(ano mais próximo).

        A pontuação será calculada de acordo com as regras de recem-doutor e mãe pesquisadora.
        """

        self._insere_producoes(ano_inicio, ano_fim)

        for grupo in self._tabela.get_grupos():
            self._pontuacao_total += grupo.calcula_nota()

        # Para o caso que o orientador é mãe pesquisadora, assim não pode ser 
        # recem doutor segundo o edital piic
        if isinstance(self.get_submissao().get_orientador(), ori.MaePesquisadora):
            self._tipo_nota = TipoNotaPIIC.MAE_PESQUISADORA
            self._media = self._pontuacao_total / self.get_submissao().get_orientador().get_qtd_anos()
            self._qtd_anos = self.get_submissao().get_orientador().get_qtd_anos()
        else:
            # Nota do orientador sem considerar o recem doutor
            conclusao = self.get_submissao().get_orientador().get_ano_conclusao()
            self._tipo_nota = TipoNotaPIIC.PADRAO
            self._qtd_anos = max(ano_fim - ano_inicio, 1)
            self._media = self._pontuacao_total / self._qtd_anos
            media_padrao = self._media

            # Pode ser recem doutor
            if conclusao > ano_inicio:
                denominador_recem = ano_fim - conclusao
                # O denominador minimo é 2, segundo o edital piic
                if denominador_recem < 2:
                    denominador_recem = 2
                    conclusao = ano_fim - 2

                recem_pts = Pontuacao(self._submissao, self._tabela, self._qualis)

                # Considera apenas os anos como recem-doutor
                recem_pts._insere_producoes(conclusao, ano_fim)
                for grupo in recem_pts._tabela.get_grupos():
                    recem_pts._pontuacao_total += grupo.calcula_nota()
                
                media = recem_pts._pontuacao_total / denominador_recem
                recem_pts._qtd_anos = denominador_recem
                recem_pts._tipo_nota = TipoNotaPIIC.RECEM_DOUTOR

                # A nota de recem-doutor é maior que a padrão
                if media > media_padrao:
                    self._pontuacao_total = recem_pts._pontuacao_total
                    self._tabela = recem_pts._tabela
                    self._tipo_nota = recem_pts._tipo_nota
                    self._media = media
                    self._qtd_anos = recem_pts._qtd_anos