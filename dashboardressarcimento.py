import pandas as pd
import streamlit as st
import gdown
import os
from datetime import datetime, timedelta

# Definir nome da aba no navegador
st.set_page_config(page_title="Ressarcimento Clubes", page_icon="logo.png")

# ID do arquivo no Google Drive
file_id = "1dlOAiRINDsDjF30uxCaHnU1bE-kge92K"
file_path = "dados_ressarcimentos.csv"

# Função para carregar os dados do Google Drive
def carregar_dados():
    try:
        gdown.download(f"https://drive.google.com/uc?id={file_id}", file_path, quiet=False)
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Erro ao carregar dados do Google Drive: {e}")
        return pd.DataFrame(columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])

# Função para salvar os dados no Google Drive
def salvar_dados(df):
    df.to_csv(file_path, index=False)
    os.system(f"gdown --id {file_id} -O {file_path}")

# Inicializar os dados na sessão do Streamlit
if "ressarcimentos" not in st.session_state:
    st.session_state["ressarcimentos"] = carregar_dados()

# Interface do Streamlit
st.image("logo.png", width=200)
st.title("📊 Dashboard de Ressarcimentos")
st.markdown("Gerencie e visualize seus ressarcimentos de forma profissional!")

# Criar inputs para os dados
data = st.date_input("**Data do ressarcimento**", value=datetime.today())
id_clube = st.text_input("**ID do Clube**", value="")
nome_clube = st.text_input("**Nome do Clube**", value="")
valor = st.text_input("**Valor do Ressarcimento**", value="")
responsavel = st.text_input("**Responsável**", value="")

# Botão para adicionar o ressarcimento
if st.button("**Adicionar Ressarcimento**"):
    if id_clube and nome_clube and valor and responsavel:
        try:
            valor_float = float(valor.replace("R$", "").replace(",", ".").strip())
            novo_dado = pd.DataFrame([[data, id_clube, nome_clube, valor_float, responsavel]], 
                                     columns=["DATA", "ID CLUBE", "NOME DO CLUBE", "VALOR", "RESPONSÁVEL"])
            st.session_state["ressarcimentos"] = pd.concat([st.session_state["ressarcimentos"], novo_dado], ignore_index=True)
            salvar_dados(st.session_state["ressarcimentos"])
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

# Botão para excluir um ressarcimento específico
if not st.session_state["ressarcimentos"].empty:
    excluir_index = st.number_input("Digite o índice do ressarcimento para excluir", min_value=0, max_value=len(st.session_state["ressarcimentos"])-1, step=1)
    if st.button("**Excluir Ressarcimento**"):
        st.session_state["ressarcimentos"] = st.session_state["ressarcimentos"].drop(excluir_index).reset_index(drop=True)
        salvar_dados(st.session_state["ressarcimentos"])
        st.success("Ressarcimento excluído com sucesso!")
        st.rerun()
