class Item():

    def __init__(self, descricao: str, valor_item: int):
        self._descricao = descricao
        self._valor_item = valor_item
        self._quantidade_total = 0

    def get_descricao(self):
        return self._descricao

    def get_valor_item(self):
        return self._valor_item
    
    def get_quantidade_total(self):
        return self._quantidade_total
        
    def add_quantidade(self, qtd: int):
        self._quantidade_total += qtd
        
    def __str__(self):
        return "Descricao: " + self.get_descricao() + " | Valor: " + str(self.get_valor_item()) + " | Quantidade: " + str(self.get_quantidade_total())