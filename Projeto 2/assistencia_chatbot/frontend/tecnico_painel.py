import streamlit as st

def interface_tecnico(usuario):
    st.title("👨‍🔧 Painel do Técnico")
    st.info(f"Você está logado como **{usuario['nome']}** (técnico).")

    opcao = st.radio("Escolha o que deseja acessar:", ["Chat com o bot", "Ver agenda"])

    if opcao == "Chat com o bot":
        st.write("Área de chat do técnico (em breve)...")
    elif opcao == "Ver agenda":
        st.write("Agenda de atendimentos (em breve)...")
