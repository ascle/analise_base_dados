import base64
import io
import urllib
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render
import base_dados.services as service
from django.http import HttpResponseServerError
from base_dados.services import info_colunas_base
import traceback
import sys


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
        traceback.print_exc()
        return HttpResponseServerError()


def ver_coluna(request, nome_variavel, url_base):
    try:

        # ................ VARIÁVEIS ................

        mensagem_erro = []
        test_normalidade = "A variável '{}' é proveniente de uma distribuição normal? {}"
        data_frame = service.get_base_dados(url_base)


        # ................ INFORMAÇÕES ................

        # Tabela de frequencia
        tabela_quantidade = service.info_coluna_quantidade(data_frame, nome_variavel).to_html(
            render_links=True,
            escape=False,)

        # Tabela do describe
        tabela_describe = service.info_coluna_describe(data_frame, nome_variavel).to_html(
            render_links=True,
            escape=False,)

        # Informações descritivas
        # descritiva = service.info_coluna_descritiva(data_frame, nome_variavel, 'OBT_NEONATAL').to_html(render_links=True,escape=False,)

        # Teste de normalidade
        is_normal = service.test_normalidade(data_frame, nome_variavel)
        verdade_ou_falso = 'Verdadeiro' if is_normal else 'Falso'
        test_normalidade = test_normalidade.format(nome_variavel, verdade_ou_falso)

        # Intervalo Z de confiança
        intervalo = service.info_inter_conf(data_frame, nome_variavel).to_html(
            render_links=True,
            escape=False,)

        # ................ GRÁFICOS ................

        # Gráfico de frequencia
        img_freq = service.graf_diag_freq(data_frame, nome_variavel)

        # Gráfico do BoxPlot
        img_boxplot = None
        try:
            img_boxplot = service.graf_boxplot(data_frame, nome_variavel)
        except Exception as e:
            mensagem_erro.append('Boxplot: '+str(e))

        # Gráfico do histograma
        img_hist = None
        try:
            img_hist = service.graf_histograma(data_frame, nome_variavel)
        except Exception as e:
            mensagem_erro.append('Histograma: '+str(e))

        # Gráfico de Frequencia Acumulada
        img_freq_acu = None
        try:
            img_freq_acu = service.graf_freq_acumulada(data_frame, nome_variavel)
        except Exception as e:
            mensagem_erro.append('Frequência Acumulada: '+str(e))

        # Gráfico das médias
        img_medias = None
        try:
            img_medias = service.graf_media(data_frame, nome_variavel)
        except Exception as e:
            mensagem_erro.append('Distribuição das Médias: ' + str(e))

        # ................ PARÂMETROS ................

        choices = {'nome_variavel': nome_variavel,
                   'url_base': url_base,
                   'tabela_quantidade': tabela_quantidade,
                   'tabela_describe': tabela_describe,
                   'inter_conf':intervalo,
                   #'descritiva': descritiva
                   'img_freq': img_freq,
                   'img_boxplot': img_boxplot,
                   'img_hist': img_hist,
                   'mensagem_erro': mensagem_erro,
                   'img_freq_acu': img_freq_acu,
                   'img_medias': img_medias,
                   'test_normal': test_normalidade,
                   }
        return render(request, 'base_dados/verColunaDaBaseDeDados.html', {"view": choices})
    except:
        traceback.print_exception(*sys.exc_info())
        return HttpResponseServerError()


