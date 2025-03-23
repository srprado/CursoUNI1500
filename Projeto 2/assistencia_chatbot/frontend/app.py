import streamlit as st
from utils import autenticar_usuario
from cliente_chat import interface_cliente
from tecnico_painel import interface_tecnico

st.set_page_config(page_title="Assistência XYZ", layout="centered")

if "usuario" not in st.session_state:
    st.title("🔧 Assistência Técnica - XYZ Tech Solutions")

    st.session_state.usuario = None

if st.session_state.usuario is None:
    with st.form("login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            usuario = autenticar_usuario(email, senha)
            if usuario:
                st.session_state.usuario = usuario
                st.success(f"Bem-vindo, {usuario['nome']}! Redirecionando...")
                st.rerun()
            else:
                st.error("Email ou senha inválidos.")
else:
    usuario = st.session_state.usuario
    if usuario["tipo"] == "cliente":
        interface_cliente(usuario)
    elif usuario["tipo"] == "tecnico":
        interface_tecnico(usuario)
