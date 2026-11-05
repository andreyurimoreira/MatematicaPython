import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="População e Crescimento Demográfico", layout="wide")

@st.cache_data
def carregar_dados(caminho_arquivo):
    xlsx = pd.ExcelFile(caminho_arquivo)
    dados_totais = []

    for sheet in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=sheet)
        dados_totais.append(df)

    return pd.concat(dados_totais, ignore_index=True)

caminho_arquivo = "CD2022_Populacao_2010_Compatibilizada_20231222.xlsx"
df = carregar_dados(caminho_arquivo)

df_cropped = df.iloc[2:5572, 4:]
df_cropped.columns = ["Cidade", "Populacao 2010", "Populacao 2010 (Alterações até 2022) ", "Populacao 2022"]


lista = ["Belo Horizonte", "Curitiba", "Porto Alegre", "Salvador", "Florianópolis"]

dfcidades = df_cropped[df_cropped["Cidade"].isin(lista)]

st.dataframe(dfcidades)


df_melted = dfcidades.melt(
                id_vars=["Cidade"],
                value_vars=["Populacao 2010", "Populacao 2022"],
                var_name="População",
                value_name="quant"
            )

st.dataframe(df_melted)

fig_bar = px.bar(
        df_melted,
            x="Cidade",
            y="quant",
            color="População",
            orientation='v',
            title=f"Crescimento populacao ({"Populacao 2010", "Populacao 2022"})",
            color_discrete_sequence=["#1f77b4", "#e377c2"]
) 


st.plotly_chart(fig_bar, use_container_width=True)