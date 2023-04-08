import base64
import io
import os
import urllib

import pandas as pd
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype

from django.templatetags.static import static
from django.contrib.staticfiles.utils import get_files
from django.contrib.staticfiles.storage import StaticFilesStorage
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

        tipos_de_dados.drop(columns=['ddd'], inplace=True)

        return tipos_de_dados
    except Exception as e:
        raise e

def info_coluna_quantidade(data_frame, nome_variavel):
    freq = data_frame[nome_variavel].value_counts(dropna=False)
    porc = (data_frame[nome_variavel].value_counts(dropna=False, normalize=True) * 100).round(2)
    dis_freq_quantitativas_personalizadas = pd.DataFrame({'Frequência': freq, 'Porcentagem (%)': porc})
    return dis_freq_quantitativas_personalizadas


# Usar quando tiver um target do tipo Valor
def info_coluna_descritiva(data_frame, agrupamento, target):
    agrupamento = data_frame.groupby(agrupamento)
    descritiva = pd.DataFrame(agrupamento[target].describe().round(2))
    print(descritiva)
    return descritiva

def graf_hist(data_frame, nome_variavel):
    try:
        plt.clf()
        plt.rc('figure', figsize=(15, 8))
        fig = plt.gcf()
        ax = fig.gca()
        data_frame[nome_variavel].value_counts(dropna=False).plot.bar(ax=ax)
        #data_frame.hist([nome_variavel], ax=ax, ec="k")
        # convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        return uri
    except ValueError:
        print()


