import mysql.connector

# Configuração do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sua senha aqui',
    'database': 'chat_ia_db'
}

# Criar conexão com o banco
def get_connection():
    return mysql.connector.connect(**db_config)
