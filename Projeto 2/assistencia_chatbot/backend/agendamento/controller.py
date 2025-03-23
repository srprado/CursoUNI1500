from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

agendamento_bp = Blueprint("agendamento", __name__)

# Técnicos mockados
tecnicos = [
    {"id": 1, "nome": "Roberto Silva", "especialidade": "Conexão e rede"},
    {"id": 2, "nome": "Fernanda Lima", "especialidade": "Mecânica e papel"},
    {"id": 3, "nome": "Carlos Mendes", "especialidade": "Falhas de impressão"}
]

# Simulação de agenda
agenda = []

# GET /tecnicos → retorna técnicos disponíveis
@agendamento_bp.route("/tecnicos", methods=["GET"])
def listar_tecnicos():
    return jsonify(tecnicos)

# POST /agendamento
@agendamento_bp.route("/agendamento", methods=["POST"])
def agendar_visita():
    data = request.get_json()
    cliente = data.get("cliente")
    tecnico_id = data.get("tecnico_id")

    if not cliente or not tecnico_id:
        return jsonify({"erro": "Dados incompletos"}), 400

    # Simula um horário automático: amanhã às 10h
    horario = datetime.now() + timedelta(days=1)
    horario_formatado = horario.strftime("%d/%m/%Y às %H:%M")

    agendamento = {
        "cliente": cliente,
        "tecnico_id": tecnico_id,
        "data_hora": horario_formatado
    }
    agenda.append(agendamento)

    # Recupera nome do técnico
    tecnico = next((t for t in tecnicos if t["id"] == tecnico_id), None)

    return jsonify({
        "mensagem": "Agendamento confirmado",
        "data": horario_formatado,
        "tecnico": tecnico["nome"] if tecnico else "Técnico não encontrado"
    })
