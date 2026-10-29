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

st.write("Colunas disponíveis no DataFrame:", df.columns)

st.sidebar.header("Filtros")
if "Municipio" in df.columns and "Ano" in df.columns and "Populacao 2010" in df.columns:
    regioes = df["Municipio"].unique()
    anos = df["Ano"].unique()
    populacao = df["Populacao 2010"].unique()

    regiao_selecionada = st.sidebar.selectbox("Selecione o Município", regioes)
    uf_selecionada = st.sidebar.selectbox("Selecione a População de 2010", populacao)
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano", anos)

    df_filtrado = df[
        (df["Municipio"] == regiao_selecionada) &
        (df["Populacao 2010"] == uf_selecionada) &
        (df["Ano"] == ano_selecionado)
    ]
else:
    st.error("As colunas necessárias ('Municipio', 'Ano', 'Populacao 2010') não foram encontradas no arquivo.")

st.title("Indicador: População e Crescimento Demográfico")

if "População" in df.columns and "Faixa Etária" in df.columns and "Sexo" in df.columns:
    st.subheader("Pirâmide Etária")
    fig_piramide = px.bar(
        df_filtrado,
        x="População",
        y="Faixa Etária",
        color="Sexo",
        orientation="h",
        title="Pirâmide Etária"
    )
    st.plotly_chart(fig_piramide, use_container_width=True)
else:
    st.error("As colunas necessárias para a Pirâmide Etária ('População', 'Faixa Etária', 'Sexo') não foram encontradas.")

if "Município" in df.columns and "Taxa de Crescimento" in df.columns:
    st.subheader("Mapa de Crescimento Populacional")
    fig_mapa = px.choropleth(
        df,
        geojson="",  
        locations="Município",
        color="Taxa de Crescimento",
        scope="south america",
        title="Mapa de Crescimento Populacional"
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
else:
    st.error("As colunas necessárias para o Mapa de Crescimento ('Município', 'Taxa de Crescimento') não foram encontradas.")

if "Ano" in df.columns and "População" in df.columns and "Município" in df.columns:
    st.subheader("Projeção Populacional")
    fig_linhas = px.line(
        df,
        x="Ano",
        y="População",
        color="Município",
        title="Projeção Populacional"
    )
    st.plotly_chart(fig_linhas, use_container_width=True)
else:
    st.error("As colunas necessárias para a Projeção Populacional ('Ano', 'População', 'Município') não foram encontradas.")


if "Taxa de Crescimento" in df_filtrado.columns:
    st.subheader("Indicadores")
    taxa_crescimento = df_filtrado["Taxa de Crescimento"].mean()
    st.metric(label="Taxa Média de Crescimento", value=f"{taxa_crescimento:.2f}%")
else:
    st.error("A coluna 'Taxa de Crescimento' não foi encontrada no DataFrame filtrado.")


st.markdown("### Notícias e Imagens")
st.markdown("Notícias sobre a transição demográfica do Brasil e envelhecimento da população.")
st.image("", caption="Expansão Urbana")