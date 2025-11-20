import pandas as pd
import json

def configura_by_json(config_path: str):
    with open(config_path) as f:
        configuracao = json.load(f)

        print("Carregando arquivo de configuração:")
        print()

        # Verificando ano inicio
        if not "ano_inicio" in configuracao:
            raise KeyError("ano_inicio não foi especificado!")
        print("ano_inicio - OK!")

        # Verificando ano fim
        if not "ano_fim" in configuracao:
            raise KeyError("ano_fim não foi especificado!")
        print("ano_fim - OK!")

        # Verificando diretorio de resultados
        if not "diretorio_resultados" in configuracao:
            raise KeyError("diretorio_resultados não foi especificado!")
        print("diretorio_resultados - OK!")

        # Verificando arquivo de orientadores
        if not "arquivo_orientadores" in configuracao:
            raise KeyError("arquivo_orientadores não foi especificado!")
        print("arquivo_orientadores - OK!")

        # Verificando arquivo mae-pesquisadoras
        if not "arquivo_maes_pesquisadoras" in configuracao:
            raise KeyError("arquivo_maes_pesquisadoras não foi especificado!")
        print("arquivo_maes_pesquisadoras - OK!")

        # Verificando diretorio dos curriculos
        if not "diretorio_dos_curriculos" in configuracao:
            raise KeyError("diretorio_dos_curriculos não foi especificado!")
        print("diretorio_dos_curriculos - OK!")

        # Verificando arquivo tabela de configuracao
        if not "tabela_de_configuracao" in configuracao:
            raise KeyError("tabela_de_configuracao não foi especificado!")
        print("tabela_de_configuracao - OK!")
        
        # Verificando arquivo qualis
        if not "arquivo_qualis" in configuracao:
            raise KeyError("arquivo_qualis não foi especificado!")
        print("arquivo_qualis - OK!")
        
        print()
        print("Arquivo de configuração carregado com sucesso.")

    return configuracao

def read_maes_pesquisadoras(arquivo_path: str):
    df = pd.read_csv(arquivo_path)
    df.set_index('cpf', inplace = True)
    df.index = df.index.map(reformatar_CPF)
    return df.to_dict('index')

def reformatar_CPF(cpf):
    if type(cpf) != str:
        cpf = str(cpf)
    novo = cpf.zfill(11)
    return novo
