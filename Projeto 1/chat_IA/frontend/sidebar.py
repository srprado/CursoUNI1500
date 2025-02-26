import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000/chat"

# Listar chats
def listar_chats(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/chats", headers=headers)
    return response.json().get("chats", [])

# Criar chat
def criar_chat(token):
    headers = {"Authorization": f"Bearer {token}"}
    # data = {"titulo": "Novo Chat"}
    response = requests.post(f"{API_URL}/chats", headers=headers)

    if response.status_code == 201:
        return response.json()["chat_id"]
    return None

# Excluir chat
def excluir_chat(token, chat_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{API_URL}/chats/{chat_id}", headers=headers)
    return response.status_code == 200

# Criar menu lateral com keys únicas para cada botão
def menu_lateral():
    st.sidebar.title("📌 Chats")
    token = st.session_state.get("token", None)

    if token:
        # Botão Novo Chat fixado no topo
        if st.sidebar.button("➕ Novo Chat", key="novo_chat"):
            chat_id = criar_chat(token)
            if chat_id:
                st.session_state["chat_id"] = chat_id
                st.rerun()

        # st.sidebar.markdown("---")  # Linha divisória visual

        # Exibir lista de chats com botão de exclusão "X"
        chats = listar_chats(token)
        for chat in chats:
            col1, col2 = st.sidebar.columns([8, 2])  # Criar colunas para separar título e botão "X"
            
            with col1:
                if st.button(chat["titulo"], key=f"chat_{chat['idchat']}"):
                    st.session_state["chat_id"] = chat["idchat"]
                    st.rerun()
            
            with col2:
                if st.button("❌", key=f"del_{chat['idchat']}"):
                    excluir_chat(token, chat["idchat"])
                    if "chat_id" in st.session_state and st.session_state["chat_id"] == chat["idchat"]:
                        del st.session_state["chat_id"]
                    st.rerun()
