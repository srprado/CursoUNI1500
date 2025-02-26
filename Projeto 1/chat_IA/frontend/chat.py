import requests
import streamlit as st
from sidebar import menu_lateral
from auth import API_URL

# Função para enviar mensagem ao backend
def enviar_mensagem(token, chat_id, mensagem):
    headers = {"Authorization": f"Bearer {token}"}
    url = "http://127.0.0.1:5000/mensagem/mensagens"
    data = {"idchat": chat_id, "conteudo": mensagem}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        return response.json()["resposta"]  # Retorna a resposta da LLM
    return "Erro ao obter resposta."

# 🔹 Função para carregar mensagens do banco de dados
def carregar_mensagens(token, chat_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"http://127.0.0.1:5000/mensagem/mensagens/{chat_id}", headers=headers)

    if response.status_code == 200:
        return response.json().get("mensagens", [])
    else:
        st.error(f"Erro ao carregar mensagens (Código {response.status_code}): {response.text}")
        return []

# 🔹 Página principal do chat
def chat_page():
    if "token" not in st.session_state:
        st.warning("Você precisa fazer login para acessar o chat!")
        st.stop()

    token = st.session_state["token"]
    chat_id = st.session_state.get("chat_id", None)

    if not chat_id:
        st.info("Selecione ou crie um chat no menu lateral.")
        st.stop()

    # 🔹 Carregar mensagens apenas se o chat for trocado
    if "last_chat_id" not in st.session_state or st.session_state["last_chat_id"] != chat_id:
        st.session_state["mensagens"] = carregar_mensagens(token, chat_id)
        st.session_state["last_chat_id"] = chat_id

    # 🔹 Exibir histórico do chat
    st.subheader(f"Chat {chat_id}")

    if not st.session_state["mensagens"]:
        st.info("Nenhuma mensagem neste chat ainda.")

    for msg in st.session_state["mensagens"]:
        with st.chat_message("usuario" if msg["origem"] == "usuario" else "LLM"):
            st.write(msg["conteudo"])

    # Entrada de texto para enviar novas mensagens
    mensagem = st.chat_input("Digite sua mensagem...")

    if mensagem:
        st.session_state["mensagens"].append({"origem": "usuario", "conteudo": mensagem})
        with st.chat_message("usuario"):
            st.write(mensagem)

        resposta = enviar_mensagem(token, chat_id, mensagem)

        st.session_state["mensagens"].append({"origem": "LLM", "conteudo": resposta})
        with st.chat_message("LLM"):
            st.write(resposta)

# 🔹 Função para enviar mensagem ao backend
def enviar_mensagem(token, chat_id, mensagem):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"idchat": chat_id, "conteudo": mensagem}
    response = requests.post(f"{API_URL}/mensagem/mensagens", json=data, headers=headers)

    if response.status_code == 201:
        return response.json().get("resposta", "Erro ao obter resposta da LLM.")
    return f"Erro ao enviar mensagem: {response.text}"