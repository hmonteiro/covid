import pandas as pd
from pkg_resources import resource_filename

from covid.constants import Niveis


def load_population_and_geographic_data() -> pd.DataFrame:
    concelhos_path = resource_filename('covid.data.pt', 'concelhos.csv')
    populacao_path = resource_filename('covid.data.pt', 'populacao.csv')
    concelhos = pd.read_csv(concelhos_path, index_col='Concelho')
    concelhos = concelhos[~concelhos['Nível I'].isna()]
    populacao_por_concelho = pd.read_csv(populacao_path, index_col='Concelho')
    populacao = pd.merge(populacao_por_concelho, concelhos, left_index=True, right_index=True).reset_index(drop=False)
    populacao['area'] = populacao.populacao2018 / populacao.densidade2018

    return populacao


def expand_data(dados: pd.DataFrame, nivel: Niveis) -> pd.DataFrame:
    populacao = load_population_and_geographic_data()

    populacao_nivel = populacao[[nivel.value, 'populacao2018', 'area']].groupby(nivel.value).sum()

    dados_por_nivel = dados.groupby(['Data', nivel.value]).sum()

    dados_com_regioes_e_populacao = pd.merge(
        dados_por_nivel,
        populacao_nivel,
        left_on=nivel.value,
        right_index=True
    )
    dados_com_regioes_e_populacao['confirmados_por_milhao'] = dados_com_regioes_e_populacao.ConfirmadosAcumulado / (
            dados_com_regioes_e_populacao.populacao2018 / 1e6)
    dados_com_regioes_e_populacao['confirmados_por_km2'] = dados_com_regioes_e_populacao.ConfirmadosAcumulado / (
            dados_com_regioes_e_populacao.area)
    return dados_com_regioes_e_populacao.unstack()
