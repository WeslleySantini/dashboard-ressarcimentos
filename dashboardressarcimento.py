import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Definir nome da aba no navegador
st.set_page_config(page_title="Ressarcimento Clubes", page_icon="logo.png")

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
st.image("logo.png", width=200)
st.title("📊 Dashboard de Ressarcimentos")
st.markdown("Gerencie e visualize seus ressarcimentos de forma profissional!")

# Criar inputs para os dados
data = st.date_input("📅 Data do ressarcimento", value=hoje)
id_clube = st.text_input("🏠 ID do Clube", value="")
nome_clube = st.text_input("🏷️ Nome do Clube", value="")
valor = st.text_input("💰 Valor do Ressarcimento", value="")
responsavel = st.text_input("👤 Responsável", value="")

# Botão para adicionar o ressarcimento
if st.button("✅ Adicionar Ressarcimento"):
    if id_clube and nome_clube and valor and responsavel:
        try:
            valor_float = float(valor.replace("R$", "").replace(",", ".").strip())
            novo_dado = pd.DataFrame([[data, id_clube, nome_clube, valor_float, responsavel]],
                                     columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])
            st.session_state["ressarcimentos"] = pd.concat([st.session_state["ressarcimentos"], novo_dado], ignore_index=True)
            st.session_state["ressarcimentos"].to_csv(file_path, index=False)
            st.success("Ressarcimento adicionado com sucesso!")
            st.rerun()
        except ValueError:
            st.error("Por favor, insira um valor válido para o ressarcimento.")
    else:
        st.error("Todos os campos devem ser preenchidos.")

# Exibir os ressarcimentos cadastrados
st.write("### 📋 Lista de Ressarcimentos")
st.dataframe(st.session_state["ressarcimentos"])

# Exibir somatória dos valores cadastrados
if not st.session_state["ressarcimentos"].empty:
    total_valor = st.session_state["ressarcimentos"]["VALOR"].sum()
    st.write(f"### 💰 Total de Ressarcimentos: R$ {total_valor:,.2f}")

    # Gráfico de valores por clube
    fig, ax = plt.subplots()
    st.session_state["ressarcimentos"].groupby("NOME DO CLUBE")["VALOR"].sum().plot(kind="bar", ax=ax, color="blue")
    ax.set_title("Ressarcimentos por Clube")
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Nome do Clube")
    st.pyplot(fig)

# Botão para excluir um ressarcimento específico
if not st.session_state["ressarcimentos"].empty:
    excluir_index = st.number_input("Digite o índice do ressarcimento para excluir", min_value=0, max_value=len(st.session_state["ressarcimentos"])-1, step=1)
    if st.button("🗑️ Excluir Ressarcimento"):
        st.session_state["ressarcimentos"] = st.session_state["ressarcimentos"].drop(excluir_index).reset_index(drop=True)
        st.session_state["ressarcimentos"].to_csv(file_path, index=False)
        st.success("Ressarcimento excluído com sucesso!")
        st.rerun()

# Botão para limpar todos os ressarcimentos sem confirmação
if st.button("🧹 Limpar Todos os Ressarcimentos"):
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
        
        # Ajustando colunas e centralizando texto
        center_format = workbook.add_format({"align": "center"})
        currency_format = workbook.add_format({"align": "center", "num_format": "R$ #,##0.00"})
        worksheet.set_column("A:A", 15, center_format)
        worksheet.set_column("B:B", 12, center_format)
        worksheet.set_column("C:C", 25, center_format)
        worksheet.set_column("D:D", 12, currency_format)
        worksheet.set_column("E:E", 15, center_format)
        
        writer.close()
    with open(filename, "rb") as file:
        st.download_button(
            label="📥 Baixar planilha de ressarcimentos",
            data=file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
