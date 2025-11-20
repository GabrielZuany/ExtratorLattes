import sys
import json
import os
import pandas as pd

def dfQualisToDict(dfQualis):
    #dfQualis.set_index('ISSN', inplace = True)

    return dfQualis['Estrato'].to_dict()

def dfISSNToDict(dataframe):

    #Cria um dicionário com a chave Print ISSN e valor EISSN
    d1 = dataframe.set_index('Print-ISSN')['E-ISSN'].to_dict()
    #Cria um dicionário com a chave EISSN e valor Print ISSN
    d2 = dataframe.set_index('E-ISSN')['Print-ISSN'].to_dict()
    
    return d1, d2

def qualisDict(dictQualis, dfISSN):
    pIssn, eIssn = dfISSNToDict(dfISSN)

    for key in list(dictQualis.keys()):
        if key in pIssn:
            value = pIssn[key]
            if not value in dictQualis:
                dictQualis[value] = dictQualis[key]
        elif key in eIssn:
            value = eIssn[key]
            if not value in dictQualis:
                dictQualis[value] = dictQualis[key]
    
    return dictQualis

def jsonToDataFrame(dirPath):

    jsonFiles = [os.path.join(dirPath, x) for x in os.listdir(dirPath) if x.endswith('.json')]
    
    data = []
    
    for path in jsonFiles:
        with open(path) as f:
            data += json.load(f)
    
    dfJson = pd.DataFrame(data=data)
    
    dfJson = dfJson[['issn', 'e-issn']].map(lambda x: None if x == '' else x)
    
    dfJson.dropna(inplace=True)
    
    # Corrigindo anomalias nos issns como no issn: 0370-629X do json part-1
    dfJson = dfJson.map(lambda x: x[:9] if len(x) > 9 else x)
    
    dfJson.columns = ['Print-ISSN', 'E-ISSN']
    
    return dfJson
    

if __name__ == '__main__':
    fileName = sys.argv[1]
    
    dfQualis = pd.read_csv(fileName)

    dfQualis = dfQualis.drop('Área de Avaliação', axis = 'columns')
    dfQualis = dfQualis.drop('Título', axis = 'columns')

    dfQualis = dfQualis.groupby('ISSN').min()

    #Tratando o arquivo issn_list_xlsx
    dfISSN = pd.read_csv('issn_list_xlsx.csv')
    #Cria um dataframe apenas com as colunas Print ISSN e EISSN
    dfISSN = dfISSN[['Print-ISSN','E-ISSN']]
    
    #Elimina todas as linhas que possuem algum valor em uma das colunas vazio
    # e altera o issn de XXXXXXXX para XXXX-XXXX, caso necessário
    dfISSN = dfISSN.dropna().map(lambda x: str(x)[:4] + '-' + str(x)[4:] if not str(x)[4] == '-' else x)

    #Tratando o arquivo ImpactFactor
    dfFactor = pd.read_csv('ImpactFactor2024.csv', sep=';')

    dfFactor = dfFactor[['ISSN','EISSN']]
    dfFactor.columns = ['Print-ISSN','E-ISSN']

    dfFactor.dropna(inplace=True)

    # Faz a associação dos issn que tem no Qualis com os issn que tem no arquivo xlsx
    data = qualisDict(dfQualisToDict(dfQualis), dfISSN)
    
    # Faz a associação dos issn que tem no Qualis com os issn que tem nos arquivos json
    dataJson = qualisDict(dfQualisToDict(dfQualis), jsonToDataFrame('ISSNJson'))

    # Faz a associação dos issn que tem no Qualis com os issn que tem no arquivo ImpactFactor
    dataFactor = qualisDict(dfQualisToDict(dfQualis), dfFactor)

    # Une as duas bases
    data.update(dataJson)

    data.update(dataFactor)
    
    c1 = list(data.keys())
    c2 = [data[key] for key in c1]
    
    df = pd.DataFrame(data = {'ISSN': c1, 'Estrato': c2})
    
    df.set_index('ISSN', inplace=True)

    df.to_csv('qualis-unificado.csv', header = True, index = True)