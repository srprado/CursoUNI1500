import streamlit as st
from auth import login
from chat import chat_page
from sidebar import menu_lateral

# Configurar título da página
st.set_page_config(page_title="Chat IA", layout="wide")

# 🔹 Criar um botão de logout no canto superior direito
st.markdown(
    """
    <style>
    .logout-button {
        position: absolute;
        top: 15px;
        right: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🔹 Exibir o botão de logout apenas se o usuário estiver logado
if "token" in st.session_state:
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🚪 Sair", key="logout"):
            st.session_state.pop("token", None)  # Remover token
            st.session_state.pop("usuario", None)  # Remover dados do usuário
            st.session_state.pop("chat_id", None)  # Remover chat selecionado
            st.session_state.pop("mensagens", None)  # Limpar histórico de mensagens
            st.rerun()  # Redirecionar para a tela de login

# Tela de login
if "token" not in st.session_state:
    st.title("🔑 Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        resultado = login(email, senha)
        if resultado:
            st.session_state["token"] = resultado["token"]
            st.session_state["usuario"] = resultado["usuario"]
            st.rerun()

        else:
            st.error("Login inválido!")

# Exibir menu lateral e chat
else:
    menu_lateral()
    chat_page()
