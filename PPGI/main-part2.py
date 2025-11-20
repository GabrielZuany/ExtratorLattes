import os
import sys

# Adiciona o diretório pai aos caminhos de importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from PontuacaoPPGI.NotaInfo import NotaInfo
from PontuacaoPPGI.Pontuacao import Pontuacao
import PontuacaoPPGI.PontuacaoTotal as PontuacaoTotal
import PontuacaoPPGI.utils as ppgiu

def get_nome_prefix(nome, ppgi_config):
    return str(ppgi_config['ano_fim_conferencia']) + '_' + nome

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Arquivo de configuração")
    parser.add_argument('config', type=argparse.FileType('r'), help="Arquivo de configuração")

    args = parser.parse_args()
    
    ppgi_config = ppgiu.config_json(args.config.name)
    
    docentes = ppgiu.docentes_by_csv(ppgi_config['rec_in'])

    pontuacoes = []

    nota_info = NotaInfo(ppgi_config['nota_info'])
    file = ppgiu.create_csv_writer(os.path.join(ppgi_config["dir_out"], get_nome_prefix(ppgi_config['docente_file'], ppgi_config)), nota_info)
    for docente in docentes:
        pontuacao = Pontuacao(docente, nota_info)
        pontuacao.processa_pontuacao()
        
        print("-"*40)
        print(docente.get_nome())
        print(pontuacao.tabela.get_data_frame().T)
        
        print()
        print(pontuacao.tabela.get_prod_min())
        pontuacao.calcula_nota()
        pontuacao.write_csv_line(sep=';', file=file)
        print("Nota:", pontuacao.nota)
    print("-"*40)
    
    file.close()

    try:
        arquivo_geral = os.path.join(ppgi_config['dir_out'], get_nome_prefix(ppgi_config['geral_file'], ppgi_config))
        PontuacaoTotal.calcula_nota_geral(docentes, nota_info, arquivo_geral)
    except ValueError as e:
        print(e)
        print(f"Corrija os erros e execute novamente. Arquivo de saída '{arquivo_geral}' não foi gerado.")