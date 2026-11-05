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

st.divider()
st.subheader("")


# Conteúdo exigido no seu cenário/persona
st.divider()
st.subheader("📰 Notícias e Contexto: Transição Demográfica no Brasil")

st.markdown("""
*Monitore os principais acontecimentos, estudos de macrocefalia urbana e relatórios dos Censos Demográficos que impactam diretamente o planejamento das capitais brasileiras.*
""")

# ==========================================
# SEÇÃO 1: TRANSICÃO ETÁRIA E DINÂMICA DEMOGRÁFICA
# ==========================================
st.markdown("---")
st.subheader("🧓 Transição Etária e Inversão da Pirâmide")

col_etaria_txt, col_etaria_img = st.columns([3, 2])

with col_etaria_txt:
    with st.container(border=True):
        st.markdown("### Porto Alegre (RS): A Capital Mais Envelhecida do Brasil")
        st.markdown(
            "Estudos demográficos detalhados posicionam a capital gaúcha na vanguarda da transição etária nacional. "
            "O envelhecimento acelerado da estrutura populacional de Porto Alegre exige atenção imediata de gestores públicos. "
            "A inversão da base da pirâmide requer a readequação urgente de orçamentos municipais para focar em saúde preventiva, "
            "atendimento à terceira idade e acessibilidade na infraestrutura urbana."
        )
        st.link_button("Ver Análise Completa", "https://ecodebate.com.br")

with col_etaria_img:
    st.image(
        "https://ibge.gov.br", 
        caption="Estrutura e Transição da Pirâmide Etária Brasileira (Fonte: IBGE)",
        use_container_width=True
    )

# ==========================================
# SEÇÃO 2: MUDANÇAS NO RANKING DAS CAPITAIS (FEED DE NOTÍCIAS)
# ==========================================
st.markdown("---")
st.subheader("📊 Relatórios Estatísticos das Metrópoles")

col_noticia1, col_noticia2, col_noticia3 = st.columns(3)

with col_noticia1:
    # Card 1: Salvador (Perda Populacional)
    with st.container(border=True):
        st.image(image=r"imagens\unnamed.png")
        st.markdown("### 📉 Salvador perde o posto de 3ª maior cidade do país")
        st.markdown(
            "Segundo dados oficiais do **Censo 2022**, divulgados pelo **IBGE**, a capital baiana registrou uma "
            "**redução de 9,6%** na sua população frente a 2010. Isso representou uma diminuição de menos **257.651 moradores** em 12 anos. "
            "Em 31 de julho de 2022, a capital contava com **2.418.005 habitantes**, caindo para a quinta posição no ranking nacional."
        )
        st.link_button("Ler Notícia no Jornal Correio", "https://correio24horas.com.br")

    st.markdown("<br>", unsafe_allow_html=True)


  
with col_noticia3:
      # Card 2: Região Metropolitana de Curitiba (Expansão e Periferia)
    with st.container(border=True):
        st.image(image=r"imagens\unnamed2.png")
        st.markdown("### 🌲 Expansão Metropolitana e Diversidade na RMC")
        st.markdown(
            "Estudos sobre a **Região Metropolitana de Curitiba** revelam um forte padrão de crescimento periférico e expansão da metrópole. "
            "Enquanto o polo urbano central passa por uma estabilização de ritmo, os municípios vizinhos absorvem de forma potente as novas demandas imobiliárias, "
            "carregando novos desafios de integração de transporte e atendimento a minorias quilombolas e indígenas fora de territórios homologados."
        )
        st.link_button("Acessar Análise da RMC", "https://observatoriodasmetropoles.net.br")




with col_noticia2:
    # Card 3: RMBH (Desaceleração Demográfica)
    with st.container(border=True):
        st.image(image=r"imagens\image.png")
        st.markdown("### ⛰️ Desaceleração de Ritmo na Grande Belo Horizonte")
        st.markdown(
            "Os dados mostram que entre 2010 e 2022 a **RMBH** ganhou 243.724 pessoas, um incremento de 5% durante todo o período, "
            "com um crescimento anual médio de apenas **0,41%**. Considerando que o crescimento demográfico do país não foi muito maior do que 0,5% ao ano "
            "no mesmo intervalo, pode-se entender por que 16 municípios da RMBH cresceram abaixo de 1% ao ano. "
            "Apenas cinco municípios tiveram taxas de crescimento abaixo da média metropolitana: **Contagem, Sabará, Belo Horizonte, Caeté e Baldim**."
        )
        st.link_button("Ver Estudo de Vulnerabilidade da RMBH", "https://observatoriodasmetropoles.net.br")

# ==========================================
# SEÇÃO 3: FENÔMENOS URBANOS E DESAFIOS SOCIOESPACIAIS
# ==========================================
st.markdown("---")
st.subheader("🏙️ Desafios Socioespaciais e Infraestrutura")

col_macro_txt, col_macro_img = st.columns([3, 2])

with col_macro_txt:
    with st.container(border=True):
        st.markdown("### O Fenômeno da Macrocefalia Urbana")
        st.markdown(
            "A **macrocefalia urbana** é um fenômeno caracterizado pelo crescimento rápido e desordenado das cidades, resultando na "
            "**concentração espacial desigual de serviços, atividades econômicas e população** em um único centro urbano. "
            "Esse processo ocorre principalmente em países subdesenvolvidos devido ao êxodo rural acelerado e à falta de planejamento urbano eficiente por parte do poder público. "
            "\n\nComo principais consequências desse inchaço desordenado, enfrentamos o **aprofundamento da segregação socioespacial**, precarização da mobilidade, escassez de saneamento básico e o **intenso processo de favelização**."
        )
        st.link_button("Estudar Conceito no Brasil Escola", "https://uol.com.br")
    
    st.info(
        "⚠️ **Recomendação Estratégica para Prefeitos:**\n\n"
        "A desaceleração demográfica das áreas centrais, combinada com o inchaço imobiliário das periferias metropolitanas, "
        "torna obrigatória a **revisão periódica dos Planos Diretores**. Os investimentos em infraestrutura e o orçamento de saúde pública "
        "precisam acompanhar os novos fluxos de deslocamento pendular da população."
    )

with col_macro_img:
    # Ilustração da Segregação Socioespacial e Urbanização Tardira (Usando imagens conceituais que batem com o briefing)
    st.image(
        "https://wikimedia.org",
        caption="Obra 'Operários' (1933) de Tarsila do Amaral: Retrato histórico do fluxo migratório e da concentração técnica da industrialização brasileira.",
        use_container_width=True
    )
    st.image(
        "https://shutterstock.com",
        caption="Paisagem Urbana Desigual: Processo de favelização e o desafio da infraestrutura de moradia nas grandes metrópoles brasileiras.",
        use_container_width=True
    )