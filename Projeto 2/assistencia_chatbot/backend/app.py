from flask import Flask, request, jsonify
from chat.langchain_chat import responder_ao_cliente
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agendamento.controller import agendamento_bp

load_dotenv(dotenv_path="../.env")

app = Flask(__name__)
CORS(app)  # Permite acesso do frontend
app.register_blueprint(agendamento_bp)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pergunta = data.get("pergunta")

    if not pergunta:
        return jsonify({"erro": "Pergunta não enviada"}), 400

    resposta, agendar = responder_ao_cliente(pergunta)
    return jsonify({
        "resposta": resposta,
        "mostrar_agendamento": agendar
    })

if __name__ == "__main__":
    app.run(debug=True)
