import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def autenticar_usuario(email, senha):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
    cursor.execute(query, (email, senha))
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()
    return usuario
