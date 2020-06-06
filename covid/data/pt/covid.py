import json
import string
from typing import Dict, Optional

import pandas as pd
import requests


def get_data(proxies: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    colunas_de_interesse = ['Concelho', 'ConfirmadosAcumulado', 'ConfirmadosNovos', 'Data']
    query_template = ('https://services.arcgis.com/CCZiGSEQbAxxFVh3/ArcGIS/rest/services/'
                      'COVID_Concelhos_DadosDiariosConcelho_VIEW2/FeatureServer/0/query?'
                      'where=Concelho+like+%27{prefix}%25%27&objectIds=&time=&geometry='
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
    dfs = []
    for prefix in string.ascii_uppercase[:26]:
        query = query_template.format(prefix=prefix)
        json_data = json.loads(requests.get(query, proxies=proxies).text)
        df = pd.DataFrame([f['attributes'] for f in json_data['features']])
        dfs.append(df)
    dados_por_concelho = pd.concat(dfs)
    dados_por_concelho.Data = pd.to_datetime(dados_por_concelho.Data, unit='ms')
    return dados_por_concelho[colunas_de_interesse].copy()
