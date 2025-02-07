import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import xlsxwriter

# Configuração do título
st.title("📊 Dashboard de Ressarcimentos Semanais")

# Função para carregar ou criar o arquivo de ressarcimentos
def load_data():
    try:
        df = pd.read_csv("ressarcimentos.csv")
        return df if not df.empty else pd.DataFrame(columns=["Data", "ID Clube", "Nome do Clube", "Valor", "Responsável"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "ID Clube", "Nome do Clube", "Valor", "Responsável"])

def save_data(df):
    df.to_csv("ressarcimentos.csv", index=False)

# Carregar os dados
df = load_data()

# Adicionar novo ressarcimento
st.header("Adicionar Novo Ressarcimento")

col1, col2 = st.columns(2)
with col1:
    data = st.date_input("Data", datetime.date.today())
    id_clube = st.text_input("ID do Clube")
with col2:
    nome_clube = st.text_input("Nome do Clube")
    valor = st.number_input("Valor do Ressarcimento (R$)", min_value=0.0, format="%.2f")
responsavel = st.text_input("Responsável", "")

if st.button("Adicionar Ressarcimento"):
    novo_registro = pd.DataFrame([[data, id_clube, nome_clube, valor, responsavel]], columns=df.columns)
    df = pd.concat([df, novo_registro], ignore_index=True)
    save_data(df)
    st.success("✅ Ressarcimento adicionado com sucesso!")

# Exibir resumo semanal
st.header("Resumo Semanal")
hoje = datetime.date.today()
inicio_semana = hoje - datetime.timedelta(days=hoje.weekday())
fim_semana = inicio_semana + datetime.timedelta(days=6)

df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
df_semana = df[(df["Data"] >= pd.Timestamp(inicio_semana)) & (df["Data"] <= pd.Timestamp(fim_semana))]

if not df_semana.empty:
    total_ressarcido = df_semana["Valor"].sum()
    num_ressarcimentos = len(df_semana)
    clubes_afetados = df_semana["Nome do Clube"].nunique()
    
    st.metric("💰 Total Ressarcido", f"R$ {total_ressarcido:,.2f}")
    st.metric("📝 Quantidade de Ressarcimentos", num_ressarcimentos)
    st.metric("🏆 Clubes Afetados", clubes_afetados)
    
    st.subheader("Detalhes dos Ressarcimentos")
    st.dataframe(df_semana)
else:
    st.warning("Nenhum ressarcimento registrado nesta semana.")

# Exportar relatório
st.header("Exportar Relatório Semanal")

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ressarcimentos')
        writer.book.close()
    processed_data = output.getvalue()
    return processed_data

# Criar nome do arquivo baseado na semana
nome_arquivo = f"Ressarcimento_Clubes_{inicio_semana.strftime('%d-%m')} a {fim_semana.strftime('%d-%m')}.xlsx"

if not df_semana.empty:
    st.download_button(
        label="Baixar Relatório em Excel",
        data=gerar_excel(df_semana),
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Nenhum dado para exportar.")

st.write("⚡ Desenvolvido para a gestão automatizada de ressarcimentos semanais ⚡")
