from enum import Enum, auto

# Configurado no __init__.py para uma importação mais limpa
class TipoNotaPIIC(Enum):
    PADRAO = auto()
    MAE_PESQUISADORA = auto()
    RECEM_DOUTOR = auto()