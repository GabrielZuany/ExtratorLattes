import pandas as pd

class Qualis():
    def __init__(self, qualis_path: str):
        self.qualis_dict = self._readQualisDict(qualis_path)

    def _readQualisDict(self, fileName):

        df = pd.read_csv(fileName)
        df.set_index('ISSN', inplace = True)

        return df['Estrato'].to_dict()
        
    def get_estrato(self, issn: str):
        """
        Retorna o estrato referente ao issn caso exista e None se o issn não for encontrado.

        Reconhece ISSN nos padrões xxxxxxxx ou xxxx-xxxx.
        """
        if len(issn) < 8:
            return None
        # Verifica se o issn está no padrão xxxxxxxx
        if issn[4] != "-":
            # Transforma o issn para o padrão xxxx-xxxx
            issn = issn[:4] + "-" + issn[4:]
        
        if issn in self.qualis_dict:
            return self.qualis_dict[issn]
        else:
            return None