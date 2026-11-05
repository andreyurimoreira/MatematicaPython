import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página (Mantida, mas com ícone)
st.set_page_config(page_title="População e Crescimento Demográfico", layout="wide", page_icon="🏙️")

# ==========================================
# BASE DO CÓDIGO (Lógica de dados mantida)
# ==========================================
@st.cache_data
def carregar_dados(caminho_arquivo):
    xlsx = pd.ExcelFile(caminho_arquivo)
    dados_totais = []
    for sheet in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=sheet)
        dados_totais.append(df)
    return pd.concat(dados_totais, ignore_index=True)

caminho_arquivo = "CD2022_Populacao_2010_Compatibilizada_20231222.xlsx"

# Bloco try-except para evitar que a tela quebre caso o arquivo não esteja na pasta
try:
    df = carregar_dados(caminho_arquivo)
    df_cropped = df.iloc[2:5572, 4:].copy()
    df_cropped.columns = ["Cidade", "Populacao 2010", "Populacao 2010 (Alterações até 2022) ", "Populacao 2022"]
except Exception as e:
    st.error(f"⚠️ Erro ao carregar os dados. Certifique-se de que o arquivo Excel está na mesma pasta. Erro: {e}")
    st.stop()

# ==========================================
# SIDEBAR (Filtros e Cenário)
# ==========================================
st.sidebar.title("⚙️ Filtros de Análise")
st.sidebar.markdown("Ajuste os parâmetros para os prefeitos.")

# Filtros adicionais do briefing (Visual)
regiao = st.sidebar.selectbox("Região", ["Todas", "Sul", "Sudeste", "Nordeste", "Norte", "Centro-Oeste"])
federacao = st.sidebar.selectbox("Unidade da Federação", ["Todos os Estados", "MG", "PR", "RS", "BA", "SC"])
anos = st.sidebar.multiselect("Anos de Censo", ["2010", "2022"], default=["2010", "2022"])

# Aplicando os filtros ao DataFrame
df_filtrado = df_cropped.copy()

# Filtro por Região
if regiao != "Todas":
    regioes = {
        "Sul": ["Curitiba", "Porto Alegre", "Florianópolis"],
        "Sudeste": ["Belo Horizonte"],
        "Nordeste": ["Salvador"],
    }
    df_filtrado = df_filtrado[df_filtrado["Cidade"].isin(regioes.get(regiao, []))]

# Filtro por UF
if federacao != "Todos os Estados":
    ufs = {
        "MG": ["Belo Horizonte"],
        "PR": ["Curitiba"],
        "RS": ["Porto Alegre"],
        "BA": ["Salvador"],
        "SC": ["Florianópolis"],
    }
    df_filtrado = df_filtrado[df_filtrado["Cidade"].isin(ufs.get(federacao, []))]

# Filtro por Anos de Censo
if "2010" not in anos:
    df_filtrado = df_filtrado.drop(columns=["Populacao 2010"], errors="ignore")
if "2022" not in anos:
    df_filtrado = df_filtrado.drop(columns=["Populacao 2022"], errors="ignore")

st.sidebar.divider()

# A sua 'lista' original agora é controlada pela sidebar
cidades_opcoes = ["Belo Horizonte", "Curitiba", "Porto Alegre", "Salvador", "Florianópolis"]
lista = st.sidebar.multiselect(
    "🏙️ Selecione as Capitais:", 
    options=cidades_opcoes, 
    default=cidades_opcoes
)

st.sidebar.divider()
st.sidebar.info("💡 **Apresentação Startup:**\nAuxiliando na alocação de orçamentos para saúde e infraestrutura urbana.")

# ==========================================
# FRONTEND PRINCIPAL (Layout bonito)
# ==========================================
st.title("🏙️ População e Crescimento Demográfico")
st.markdown("""
*Análise estratégica para Prefeitos: Revisão de Planos Diretores e impacto do envelhecimento populacional.*
""")

# CORREÇÃO AQUI: Filtrando a partir do df_filtrado (que já obedece os filtros de anos, UFs e regiões)
dfcidades = df_filtrado[df_filtrado["Cidade"].isin(lista)]

# Exibindo KPIs para deixar visualmente profissional
st.subheader("📈 Resumo Executivo")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Capitais Selecionadas", len(dfcidades["Cidade"].unique()))
with col2:
    st.metric("Status", "Processando Projeções")
with col3:
    st.metric("Foco do Orçamento", "Saúde & Infraestrutura")

st.divider()

# Escondendo os dataframes brutos em um "expander" para não poluir a tela
with st.expander("📂 Visualizar Tabelas de Dados Brutos"):
    st.dataframe(dfcidades, use_container_width=True)

    # CORREÇÃO DO MELT DINÂMICO: Identifica quais colunas de valor realmente existem no df atual
    colunas_disponiveis = [col for col in ["Populacao 2010", "Populacao 2022", "Populacao diferenca entre 2010 e 2022 "] if col in dfcidades.columns]
    
    if colunas_disponiveis:
        df_melted = dfcidades.melt(
            id_vars=["Cidade"],
            value_vars=colunas_disponiveis,
            var_name="População",
            value_name="quant"
        )
        st.markdown("**Dados Transformados (Melted)**")
        st.dataframe(df_melted, use_container_width=True)
    else:
        st.warning("Nenhum ano selecionado para gerar a tabela de dados brutos transformados.")
        df_melted = pd.DataFrame()

# ==========================================
# GRÁFICOS E CONTEÚDO ADICIONAL
# ==========================================
st.subheader("📊 Comparativo Populacional por Capital")

if not df_melted.empty:
    # Gráfico original mantido (com ajuste no título e no modo das barras)
    fig_bar = px.bar(
        df_melted,
        x="Cidade",
        y="quant",
        color="População",
        barmode="group", # Barras lado a lado fica mais fácil de ler
        orientation='v',
        title="Crescimento populacional", 
        color_discrete_sequence=["#1f77b4", "#e377c2", "#2ca02c"] 
    ) 

    # Deixando o fundo transparente e mais elegante
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Cidades",
        yaxis_title="Habitantes"
    )

    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Selecione ao menos um Ano de Censo na barra lateral para visualizar o gráfico.")

# Conteúdo exigido no seu cenário/persona
st.divider()
st.subheader("📰 Notícias e Contexto: Transição Demográfica no Brasil")