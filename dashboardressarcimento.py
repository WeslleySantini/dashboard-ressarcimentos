import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Função para gerar o nome do arquivo
def generate_filename(start_date, end_date):
    return f"ressarcimento_clubes_{start_date.strftime('%d-%m')} a {end_date.strftime('%d-%m')}.xlsx"

# Definição das datas para filtragem
hoje = datetime.today()
inicio_semana = hoje - timedelta(days=hoje.weekday() + 1)
fim_semana = inicio_semana + timedelta(days=6)

# Interface do Streamlit
st.title("📊 Dashboard de Ressarcimentos")
st.markdown("**Preencha os dados para gerar a planilha de ressarcimentos**")

# Criar inputs para os dados
data = st.date_input("Data do ressarcimento", value=hoje)
id_clube = st.text_input("ID do Clube")
nome_clube = st.text_input("Nome do Clube")
valor = st.number_input("Valor do Ressarcimento", min_value=0.01, format="%.2f")
responsavel = st.text_input("Responsável")

# Criar DataFrame para armazenar os dados
if "ressarcimentos" not in st.session_state:
    st.session_state["ressarcimentos"] = pd.DataFrame(columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])

# Botão para adicionar o ressarcimento
if st.button("Adicionar Ressarcimento"):
    novo_dado = pd.DataFrame([[data, id_clube, nome_clube, valor, responsavel]], columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])
    st.session_state["ressarcimentos"] = pd.concat([st.session_state["ressarcimentos"], novo_dado], ignore_index=True)
    st.success("Ressarcimento adicionado com sucesso!")

# Exibir os ressarcimentos adicionados
st.write("### 📅 Ressarcimentos cadastrados:")
st.dataframe(st.session_state["ressarcimentos"])

# Botão para baixar a planilha semanal
if not st.session_state["ressarcimentos"].empty:
    filename = generate_filename(inicio_semana, fim_semana)
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        st.session_state["ressarcimentos"].to_excel(writer, index=False, sheet_name="Ressarcimentos")
        worksheet = writer.sheets["Ressarcimentos"]
        workbook = writer.book
        
        # Aplicando formatação ao cabeçalho
        header_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#92D050",
            "border": 1
        })
        for col_num, value in enumerate(st.session_state["ressarcimentos"].columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ajustando colunas
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 12)
        worksheet.set_column("C:C", 25)
        worksheet.set_column("D:D", 12)
        worksheet.set_column("E:E", 15)
        
        # Aplicando formatação de moeda
        currency_format = workbook.add_format({"num_format": "R$ #,##0.00"})
        worksheet.set_column("D:D", 12, currency_format)
        
        writer.close()
    
    with open(filename, "rb") as file:
        st.download_button(
            label="📥 Baixar planilha de ressarcimentos",
            data=file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
