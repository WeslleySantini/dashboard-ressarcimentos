import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Função para carregar os dados da planilha
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, dtype={"ID CLUBE": str})
        df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True)
        df["VALOR"] = df["VALOR"].astype(str).str.replace('R\$ ', '').str.replace(',', '.').astype(float)
        return df
    return None

# Função para gerar o nome do arquivo
def generate_filename(start_date, end_date):
    return f"ressarcimento_clubes_{start_date.strftime('%d-%m')} a {end_date.strftime('%d-%m')}.xlsx"

# Definição das datas para filtragem
hoje = datetime.today()
inicio_semana = hoje - timedelta(days=hoje.weekday() + 1)
fim_semana = inicio_semana + timedelta(days=6)

# Interface do Streamlit
st.title("📊 Dashboard de Ressarcimentos")
st.markdown("**Carregue sua planilha de ressarcimentos no formato .xlsx**")

uploaded_file = st.file_uploader("Carregue a planilha de ressarcimentos", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### 📂 Dados carregados:")
    st.dataframe(df)
    
    # Filtro por data da semana
    df_semana = df[(df["DATA"] >= inicio_semana) & (df["DATA"] <= fim_semana)]
    
    if df_semana.empty:
        st.warning("Nenhum ressarcimento registrado nesta semana.")
    else:
        st.write("### 📅 Ressarcimentos da semana:")
        st.dataframe(df_semana)
        
        # Total de ressarcimentos na semana
        total_ressarcimentos = df_semana["VALOR"].sum()
        st.write(f"### 💰 Total da semana: **R$ {total_ressarcimentos:,.2f}**")
        
        # Gráfico de barras por clube
        fig, ax = plt.subplots()
        df_semana.groupby("NOME DO CLUBE")["VALOR"].sum().sort_values().plot(kind="barh", ax=ax)
        ax.set_xlabel("Valor Ressarcido (R$)")
        ax.set_ylabel("Nome do Clube")
        ax.set_title("Total de Ressarcimentos por Clube")
        st.pyplot(fig)
        
        # Botão para baixar a planilha semanal
        filename = generate_filename(inicio_semana, fim_semana)
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df_semana.to_excel(writer, index=False, sheet_name="Ressarcimentos")
            writer.close()
        
        with open(filename, "rb") as file:
            st.download_button(
                label="📥 Baixar planilha semanal",
                data=file,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
