import streamlit as st
import pandas as pd
import plotly.express as px




st.set_page_config(page_title="Cuidados", layout="wide")


@st.cache_data
def carregar_dados(caminho_arquivo):
    xls = pd.ExcelFile(caminho_arquivo)


    abas_anos = [sheet for sheet in xls.sheet_names if "(CV)" not in sheet]


    dados_totais = []


    for ano in abas_anos: 
        df_raw = pd.read_excel(xls, sheet_name=ano)


        start_idx = df_raw[df_raw.iloc[:, 0] == "Brasil"].index[0]


        df_ano = df_raw.iloc[start_idx:, [0,1,2,3]].copy()
        df_ano.columns = ["Localidade", "Total", "Homem", "Mulher"]


        df_ano = df_ano.dropna(subset=["Localidade"])
        df_ano = df_ano[df_ano["Localidade"].astype(str).str.strip() != ""]


        for col in ["Total", "Homem", "Mulher"]:
            df_ano[col] = pd.to_numeric(df_ano[col], errors="coerce")
        
        df_ano["Ano"] = str(ano)
        dados_totais.append(df_ano)


    df_completo = pd.concat(dados_totais, ignore_index=True)
    return df_completo


caminho_arquivo = r"H:\python\TerceiraEtapa\exemplo\Tabela 1.1.2.xls"




try:
    df = carregar_dados(caminho_arquivo)


    st.sidebar.header("Flitros")


    anos_disponveis = sorted(df["Ano"].unique(), reverse=True)
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano", anos_disponveis)


    localidades_disponiveis = df["Localidade"].unique().tolist()
    localidades_selecionados = st.sidebar.multiselect(
        "Aelecoone as Regioes/UFs:",
        options=localidades_disponiveis,
        default=["Brasil", "Norte", "Mordeste", "Sudeste", "Sul", "Centro-Oeste"]
    )


    st.title("Horas Dedicadas a Cuidados e Afazeres Domesticos")
    st.markdown("Analise da media de horas semanais dedicadas por pessoas ocupadas de 14 anos ou mais por sexo")


    df_filtrado= df[(["Ano"] == ano_selecionado) & (df["Localidade"].isin)]


    if not df_filtrado.empty:
        st.subheader(f"Dados em Tabela ({ano_selecionado})")
        st.dataframe(df_filtrado[["Localidade", "Total", "Homem", "Mulher"]].reset_index(drop=True), use_container_width=True)




        st.markdown("---")
        st.subheader("Graficos Comparativos")


        col1, col2 = st.columns(2)


        with col1: 
            df_melted = df_filtrado.melt(
                id_vars=["Localidade"],
                value_vars=["Homem", "Mulher"],
                var_name="Sexo",
                value_name="Horas Semanais"
            )


            fig_bar = px.bar(
                df_melted,
                x="Localidade",
                y="Horas Semanais"
                color="Sexo",
                barmode="group",
                title=f"Media de Horas por Sexo ({ano_selecionado})",
                color_discrete_sequence=["#1f77b4", "#e377c2"],
                labels={"Horas Semanais" : "Horas/Semana", "Localidade": "Regiao / UF"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)




        with col2: 
            df_historico = df[df["Localidade"].isin(localidades_disponiveis)]


            fig_line = px.line(
                df_historico,
                x="Ano",
                y="Total",
                color="Localidade",
                markers=True,
                title="Evolucao Temporal do Roral de Horas Dedicados",
                labels={"Total": "Horas/semana", "Ano": "Ano"}
            )
            st.plotly_chart(fig_line, use_container_width=True)


    else:
        st.warning("Nenhuma localidade selecionada nos filtros da barra leteral.")




except Exception as e:
    st.error(f"Erro ao carregar o aequivo: {e}")
    st.info("Certifique-se de que o arquivo 'taebla 1.1.2.xls esta no mesmo diretorio do script")