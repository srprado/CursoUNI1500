import mysql.connector
from openai import OpenAI
from dotenv import load_dotenv
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import get_connection

#Carregar a chave da OpenAI do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

#Função para gerar embeddings
def gerar_embeddings_fazenda(texto):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texto
    )
    return response.data[0].embedding #retorna a lista de valores numéricos 

#conectar ao banco de dados
conn = get_connection()
cursor = conn.cursor(dictionary=True)

try:
    #Buscar todas as fazendas
    cursor.execute("SELECT idfazenda, nome FROM fazenda WHERE embedding IS NULL")
    fazendas = cursor.fetchall()

    for fazenda in fazendas:
        nome_fazenda = fazenda["nome"]
        embedding = gerar_embeddings_fazenda(nome_fazenda)

        #Atualizar a fazenda com o embedding gerado
        cursor.execute("UPDATE fazenda SET embedding = %s WHERE idfazenda = %s",
                       (json.dumps(embedding), fazenda["idfazenda"]))
        
        #Confirmar mudanças
        conn.commit()
        print("Embeddings das fazendas gerados.")

except Exception as e:
    conn.rollback()
    print(f"Erro ao gerar embeddings: {e}")

finally:
    cursor.close()
    conn.close()
    