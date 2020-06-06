import pandas as pd
from pkg_resources import resource_filename

from covid.constants import Niveis


def load_population_and_geographic_data() -> pd.DataFrame:
    concelhos_path = resource_filename('covid.data.pt', 'concelhos.csv')
    populacao_path = resource_filename('covid.data.pt', 'populacao.csv')
    concelhos = pd.read_csv(concelhos_path, index_col='Concelho')
    concelhos = concelhos[~concelhos['Nível I'].isna()]
    populacao_por_concelho = pd.read_csv(populacao_path, index_col='Concelho')
    populacao = pd.merge(populacao_por_concelho, concelhos, left_index=True, right_index=True)

    return populacao


def expand_data(dados: pd.DataFrame, nivel: Niveis) -> pd.DataFrame:
    populacao = load_population_and_geographic_data()

    populacao[f'populacao_{nivel}'] = populacao[[nivel, 'populacao2018']].groupby(nivel).populacao2018.transform('sum')

    dados_limpos = dados.drop_duplicates(['Data', 'Concelho'])
    dados_por_nivel = dados_limpos.groupby(['Data', nivel]).agg({'ConfirmadosAcumulado': 'sum'})

    dados_com_regioes_e_populacao = pd.merge(
        dados_por_nivel,
        populacao,
        left_on='Concelho',
        right_on=populacao.str.upper()
    ).drop(columns='Concelhos').copy()
    dados_com_regioes_e_populacao['confirmados_por_milhao'] = dados_com_regioes_e_populacao.ConfirmadosAcumulado / (
            dados_com_regioes_e_populacao.populacao2018 / 1e6)
    return dados_com_regioes_e_populacao
