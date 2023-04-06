from django.shortcuts import render
import base_dados.services as service
from base_dados.services import info_colunas_base


def listar_bases(request):
    return render(request, 'base_dados/listarBasesDados.html', {"lista_bases": service.get_lista_bases()})


def ver_base_dados(request, base_dados):
    try:
        dados = service.get_base_dados(base_dados)
        info = service.info_base_dados(dados)
        info_colunas = service.info_colunas_base(dados).to_html()
    except Exception as e:
        print(e)

    choices = {'url': base_dados,
               'info': info,
               'info_colunas': info_colunas}
    return render(request, 'base_dados/verBaseDados.html', {"base_dados": choices})
