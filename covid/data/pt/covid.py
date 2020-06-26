import json
from functools import partial
from multiprocessing import Pool
from typing import Dict, Optional

import numpy as np
import pandas as pd
import requests
from pkg_resources import resource_filename


def get_raw_data(proxies: Optional[Dict[str, str]] = None):
    concelhos_path = resource_filename('covid.data.pt', 'concelhos.csv')
    concelhos = pd.read_csv(concelhos_path, usecols=['Concelho']).Concelho.str.upper().to_list()
    with Pool(10) as p:
        f = partial(_get_concelho, proxies=proxies)
        dfs = p.map(f, concelhos)
    dados_por_concelho = pd.concat(dfs).rename(
        columns={'Concelho': 'CONCELHO'}).drop_duplicates(['Data', 'CONCELHO'])
    dados_por_concelho.Data = pd.to_datetime(dados_por_concelho.Data, unit='ms')
    return dados_por_concelho


def _get_concelho(concelho, proxies):
    query_template = ('https://services.arcgis.com/CCZiGSEQbAxxFVh3/ArcGIS/rest/services/'
                      'COVID_Concelhos_DadosDiariosConcelho_VIEW2/FeatureServer/0/query?'
                      'where=Concelho+like+%27{concelho}%27&objectIds=&time=&geometry='
                      '&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects'
                      '&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false'
                      '&outFields=*&returnGeometry=false&featureEncoding=esriDefault'
                      '&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision='
                      '&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false'
                      '&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false'
                      '&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields='
                      '&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=32000'
                      '&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters='
                      '&sqlFormat=none&f=pjson&token=')
    query = query_template.format(concelho=concelho)
    json_data = json.loads(requests.get(query, proxies=proxies).text)
    df = pd.DataFrame([f['attributes'] for f in json_data['features']])
    return df


def get_data(proxies: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    dados_por_concelho = get_raw_data(proxies)
    colunas_de_interesse = ['CONCELHO', 'ConfirmadosAcumulado', 'ConfirmadosNovos', 'Data']
    dados_por_concelho = dados_por_concelho[colunas_de_interesse]

    tabela = dados_por_concelho.pivot('Data', 'CONCELHO').ffill().fillna(0)
    tabela[
        (tabela > tabela.sort_index(ascending=False).cummin().sort_index())] = np.nan
    tabela = tabela.interpolate()
    dados_por_concelho = tabela.stack().reset_index()

    concelhos_path = resource_filename('covid.data.pt', 'concelhos.csv')
    concelhos = pd.read_csv(concelhos_path)
    concelhos = concelhos[~concelhos['Nível I'].isna()]
    resultado = pd.merge(left=dados_por_concelho,
                         right=concelhos,
                         left_on='CONCELHO',
                         right_on=concelhos.Concelho.str.upper()).drop(columns='CONCELHO')
    return resultado
