import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Função para gerar o nome do arquivo
def generate_filename(start_date, end_date):
    return f"ressarcimento_clubes_{start_date.strftime('%d-%m')} a {end_date.strftime('%d-%m')}.xlsx"

# Definição das datas para filtragem
hoje = datetime.today()
inicio_semana = hoje - timedelta(days=hoje.weekday() + 1)
fim_semana = inicio_semana + timedelta(days=6)

# Carregar os dados salvos
file_path = "dados_ressarcimentos.csv"
if "ressarcimentos" not in st.session_state:
    if os.path.exists(file_path):
        st.session_state["ressarcimentos"] = pd.read_csv(file_path)
    else:
        st.session_state["ressarcimentos"] = pd.DataFrame(columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])

# Interface do Streamlit
st.title("📊 Dashboard de Ressarcimentos")
st.markdown("**Preencha os dados para gerar a planilha de ressarcimentos**")

# Criar inputs para os dados
data = st.date_input("Data do ressarcimento", value=hoje, key="data_input")
id_clube = st.text_input("ID do Clube", key="id_clube_input")
nome_clube = st.text_input("Nome do Clube", key="nome_clube_input")
valor = st.text_input("Valor do Ressarcimento (R$)", key="valor_input")
responsavel = st.text_input("Responsável", key="responsavel_input")

# Botão para adicionar o ressarcimento
if st.button("Adicionar Ressarcimento"):
    try:
        valor_float = float(st.session_state["valor_input"].replace(",", "."))
        novo_dado = pd.DataFrame([[st.session_state["data_input"], st.session_state["id_clube_input"], st.session_state["nome_clube_input"], valor_float, st.session_state["responsavel_input"]]],
                                 columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])
        st.session_state["ressarcimentos"] = pd.concat([st.session_state["ressarcimentos"], novo_dado], ignore_index=True)
        st.session_state["ressarcimentos"].to_csv(file_path, index=False)
        st.success("Ressarcimento adicionado com sucesso!")
        
        # Limpar os campos após adicionar
        st.session_state["id_clube_input"] = ""
        st.session_state["nome_clube_input"] = ""
        st.session_state["valor_input"] = ""
        st.session_state["responsavel_input"] = ""
        
        st.rerun()
    except ValueError:
        st.error("Por favor, insira um valor válido para o ressarcimento.")

# Exibir os ressarcimentos adicionados
st.write("### 📅 Ressarcimentos cadastrados:")
st.dataframe(st.session_state["ressarcimentos"])

# Botão para excluir um ressarcimento específico
if not st.session_state["ressarcimentos"].empty:
    excluir_index = st.number_input("Digite o índice do ressarcimento para excluir", min_value=0, max_value=len(st.session_state["ressarcimentos"])-1, step=1)
    if st.button("Excluir Ressarcimento"):
        st.session_state["ressarcimentos"] = st.session_state["ressarcimentos"].drop(excluir_index).reset_index(drop=True)
        st.session_state["ressarcimentos"].to_csv(file_path, index=False)
        st.success("Ressarcimento excluído com sucesso!")
        st.rerun()

# Botão para limpar todos os ressarcimentos
if st.button("Limpar Todos os Ressarcimentos"):
    st.session_state["ressarcimentos"] = pd.DataFrame(columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])
    if os.path.exists(file_path):
        os.remove(file_path)
    st.success("Todos os ressarcimentos foram removidos!")
    st.rerun()

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
