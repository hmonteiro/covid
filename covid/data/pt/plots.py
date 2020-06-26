import matplotlib.pylab as plt
import pandas as pd
import seaborn as sns

from covid.constants import Niveis

sns.set()


def plot_densidade(dados: pd.DataFrame, nivel: Niveis, top_k: int = 5):
    dados_por_nivel_sort = dados.iloc[-1].confirmados_por_km2.sort_values(ascending=False).index
    crescimento_semanal_nivel = \
        ((dados.confirmados_por_km2 - dados.confirmados_por_km2.shift(7)) / dados.confirmados_por_km2.shift(7)).iloc[
            -1].sort_values(ascending=False)
    top_crescimento_nivel = crescimento_semanal_nivel.head(top_k).index
    legendas_aumento = {k: f'{k} (subiu {v:.1f}%)' for k, v in (crescimento_semanal_nivel * 100).to_dict().items()}

    with sns.plotting_context("talk"):
        plt.figure(figsize=(16, 9))
        for c in dados.confirmados_por_km2[dados_por_nivel_sort]:
            if c in top_crescimento_nivel:
                plt.plot(dados.confirmados_por_km2[c].fillna(0), label=legendas_aumento[c], linewidth=5)
            else:
                plt.plot(dados.confirmados_por_km2[c].fillna(0), label=legendas_aumento[c], alpha=0.5)
        l = plt.legend(loc=5, bbox_to_anchor=(1.5, 0.5))
        plt.xlim((dados.index[0], dados.index[-1]))
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Casos por km2')
        plt.title(f'Casos confirmados por km2 por {nivel.value}.\n'
                  f'Realce para os {top_k} locais com maior aumento percentual nos últimos 7 dias.')


def plot(dados: pd.DataFrame, nivel: Niveis, top_k: int = 5):
    dados_por_nivel_sort = dados.iloc[-1].confirmados_por_milhao.sort_values(ascending=False).index
    crescimento_semanal_nivel = \
        ((dados.ConfirmadosAcumulado - dados.ConfirmadosAcumulado.shift(7)) / dados.ConfirmadosAcumulado.shift(7)).iloc[
            -1].sort_values(ascending=False)
    top_crescimento_nivel = crescimento_semanal_nivel.head(top_k).index
    legendas_aumento = {k: f'{k} (subiu {v:.1f}%)' for k, v in (crescimento_semanal_nivel * 100).to_dict().items()}

    with sns.plotting_context("talk"):
        plt.figure(figsize=(16, 9))
        for c in dados.confirmados_por_milhao[dados_por_nivel_sort]:
            if c in top_crescimento_nivel:
                plt.plot(dados.confirmados_por_milhao[c].fillna(0), label=legendas_aumento[c], linewidth=5)
            else:
                plt.plot(dados.confirmados_por_milhao[c].fillna(0), label=legendas_aumento[c], alpha=0.5)
        plt.legend(loc=5, bbox_to_anchor=(1.5, 0.5))
        plt.xlim((dados.index[0], dados.index[-1]))
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Casos por milhão')
        plt.title(f'Casos confirmados por milhão de habitantes por {nivel.value}.\n'
                  f'Realce para os {top_k} locais com maior aumento percentual nos últimos 7 dias.')
