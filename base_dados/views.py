from django.shortcuts import render
import base_dados.services as service
from django.http import HttpResponseServerError
from base_dados.services import info_colunas_base
import traceback


def listar_bases(request):
    return render(request, 'base_dados/listarBasesDados.html', {"lista_bases": service.get_lista_bases()})


def ver_base_dados(request, base_dados):
    try:
        dados = service.get_base_dados(base_dados)
        info = service.info_base_dados(dados)
        dicionario = service.info_colunas_base(dados)

        # Ação
        dicionario['ddd'] = dicionario.index
        dicionario['Ação'] = dicionario.apply(
            lambda row: "<a href='/verColunaDaBaseDeDados/{}/{}'>Ver</a>".format(
                row.ddd,
                base_dados.replace('\\', '%5C')),
            axis=1
        )
        dicionario.drop(columns=['ddd'], inplace=True)

        info_colunas = dicionario.to_html(render_links=True, escape=False, )
        choices = {'url': base_dados,
                   'info': info,
                   'info_colunas': info_colunas}
        return render(request, 'base_dados/verBaseDados.html', {"base_dados": choices})
    except:
        traceback.print_stack()
        return HttpResponseServerError()


def ver_coluna(request, nome_variavel, url_base):
    try:
        choices = {'nome_variavel': nome_variavel,
                   'url_base': url_base,
                   'tabela_quantidade': service.info_coluna_quantidade(url_base, nome_variavel).to_html(render_links=True, escape=False, )
                   }
        return render(request, 'base_dados/verColunaDaBaseDeDados.html', {"view": choices})
    except:
        traceback.print_stack()
        return HttpResponseServerError()
