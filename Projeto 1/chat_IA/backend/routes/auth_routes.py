from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import mysql.connector
from db import get_connection

auth_bp = Blueprint('auth', __name__)

# Rota de Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT idusuario, nome, email, senha FROM usuario WHERE email = %s AND senha = %s", (email, senha))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if usuario:
        # Criar token JWT para autenticação
        token = create_access_token(identity=str(usuario['idusuario']))
        return jsonify({'message': 'Login bem-sucedido!', 'token': token, 'usuario': usuario}), 200
    else:
        return jsonify({'message': 'Credenciais inválidas'}), 401

# Rota de Cadastro
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
        conn.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201
    except mysql.connector.Error as err:
        return jsonify({'message': 'Erro ao cadastrar usuário', 'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
