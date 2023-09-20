import base64
import io
import os
import urllib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.contrib.staticfiles.utils import get_files
from pandas.api.types import is_numeric_dtype
from scipy.stats import normaltest
from statsmodels.stats.weightstats import zconfint

from setup.settings import STATIC_ROOT


def get_lista_bases():
    try:
        url_bases = StaticFilesStorage()
        bases_list = list(get_files(url_bases, location='bases'))
        return bases_list
    except Exception as e:
        raise e


def get_base_dados(url):
    try:
        url = os.path.join(STATIC_ROOT, url)
        dados = pd.read_csv(url, sep=';', low_memory=False)
        dados.sort_index(axis=1, inplace=True)
        return dados
    except Exception as e:
        raise e


def info_base_dados(dados):
    try:
        return 'A base de dados apresenta {} registros  e {} variáveis'.format(dados.shape[0], dados.shape[1])
    except Exception as e:
        raise e


def info_colunas_base(dados):
    try:
        tipos_de_dados = pd.DataFrame(dados.dtypes, columns=['Tipos de dados'])
        tipos_de_dados.columns.name = 'Variáveis'

        # Possui Nan
        tipos_de_dados['ddd'] = tipos_de_dados.index
        tipos_de_dados['Possui Nan'] = tipos_de_dados.apply(
            lambda row: 'Sim' if dados[row.ddd].isnull().values.any() else 'Não', axis=1)

        # Intervalo de Valores
        tipos_de_dados['Intervalo de Valores'] = tipos_de_dados.apply(
            lambda row: sorted(dados[row.ddd].unique()) if is_numeric_dtype(dados[row.ddd].dtype) else dados[
                row.ddd].unique(), axis=1)

        # Tipo de Variável
        tipos_de_dados['Tipo de variável'] = tipos_de_dados.apply(
            lambda row: None if row['Tipos de dados'] == 'object' else 'Numérico',
            axis=1
        )



        tipos_de_dados.drop(columns=['ddd'], inplace=True)

        return tipos_de_dados
    except Exception as e:
        raise e


def info_coluna_quantidade(data_frame, nome_variavel):
    try:
        freq = data_frame[nome_variavel].value_counts(dropna=False)
        porc = (data_frame[nome_variavel].value_counts(dropna=False, normalize=True) * 100).round(2)
        dis_freq_quantitativas_personalizadas = pd.DataFrame({'Frequência': freq, 'Porcentagem (%)': porc})
        return dis_freq_quantitativas_personalizadas
    except Exception as e:
        raise e

def info_coluna_describe(data_frame, nome_variavel):
    try:
        describe = pd.DataFrame(data_frame[nome_variavel].describe())
        return describe
    except Exception as e:
        raise e

def info_inter_conf(data_frame, nome_variavel):
    try:
        serie = data_frame[nome_variavel].dropna()
        intervalo = pd.DataFrame([zconfint(serie)], columns=['Min', 'Max'])
        return intervalo
    except Exception as e:
        raise e

# Usar quando tiver um target do tipo Valor
def info_coluna_descritiva(data_frame, agrupamento, target):
    try:
        agrupamento = data_frame.groupby(agrupamento)
        descritiva = pd.DataFrame(agrupamento[target].describe().round(2))
        return descritiva
    except Exception as e:
        raise e


def iniciar_grafico():
    plt.clf()
    # plt.rc('figure', figsize=(15, 8))
    # fig = plt.gcf()
    # ax = fig.gca()
    sns.set_style("darkgrid")
    sns.set(rc={'figure.figsize': (15, 8)})


