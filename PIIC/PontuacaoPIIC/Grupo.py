from PontuacaoPIIC.Item import Item

class Grupo():
    def __init__(self, limite: float, itens: list[Item]):
        self._limite = limite
        self._pontuacao = 0
        self._itens = itens
    
    def get_limite(self):
        return self._limite
    
    def get_pontuacao(self):
        return self._pontuacao
    
    def get_itens(self):
        return self._itens
        
    def insere_item(self, item: Item):
        self._itens.append(item)

    def calcula_nota(self):
        """
        Calcula a pontuação do grupo e retorna o valor obtido.
        """
        for item in self.get_itens():
            self._pontuacao += item.get_valor_item() * item.get_quantidade_total()
            if self.get_pontuacao() >= self.get_limite():
                self._pontuacao = self.get_limite()
                break
            
        return self.get_pontuacao()


    def __str__(self):
        r = "Pontuação: " + str(self.get_pontuacao()) + "\n"
        for a in self.get_itens():
            r += str(a) + "\n"
        return r