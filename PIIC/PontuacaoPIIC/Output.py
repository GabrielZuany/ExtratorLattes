from PontuacaoPIIC.Submissao import Submissao
import textwrap
import sys
    
def write_html(submissao: Submissao, file = sys.stdout):
    cpf = submissao.get_orientador().get_cpf()
    nome = submissao.get_orientador().get_nome()
    f = file

    print('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">',file=f)
    print("<html>",file=f)
    _print_html_tag("meta","",attr="charset=utf-8",file=f)
    print('<head>',file=f)
    _print_html_tag("title",cpf,file=f)
    print("</head><body>",file=f)
    _print_html_tag("H1",nome,file=f)
    _write_html_table(submissao, file=f)
    print("<br /",file=f)
    print("</body></html>",file=f)
    
def write_text(submissao: Submissao, file=sys.stdout):
    tabela = submissao.get_pontuacao().get_tabela()
    id_grupo = 0
    i = 0

    print(submissao.get_orientador().get_nome(), file = file)
    print("",file = file)
    
    for grupo in tabela.get_grupos():
        for item in grupo.get_itens():
            q = item.get_quantidade_total()
            v = grupo.get_pontuacao()
            l = grupo.get_limite()
            u = item.get_valor_item()
            d = item.get_descricao()
            # Preparar para o campo descriçaõ precisar de multiplas
            # linhas
            dlinhas = textwrap.wrap(d, 55)
            # Valor e limite so impressos no ultimo item do grupo
            if i < id_grupo:
                print("%2d %-55s %-3s %3d %3d"%(i+1,dlinhas[0],"",u,q),
                    file=file)
            else:
                print("%2d %-55s %3d %3d %3d %3d"%(i+1,dlinhas[0],l,u,q,v),
                    file=file)
            if len(dlinhas) > 1:
                for j in range(1,len(dlinhas)):
                    print("   %-55s"%dlinhas[j],file=file)
            i += 1
        id_grupo += 1

    somapontos = submissao.get_pontuacao().get_pontuacao_total()
    print("%-70s %3d"%("SOMA",somapontos),file=file)

def write_csv_line(submissao: Submissao, sep: str = ';', file = sys.stdout):
    tabela = submissao.get_pontuacao().get_tabela()

    s = f"{submissao.get_orientador().get_cpf()},{submissao.get_pontuacao().get_qtd_anos()},{submissao.get_orientador().get_nome()},"
    for grupo in tabela.get_grupos():
        for item in grupo.get_itens():
            q = item.get_quantidade_total()
            s += sep
            s += str(q)
    s += sep
    s += "|"
    for grupo in tabela.get_grupos():
        qtd_itens = len(grupo.get_itens())
        for item in grupo.get_itens():
            v = grupo.get_pontuacao()
            s += sep
            qtd_itens -= 1
            if qtd_itens == 0:
                s += str(v)

    somapontos = submissao.get_pontuacao().get_pontuacao_total()
    s += sep
    s += str(somapontos)
    media = submissao.get_pontuacao().get_media()
    s += sep
    s += "%.2f"%media
    
    print(s,file=file)

    return s

def write_csv_line_short(submissao: Submissao, sep: str = ';', file = sys.stdout):
    """
        Escreve uma linha no arquivo passado em 'file', com as informações do 
        orientador, a quantidade de cada item, os valores obtidos em cada grupo, 
        pontuação total e média do orientador.
        Formatação da linha:\n
        cpf;quantidade de anos;nome;tipo da pontuação;quantidade para cada item;pontuação para cada grupo;total;média
    """
    tabela = submissao.get_pontuacao().get_tabela()

    s = f"{submissao.get_orientador().get_cpf()};{submissao.get_pontuacao().get_qtd_anos()};{submissao.get_orientador().get_nome()};{submissao.get_pontuacao().get_tipo_nota().name}"
    for grupo in tabela.get_grupos():
        for item in grupo.get_itens():
            q = item.get_quantidade_total()
            s += sep
            s += str(q)
    s += sep
    s += "|"
    for grupo in tabela.get_grupos():
        v = grupo.get_pontuacao()
        s += sep
        s += str(v)

    somapontos = submissao.get_pontuacao().get_pontuacao_total()
    s += sep
    s += str(somapontos)
    media = submissao.get_pontuacao().get_media()
    s += sep
    s += "%.2f"%media
    
    print(s,file=file)

    return s

def _write_html_table(submissao: Submissao, file = sys.stdout):
    f = file

    anos = submissao.get_pontuacao().get_qtd_anos()

    print('<table border="1px">',file = f)
    print('<tr>',file=f)
    _print_html_tag("th","N",file=f)
    _print_html_tag("th","Descricao",file=f)
    _print_html_tag("th","Limite<br />Grupo",file=f)
    _print_html_tag("th","Valor<br />Unitário",file=f)
    _print_html_tag("th","Qte",file=file)
    _print_html_tag("th","Pontos",file=file)
    print('</tr>',file=f)

    tabela = submissao.get_pontuacao().get_tabela()
    idc_item = 1
    
    for grupo in tabela.get_grupos():
        rowspan = len(grupo.get_itens())
        for item in grupo.get_itens():
            q = item.get_quantidade_total()
            v = grupo.get_pontuacao()
            l = grupo.get_limite()
            u = item.get_valor_item()
            d = item.get_descricao()

            print('<tr>',file=f)
            # Item
            _print_html_tag("td",str(idc_item),file=f)
            # Descricao
            _print_html_tag("td",d,"text-align:left",file=f)
            # Limite do grupo
            if rowspan > 1:
                _print_html_tag('td rowspan="%1d"'%rowspan,l,file=f)
            elif rowspan == 1:
                _print_html_tag("td",l,file=f)
            # Unitario
            _print_html_tag("td",u,file=f)
            # Quantidade
            _print_html_tag("td",q,file=f)
            # Pontos
            if rowspan > 1:
                # v = submissao.get_valor[indicegrupo[i]]
                _print_html_tag('td rowspan="%1d"'%rowspan,v,file=f)
            elif rowspan == 1:
                _print_html_tag("td",v,file=f)
            print('</tr>',file=f)

            rowspan = 0
            idc_item += 1
        print('<tr>',file=f)

    somapontos = submissao.get_pontuacao().get_pontuacao_total()
    _print_html_tag("td","",file=f)
    _print_html_tag("td","TOTAL",file=f)
    _print_html_tag("td","",file=f)
    _print_html_tag("td","",file=f)
    _print_html_tag("td","",file=f)
    _print_html_tag("td",str(somapontos),file=f)
    print('<tr>',file=file)
    _print_html_tag("td","",file=f)
    _print_html_tag("td","MEDIA",file=f)
    _print_html_tag("td","",file=f)
    _print_html_tag("td","",file=f)
    _print_html_tag("td","",file=f)
    s = "%.2f" % (somapontos/float(anos)) 
    _print_html_tag("td",s,file=f)
    print('</tr>',file=f)
    print('</table>',file=f)

def _print_html_tag(tag, value, style = "",attr = "",file = sys.stdout):
    if not style:
        print('<%s %s>%s</%s>'%(tag,attr,value,tag),file=file)
    else:
        print('<%s %s style="%s;">%s</%s>'%(tag,attr,style,value,tag),file=file)