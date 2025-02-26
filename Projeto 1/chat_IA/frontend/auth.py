import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000"

# 🔹 Função para fazer login
def login(email, senha):
    url = f"{API_URL}/auth/login"  # 🔹 Corrigido para apontar para /auth/login
    data = {"email": email, "senha": senha}
    
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("Erro ao fazer login! Verifique seu email e senha.")
        return None

# 🔹 Função para registrar um novo usuário
def registrar_usuario(nome, email, senha):
    url = f"{API_URL}/auth/register"  # 🔹 Corrigido para apontar para /auth/register
    data = {"nome": nome, "email": email, "senha": senha}

    response = requests.post(url, json=data)

    if response.status_code == 201:
        st.success("Usuário registrado com sucesso! Agora você pode fazer login.")
    else:
        st.error("Erro ao registrar usuário.")