def finalizar_grafico(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri

def graf_diag_freq(data_frame, nome_variavel):
    try:
        iniciar_grafico()

        # Dados categoricos
        if data_frame[nome_variavel].dtype == 'object':
            porc = (data_frame[nome_variavel].value_counts()).round(2)
            dados = pd.DataFrame({'Frequência': porc}).sort_values('Frequência')
            ax = sns.barplot(dados.transpose())
            plt.xticks(rotation=45, ha='right');
            ax.set(title='Distribuição por frequência', xlabel=nome_variavel, ylabel='Frequência')
        else:
            # data_frame[nome_variavel].value_counts(dropna=False).plot.bar(ax=ax)
            ax = sns.histplot(data_frame[nome_variavel], discrete=True)
            ax.set(title='Distribuição por frequência', xlabel=nome_variavel, ylabel='Frequência')

        return finalizar_grafico(ax.get_figure())
    except ValueError as e:
        raise e
    except Exception as e:
        raise e


def graf_histograma(data_frame, nome_variavel):
    try:
        iniciar_grafico()

        # Dados categoricos
        if data_frame[nome_variavel].dtype == 'object':
            porc = (data_frame[nome_variavel].value_counts(normalize=True)).round(2)
            dados = pd.DataFrame({'Densidade': porc}).sort_values('Densidade')
            ax = sns.barplot(dados.transpose())
            plt.xticks(rotation=45, ha='right');
            ax.set(title='Distribuição por densidade', xlabel=nome_variavel, ylabel='Densidade')
        else:
            ax = sns.distplot(data_frame[nome_variavel], hist=False, kde_kws={'bw': 0.5})
            ax = sns.histplot(data_frame[nome_variavel], stat='density', discrete=True)
            ax.set(title='Histograma', xlabel=nome_variavel, ylabel='Densidade')

        return finalizar_grafico(ax.get_figure())
    except ValueError as e:
        raise e
    except Exception as e:
        raise e


def graf_boxplot(data_frame, nome_variavel):
    try:
        iniciar_grafico()

        ax = sns.boxplot(data=data_frame[nome_variavel], orient='h', medianprops={"color": "coral"})
        ax.set(title='Boxplot', xlabel=nome_variavel)

        return finalizar_grafico(ax.get_figure())
    except ValueError as e:
        raise e
    except Exception as e:
        raise e


def graf_freq_acumulada(data_frame, nome_variavel):
    try:
        iniciar_grafico()

        ax = sns.distplot(data_frame[nome_variavel],
                          hist_kws={'cumulative': True},
                          kde_kws={'cumulative': True})

        ax.set_title('Distribuição de frequências acumulada')
        ax.set_ylabel('Acumulado', fontsize=14)
        ax.set_xlabel(nome_variavel, fontsize=14)

        return finalizar_grafico(ax.get_figure())
    except Exception as e:
        raise e


def graf_media(data_frame, nome_variavel):
    try:
        iniciar_grafico()

        np.random.seed(101)
        temp = data_frame[nome_variavel].sample(frac=0.5)
        medias = [temp[0:i].mean() for i in range(1, len(temp))]
        ax = sns.lineplot(medias)
        ax.set_title('Distribuição das médias')
        ax.set_xlabel(nome_variavel, fontsize=14)

        return finalizar_grafico(ax.get_figure())
    except Exception as e:
        raise e

def graf_boxplot_var_denpendente(data_frame, nome_variavel):
    try:
        iniciar_grafico()

        ax = sns.boxplot(y='OBT_NEONATAL', x=nome_variavel, data=data_frame, orient='h', width=0.5)
        ax.figure.set_size_inches(12, 6)
        ax.set_title('Situação neonatal', fontsize=20)
        ax.set_ylabel('Óbito', fontsize=16)
        ax.set_xlabel(nome_variavel, fontsize=16)

        return finalizar_grafico(ax.get_figure())
    except Exception as e:
        raise e


# A função normaltest testa a hipótese nula H0 de que a amostra é proveniente de uma distribuição normal.
# Rejeitar H0 se o valor p≤0,05
def test_normalidade(data_frame, nome_variavel):
    try:
        significancia = 0.05
        stat_test, p_valor = normaltest(data_frame[nome_variavel])
        return not (p_valor <= significancia)
    except Exception as e:
        raise e

# Método inadequado, tem filtrar as colunas categoricas
#def info_correlacao(data_frame, nome_variavel):
#    try:
#        target = pd.to_numeric(data_frame[nome_variavel], errors='coerce')
#        serie_corr = data_frame._get_numeric_data().corrwith(target).round(2)
#        df_corr = pd.DataFrame(serie_corr, columns=[nome_variavel])
#        df_corr.sort_values(by=[nome_variavel], inplace=True)
#        return df_corr
#    except Exception as e:
#        raise e