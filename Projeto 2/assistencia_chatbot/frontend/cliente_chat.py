import streamlit as st
import requests

API_URL = "http://localhost:5000"  # backend Flask rodando localmente

def interface_cliente(usuario):
    st.markdown("""
        <style>
            html, body, .main {
                height: 100vh;
                overflow: hidden;
                padding: 0;
                margin: 0;
            }
            .chat-container {
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            .chat-header {
                height: 50px;
                flex-shrink: 0;
                background-color: #fff;
                border-bottom: 1px solid #ddd;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 1.5rem;
                font-size: 14px;
            }
            .chat-body {
                flex: 1;
                overflow-y: auto;
                padding: 1rem 2rem;
                background-color: #f9f9f9;
            }
            .chat-footer {
                height: 70px;
                flex-shrink: 0;
                background-color: white;
                border-top: 1px solid #ddd;
                display: flex;
                align-items: center;
                padding: 0 1.5rem;
            }
            .mensagem {
                padding: 0.8rem 1rem;
                margin: 0.5rem 0;
                border-radius: 10px;
                max-width: 70%;
                word-wrap: break-word;
                font-size: 1rem;
            }
            .cliente {
                background-color: #d1e7dd;
                align-self: flex-end;
                text-align: right;
                margin-left: auto;
            }
            .bot {
                background-color: #e2e3e5;
                align-self: flex-start;
                text-align: left;
                margin-right: auto;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='chat-header'>
            <div><b>💬 Assistente Técnico Virtual</b></div>
            <div>{usuario['nome']} | <button onclick="window.location.reload()">Sair</button></div>
        </div>
    """, unsafe_allow_html=True)

    if "chat_cliente" not in st.session_state:
        st.session_state.chat_cliente = []

    if "mostrar_agendar" not in st.session_state:
        st.session_state.mostrar_agendar = False

    st.markdown("<div class='chat-body'>", unsafe_allow_html=True)
    for remetente, mensagem in st.session_state.chat_cliente:
        estilo = "cliente" if remetente == "cliente" else "bot"
        st.markdown(f"<div class='mensagem {estilo}'>{mensagem}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 🔘 Botão para agendar visita
    if st.session_state.mostrar_agendar:
        st.warning("Problema não resolvido? Agende uma visita técnica.")
        if st.button("📅 Agendar visita técnica"):
            response = requests.get(f"{API_URL}/tecnicos")
            if response.status_code == 200:
                tecnicos = response.json()
                nomes = [f"{t['nome']} - {t['especialidade']}" for t in tecnicos]
                escolha = st.selectbox("Escolha um técnico", nomes, index=0)
                selecionado = tecnicos[nomes.index(escolha)]

                if st.button("Confirmar agendamento"):
                    dados = {
                        "cliente": usuario["nome"],
                        "tecnico_id": selecionado["id"]
                    }
                    r = requests.post(f"{API_URL}/agendamento", json=dados)
                    if r.status_code == 200:
                        agendamento = r.json()
                        st.success(f"✅ Visita agendada com {agendamento['tecnico']} em {agendamento['data']}")
                        st.session_state.mostrar_agendar = False
                    else:
                        st.error("Erro ao agendar.")
            else:
                st.error("Erro ao buscar técnicos.")

    # ÁREA DE INPUT
    st.markdown("<div class='chat-footer'>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([10, 1])
        with col1:
            pergunta = st.text_input("", placeholder="Digite sua mensagem...", key="pergunta_input")
        with col2:
            enviar = st.form_submit_button("Enviar")

        if enviar and pergunta.strip():
            st.session_state.chat_cliente.append(("cliente", pergunta))
            st.session_state.ultima_pergunta = pergunta  # salvar para responder depois do rerun
            st.rerun()

    if "ultima_pergunta" in st.session_state:
        nova = st.session_state.ultima_pergunta
        try:
            r = requests.post(f"{API_URL}/chat", json={"pergunta": nova})
            if r.status_code == 200:
                data = r.json()
                resposta = data["resposta"]
                st.session_state.mostrar_agendar = data["mostrar_agendamento"]
                st.session_state.chat_cliente.append(("bot", resposta))
            else:
                st.session_state.chat_cliente.append(("bot", "Erro ao obter resposta da API."))
        except:
            st.session_state.chat_cliente.append(("bot", "Erro ao enviar pergunta."))

        del st.session_state["ultima_pergunta"]  # garantir que só processa 1x
        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

