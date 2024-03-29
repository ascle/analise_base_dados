import matplotlib

matplotlib.use('Agg')

from django.shortcuts import render
from django.http import HttpResponseServerError
import base_dados.services as service
import traceback
import sys
import time
import numpy as np
from pandas.api.types import is_numeric_dtype


def listar_bases(request):
    return render(request, 'base_dados/listarBasesDados.html', {"lista_bases": service.get_lista_bases()})


def ver_base_dados(request, base_dados):
    try:
        dados = service.get_base_dados(base_dados)
        info = service.info_base_dados(dados)
        dicionario = service.info_colunas_base(dados)

        # Ação
        dicionario['ddd'] = dicionario.index

        select = "<select id='id_sel_{}'>" \
                 "<option value='1'>CATEGÓRICO NOMINAL</option>" \
                 "<option value='2'>CATEGÓRICO ORDINAL</option>" \
                 "</select>"
        dicionario['Tipo de variável'] = dicionario.apply(
            lambda row: select.format(row.ddd) if row['Tipo de variável'] is None else row['Tipo de variável'],
            axis=1
        )

        dicionario['Ação'] = dicionario.apply(
            lambda row: "<a href='/verColunaDaBaseDeDados/{}/{}'>Explorar</a>".format(
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
        t_ini = 0
        t_fim = 0
        t_total = 0
        data_is_numeric = is_numeric_dtype(data_frame[nome_variavel])
        choices = {'nome_variavel': nome_variavel,
                   'url_base': url_base}

        # ................ INFORMAÇÕES ................

        # Tabela de frequencia
        tabela_quantidade = None
        time_exec_tabela_quantidade = None
        t_ini = time.time()
        try:
            tabela_quantidade = service.info_coluna_quantidade(data_frame, nome_variavel) \
                .to_html(render_links=True, escape=False, )
            choices['tabela_quantidade'] = tabela_quantidade
        except Exception as e:
            mensagem_erro.append('Tabela de frequência: ' + str(e))
        t_fim = time.time()
        time_exec_tabela_quantidade = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_tabela_quantidade

        # Tabela do describe
        tabela_describe = None
        time_exec_tabela_describe = None
        t_ini = time.time()
        try:
            tabela_describe = service.info_coluna_describe(data_frame, nome_variavel).to_html(
                render_links=True,
                escape=False, )
            choices['tabela_describe'] = tabela_describe
        except Exception as e:
            mensagem_erro.append('Estatística descritiva: ' + str(e))
        t_fim = time.time()
        time_exec_tabela_describe = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_tabela_describe

        # Informações descritivas
        # descritiva = service.info_coluna_descritiva(data_frame, nome_variavel, 'OBT_NEONATAL').to_html(
        #    render_links=True,
        #    escape=False,)

        # Teste de normalidade
        is_normal = None
        time_exec_is_normal = None
        t_ini = time.time()
        try:
            if data_is_numeric:
                is_normal = service.test_normalidade(data_frame, nome_variavel)
                verdade_ou_falso = 'Verdadeiro' if is_normal else 'Falso'
                test_normalidade = test_normalidade.format(nome_variavel, verdade_ou_falso)
                choices['test_normal'] = test_normalidade
            else:
                raise ValueError('Funcionalidade implementada somente para tipos numéricos')
        except Exception as e:
            mensagem_erro.append('Teste de normalidade: ' + str(e))
        t_fim = time.time()
        time_exec_is_normal = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_is_normal

        # Intervalo Z de confiança
        intervalo = None
        time_exec_intervalo = None
        t_ini = time.time()
        try:
            if data_is_numeric:
                intervalo = service.info_inter_conf(data_frame, nome_variavel).to_html(
                    render_links=True,
                    escape=False, )
                choices['inter_conf'] = intervalo
            else:
                raise ValueError('Funcionalidade implementada somente para tipos numéricos')
        except Exception as e:
            mensagem_erro.append('Intervalo de confiança (Z): ' + str(e))
        t_fim = time.time()
        time_exec_intervalo = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_intervalo

        # ................ GRÁFICOS ................

        # Gráfico de frequencia
        time_exec_img_freq = None
        t_ini = time.time()
        img_freq = service.graf_diag_freq(data_frame, nome_variavel)
        choices['img_freq'] = img_freq
        t_fim = time.time()
        time_exec_img_freq = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_img_freq

        # Gráfico do BoxPlot
        img_boxplot = None
        time_exec_img_boxplot = None
        t_ini = time.time()
        try:
            if data_is_numeric:
                img_boxplot = service.graf_boxplot(data_frame, nome_variavel)
                choices['img_boxplot'] = img_boxplot
            else:
                raise ValueError('Funcionalidade implementada somente para tipos numéricos')
        except Exception as e:
            mensagem_erro.append('Boxplot: ' + str(e))
        t_fim = time.time()
        time_exec_img_boxplot = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_img_boxplot

        # Gráfico do histograma
        img_hist = None
        time_exec_img_hist = None
        t_ini = time.time()
        try:
            img_hist = service.graf_histograma(data_frame, nome_variavel)
            choices['img_hist'] = img_hist
        except Exception as e:
            mensagem_erro.append('Histograma: ' + str(e))
        t_fim = time.time()
        time_exec_img_hist = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_img_hist

        # Gráfico de Frequencia Acumulada
        img_freq_acu = None
        time_exec_img_freq_acu = None
        t_ini = time.time()
        try:
            if data_is_numeric:
                img_freq_acu = service.graf_freq_acumulada(data_frame, nome_variavel)
                choices['img_freq_acu'] = img_freq_acu
            else:
                raise ValueError('Funcionalidade implementada somente para tipos numéricos')
        except Exception as e:
            mensagem_erro.append('Frequência Acumulada: ' + str(e))
        t_fim = time.time()
        time_exec_img_freq_acu = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_img_freq_acu

        # Gráfico das médias
        img_medias = None
        ime_exec_img_medias = None
        t_ini = time.time()
#        try:
#            if data_is_numeric:
#                #img_medias = service.graf_media(data_frame, nome_variavel)
#            #else:
#            #   raise ValueError('Funcionalidade implementada somente para tipos numéricos')
#        except Exception as e:
#            mensagem_erro.append('Distribuição das Médias: ' + str(e))
        t_fim = time.time()
        time_exec_img_medias = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_img_medias


        # Gráfico Boxplot da variável dependente
        img_boxplot_denpendente = None
        time_exec_boxplot = None
        t_ini = time.time()
        try:
            img_boxplot_denpendente = service.graf_boxplot_var_denpendente(data_frame, nome_variavel)
            choices['img_boxplot_denpendente'] = img_boxplot_denpendente
        except Exception as e:
            mensagem_erro.append('Boxplot da variável dependente: ' + str(e))
        t_fim = time.time()
        time_exec_boxplot = np.float64(t_fim - t_ini).round(4)
        t_total = t_total + time_exec_boxplot



        # ................ PARÂMETROS ................

        choices['time_exec_tabela_quantidade'] = time_exec_tabela_quantidade
        choices['time_exec_tabela_describe'] = time_exec_intervalo
        choices['time_exec_intervalo'] = time_exec_intervalo
        choices['time_exec_img_freq'] = time_exec_img_freq
        choices['time_exec_img_boxplot'] = time_exec_img_boxplot
        choices['time_exec_img_hist'] = time_exec_img_hist
        choices['time_exec_img_freq_acu'] = time_exec_img_freq_acu
        choices['time_exec_img_medias'] = time_exec_img_medias
        choices['time_exec_is_normal'] = time_exec_is_normal
        choices['time_exec_boxplot'] = time_exec_boxplot
        choices['t_total'] = t_total
        choices['mensagem_erro'] = mensagem_erro

        return render(request, 'base_dados/verColunaDaBaseDeDados.html', {"view": choices})
    except:
        traceback.print_exception(*sys.exc_info())
        return HttpResponseServerError()
