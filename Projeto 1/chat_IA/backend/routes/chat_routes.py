from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import mysql.connector
from db import get_connection

chat_bp = Blueprint('chat', __name__)

# Criar um novo chat
@chat_bp.route('/chats', methods=['POST'])
@jwt_required()
def criar_chat():
    usuario_id = get_jwt_identity()

    conn = get_connection()
    cursor = conn.cursor()

    # Inserir primeiro para obter o ID gerado
    cursor.execute("INSERT INTO chat (titulo, data_criacao, idusuario) VALUES (%s, NOW(), %s)", ("", usuario_id))
    conn.commit()
    chat_id = cursor.lastrowid  # Obtém o ID gerado

    # Atualiza o título do chat com o ID
    titulo = f"Chat {chat_id}"
    cursor.execute("UPDATE chat SET titulo = %s WHERE idchat = %s", (titulo, chat_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Chat criado com sucesso!', 'chat_id': chat_id, 'titulo': titulo}), 201

# Listar chats do usuário autenticado
@chat_bp.route('/chats', methods=['GET'])
@jwt_required()
def listar_chats():
    usuario_id = get_jwt_identity()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM chat WHERE idusuario = %s ORDER BY data_criacao DESC", (usuario_id,))
    chats = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'chats': chats}), 200

# Deletar um chat
@chat_bp.route('/chats/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def deletar_chat(chat_id):
    usuario_id = get_jwt_identity()

    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se o chat pertence ao usuário autenticado primeiramente
    cursor.execute("SELECT * FROM chat WHERE idchat = %s AND idusuario = %s", (chat_id, usuario_id))
    chat = cursor.fetchone()

    if not chat:
        return jsonify({'message': 'Chat não encontrado ou não pertence a você'}), 404

    cursor.execute("DELETE FROM mensagem WHERE idchat = %s", (chat_id,))  # Exclui mensagens do chat
    cursor.execute("DELETE FROM chat WHERE idchat = %s", (chat_id,))  # Exclui o chat
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Chat excluído com sucesso!'}), 200

# Atualizar nome do chat
@chat_bp.route('/chats/<int:chat_id>', methods=['PUT'])
@jwt_required()
def atualizar_chat(chat_id):
    usuario_id = get_jwt_identity()
    data = request.json
    novo_nome = data.get('titulo')

    if not novo_nome:
        return jsonify({"message": "Dê um nome ao chat!"}), 400
    
    conn = get_connection()
    cursor = conn.cursor()

    try:
        #Verificar se o chat pertence ao usuário
        cursor.execute("SELECT idchat FROM chat WHERE idchat = %s AND idusuario = %s", (chat_id, usuario_id))
        chat = cursor.fetchone()

        if not chat:
            return jsonify({"message": "Chat não encontrado ou não pertence ao usuário!"}), 404
        
        # Atualizar o nome do chat
        cursor.execute("UPDATE chat SET titulo = %s WHERE idchat = %s", (novo_nome, chat_id))
        conn.commit()

        return jsonify({"message": "Chat atualizado com sucesso!"}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Erro ao atualizar o chat", "error": str(e)}),500
    
    finally:
        cursor.close()
        conn.close()