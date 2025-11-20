from PontuacaoPIIC.Item import Item
from PontuacaoPIIC.Grupo import Grupo
import json

"""
Funcionamento da tabela:

O funcionamento da tabela é baseado em tags, cada tag é uma produção
que o programa é capaz de considerar e ela guarda a posição do item na
tabela que está relacionado com essa produção. Com isso um item é definido 
por sua descrição, valor e as tags que ele está relacionado.

Ao definir uma tag para um item, essa tag estará ligada a posição do
item na tabela, que é uma tupla (G, I), sendo G a posição do grupo em
que o item se encontra na tabela e I a posição do item nesse grupo. Assim
a função add_producao recebe uma tag e a partir dela é capaz de incrementar
a quantidade do item correto na tabela.

Observações:

- Uma tag só pode estar relacionada a um item da tabela, pois ela serve
para guardar a posição de um item, assim ela não pode estar relacionada a
duas posições diferentes.

- Um item pode estar relacionado a várias tags diferentes, isso significa
que essas tags guardarão a mesma posição da tabela.

Exemplo:
Representação no arquivo .json:

[
{"limite": 200, 
    "itens": [{"descricao": "Artigo A1 e A2", 
                "valor": 20, 
                "tags": ["artigo_a1", "artigo_a2"]}]},
    {"limite": 100,
    "itens": [{"descricao": "Orientação científica", 
                "valor": 10, 
                "tags":["orientacao_ic"]}
            ]}
]

Considerando que o item "Artigo A1 e A2" está no grupo 0 e se 
relaciona com as tags artigo_a1 e artigo_a2, e o outro item "Orientação científica"
está no grupo 1 e se ralciona com a tag orientacao_ic, temos que essas três tags 
teriam os seguintes valores:

artigo_a1 = (0, 0)
artigo_a2 = (0, 0)
orientacao_ic = (1, 0)
"""

class Tabela:

    def __init__(self, tabela_config):
        # Todas as tags possíveis em que os itens podem estar relacionados
        # obs: cada tag deve ser relacionada com um item no máximo, mas
        # um item pode ter várias tags relacionadas diferentes
        self._tags_map = {
            "livro": None,
            "cap_livro": None,
            "artigo_a1": None,
            "artigo_a2": None,
            "artigo_a3": None,
            "artigo_a4": None,
            "artigo_b1": None,
            "artigo_b2": None,
            "artigo_b3": None,
            "artigo_b4": None,
            "artigo_c": None,
            "artigo_nc": None,
            "trabalho_inter": None,
            "trabalho_nac": None,
            "resumo_inter": None,
            "resumo_nac": None,       
            "organizacao_livro": None,
            "organizacao_evento": None,
            "traducao_livro": None,  
            "prod_tecnica": None,       
            "outra_artistica": None,
            "musica": None,
            "artes_cenicas": None,
            "artes_visuais": None,
            "programa_radio_tv": None,
            "orientacao_doutorado": None,
            "orientacao_mestrado": None,
            "coorientacao_doutorado": None,
            "coorientacao_mestrado": None,
            "orientacao_monografia": None,
            "orientacao_tcc": None,
            "orientacao_ic": None,
        }

        # Configura a tabela a partir de um json
        if isinstance(tabela_config, str):   
            self._parse_json(tabela_config)
        # Configura a tabela a partir de outra tabela
        elif isinstance(tabela_config, Tabela):
            self._configura_tabela(tabela_config)

    def get_grupos(self):
        return self._grupos
    
    def _configura_tabela(self, tabela):
        """
        Configura a tabela a partir de outra tabela com as quantidades zeradas.
        """
        self._grupos = []

        for k in self._tags_map:
            self._tags_map[k] = tabela._tags_map[k]

        for grupo in tabela.get_grupos():
            g = Grupo(grupo.get_limite(), [])
            for item in grupo.get_itens():
                g.insere_item(Item(item.get_descricao(), item.get_valor_item()))
            self._grupos.append(g)

    def _parse_json(self, json_path: str):
        """
        Configura os grupos e os itens da tabela de acordo com o arquivo json especificado 
        no caminho json_path.
        """
        
        self._grupos = []
        with open(json_path, 'r') as f:
            json_file = json.load(f)
            
            # Percorre a lista de grupos do arquivo json
            for idx_grupo, grupo in enumerate(json_file):
                new_grupo = Grupo(grupo['limite'], [])
                
                # Percorre todos os itens na lista de itens do grupo
                for idx_item, item in enumerate(grupo['itens']):
                    new_grupo.insere_item(Item(item['descricao'], item['valor']))
                    
                    # Verifica quais tags estão relacionadas a esse item
                    for tag in item['tags']:
                        if tag in self._tags_map:
                            # Verifica se é primeira vez que a tag foi encontrada no arquivo json, 
                            if self._tags_map[tag] == None:
                                # Configura a posição do item em que a tag está relacionada
                                self._tags_map[tag] = (idx_grupo, idx_item)
                            else:
                                m = f'a tag {tag} está relacionada com mais de um item da tabela do arquivo {json_path}'
                                raise(Exception(m))
                        else:
                            m = f'{tag} não é uma tag esperada'
                            raise(Exception(m))
                self._grupos.append(new_grupo)

    def add_producao(self, tag: str):
        """
        Adiciona um na quantidade da produção referente a tag passada, caso a 
        tag não esteja na tabela nada acontece.
        """
        item_pos = self._tags_map[tag]
        # Verifica se a tabela utiliza a tag
        if item_pos != None:
            # Adiciona um na quantidade do item em que essa tag está relacionada na tabela
            self._grupos[item_pos[0]].get_itens()[item_pos[1]].add_quantidade(1)
        
    def __str__(self):
        r = ""
        for i, a in enumerate(self._grupos):
            r += "Grupo: " + str(i) + "\n"
            r += str(a)
        return r