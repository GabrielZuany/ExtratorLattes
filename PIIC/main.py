import sys
import os       

# Adiciona o diretório pai aos caminhos de importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PontuacaoPIIC.Orientador import Orientador, MaePesquisadora
import PontuacaoPIIC.Output as opiic
import PontuacaoPIIC.utils as upiic
from tqdm import tqdm
import argparse
import csv
import os

if __name__ == "__main__":
    #Flag para impressao da saida atualizada
    parser = argparse.ArgumentParser(description="Saida atualizada")
    parser.add_argument('-n', action='store_true', help="Ativa a saida nova")
    parser.add_argument('config', type=argparse.FileType('r'), help="Arquivo de configuração")

    args = parser.parse_args()
    
    # Carregando a configuração
    config = upiic.configura_by_json(args.config.name)
    
    ano_fim = config["ano_fim"]
    ano_inicio = config["ano_inicio"]
    tabela_json = config["tabela_de_configuracao"]
    arquivo_qualis = config["arquivo_qualis"]
    arquivo_maes = config["arquivo_maes_pesquisadoras"]
    diretorio_resultados = config["diretorio_resultados"]
    diretorio_curriculo = config["diretorio_dos_curriculos"]

    maes = upiic.read_maes_pesquisadoras(arquivo_maes)
    
    orientadores = {}

    results_csv_file = open(os.path.join(diretorio_resultados, "resultados.csv"), "w")

    with open(config["arquivo_orientadores"]) as f:
        lines_qtd = sum(1 for _ in csv.reader(f, delimiter=";")) - 1

    print()
    with open(config["arquivo_orientadores"]) as f:
        r = csv.reader(f, delimiter=";")
        next(r)
        tq = tqdm(r, desc='Progresso', total = lines_qtd, unit='curriculo')
        for row in tq:
            cpf = upiic.reformatar_CPF(row[0])
            area = row[1]

            tq.set_description_str(f"Processando {cpf}")

            curriculo_path = os.path.join(diretorio_curriculo, cpf + ".xml")

            try:
                if cpf not in maes:
                    orientador = Orientador(cpf, curriculo_path, ano_inicio, ano_fim)
                else:
                    orientador = MaePesquisadora(cpf, curriculo_path, maes[cpf]['anos'], ano_inicio, ano_fim)
            except Exception as e:
                tq.write(f"Erro ao processar o currículo {curriculo_path}: verifique se o xml é válido.\n")
                continue
            
            orientador.add_submissao(area, ano_inicio, ano_fim, tabela_json, arquivo_qualis)
            
            # Verifica se o orientador ja teve alguma submissao, se tiver, adiciona o numero 
            # da submissao no nome do arquivo de saida
            name_suffix = ''
            if orientador.get_cpf() in orientadores:
                orientadores[orientador.get_cpf()] += 1
                name_suffix = '_' + str(orientadores[orientador.get_cpf()])
            else:
                orientadores[orientador.get_cpf()] = 1

            sub = orientador.get_submissoes()[0]

            html_p = os.path.join(diretorio_resultados, cpf + name_suffix + ".html")
            with open(html_p, "w") as f:
                opiic.write_html(sub, f)
            
            text_p = os.path.join(diretorio_resultados, cpf + name_suffix + ".txt")
            with open(text_p, "w") as f:
                opiic.write_text(sub, f)
            
            if args.n:
                opiic.write_csv_line_short(sub, sep = ";", file = results_csv_file)
            else:
                opiic.write_csv_line(sub, sep = ";", file = results_csv_file)
    
    print()
    results_csv_file.close()