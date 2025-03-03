import requests
import streamlit as st
# from auth import API_URL 

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

# Estado temporário para armazenar qual chat está sendo editado
if "chat_editando" not in st.session_state:
    st.session_state["chat_editando"] = None

# Renomear um chat
def renomear_chat(chat_id, novo_nome, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{API_URL}/chats/{chat_id}", json={"titulo": novo_nome}, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        st.error("Erro ao renomear chat!")
        return False


# 🔹 Menu lateral para exibir os chats
def menu_lateral():
    st.sidebar.title("💬 Chats")

    # Garantir que o estado do chat_editando seja inicializado
    if "chat_editando" not in st.session_state:
        st.session_state["chat_editando"] = None

    token = st.session_state.get("token")
    if not token:
        st.sidebar.warning("Faça login para acessar os chats.")
        return

    # Carregar chats do usuário
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/chats", headers=headers)
    
    if response.status_code == 200:
        chats = response.json()["chats"]
    else:
        chats = []

    # 🔹 Botão fixo para criar um novo chat
    if st.sidebar.button("➕ Novo Chat", use_container_width=True):
        novo_chat = requests.post(f"{API_URL}/chats", headers=headers)
        if novo_chat.status_code == 201:
            st.session_state["chat_id"] = novo_chat.json()["chat_id"]
            st.rerun()

    st.sidebar.markdown("---")  # 🔹 Linha divisória para separar os chats

    # 🔹 Exibir lista de chats com nome, editar e excluir
    for chat in chats:
        chat_id = chat["idchat"]
        chat_titulo = chat["titulo"]

        # Identificar se é o chat selecionado
        is_selected = st.session_state.get("chat_id") == chat_id

        col1, col2, col3 = st.sidebar.columns([5, 1, 1])  # Ajuste de proporções

        # with col1:
        #     if st.session_state["chat_editando"] == chat["idchat"]:
        #         # 🔹 Campo de edição do nome do chat
        #         novo_nome = st.text_input("Novo nome", chat["titulo"], key=f"edit_{chat['idchat']}")
        #         if novo_nome and novo_nome != chat["titulo"]:
        #             if renomear_chat(chat["idchat"], novo_nome, token):
        #                 st.session_state["chat_editando"] = None
        #                 st.rerun()
        #     else:
        #         # 🔹 Nome do chat como botão clicável
        #         if st.button(chat["titulo"], key=f"chat_{chat['idchat']}", use_container_width=True, ):
        #             st.session_state["chat_id"] = chat["idchat"]
        #             st.rerun()    

        with col1:
            if st.session_state["chat_editando"] == chat["idchat"]:
                # Campo de edição do nome do chat
                novo_nome = st.text_input("Novo nome", chat["titulo"], key=f"edit_{chat['idchat']}")
                if novo_nome and novo_nome != chat["titulo"]:
                    if renomear_chat(chat["idchat"], novo_nome, token):
                        st.session_state["chat_editando"] = None
                        st.rerun()
            else:
                # Botão para selecionar o chat
                if st.button(
                    chat["titulo"],
                    key=f"chat_{chat['idchat']}",
                    help="Selecionar chat",
                    type="primary" if is_selected else "secondary",  # Destacar o botão ativo
                    use_container_width=True,
                ):
                    st.session_state["chat_id"] = chat["idchat"]
                    st.rerun()            

        with col2:
            # 🔹 Botão de edição
            if st.button("✏️", key=f"editar_{chat['idchat']}", help="Renomear chat"):
                st.session_state["chat_editando"] = None if st.session_state["chat_editando"] == chat["idchat"] else chat["idchat"]
                st.rerun()

        with col3:
            # 🔹 Botão de exclusão
            if st.button("❌", key=f"excluir_{chat['idchat']}", help="Excluir chat"):
                 if requests.delete(f"{API_URL}/chats/{chat['idchat']}", headers=headers).status_code == 200:
                    st.session_state["chat_editando"] = None  # Sai do modo de edição ao excluir
                    st.rerun()
                # if excluir_chat(chat["idchat"], token):
                #     st.session_state["chat_editando"] = None
                #     st.rerun()



# # Criar menu lateral com keys únicas para cada botão
# def menu_lateral():
#     st.sidebar.title("📌 Chats")
#     token = st.session_state.get("token", None)

#     if token:
#         # Botão Novo Chat fixado no topo
#         if st.sidebar.button("➕ Novo Chat", key="novo_chat"):
#             chat_id = criar_chat(token)
#             if chat_id:
#                 st.session_state["chat_id"] = chat_id
#                 st.rerun()

#         # st.sidebar.markdown("---")  # Linha divisória visual

#         # Exibir lista de chats com botão de exclusão "X"
#         chats = listar_chats(token)
#         for chat in chats:
#             col1, col2, col3 = st.sidebar.columns([4, 1, 1])

#             with col1:
#                 chat_nome = st.text_input(f"Nome do Chat {chat['idchat']}", chat["titulo"], key=f"chat_{chat['idchat']}")

#             with col2:
#                 if st.button("✏️", key=f"editar_{chat['idchat']}"):
#                     if renomear_chat(chat["idchat"], chat_nome, token):
#                         st.rerun()

#             with col3:
#                 if st.button("❌", key=f"excluir_{chat['idchat']}"):
#                     if requests.delete(f"{API_URL}/chats/{chat['idchat']}", headers=headers).status_code == 200:
#                         st.rerun()
