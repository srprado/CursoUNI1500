import os
import mysql.connector
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# Carregar variáveis do .env
load_dotenv()

# Conectar ao banco de dados
conexao = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conexao.cursor(dictionary=True)

# Buscar dados da tabela problemas_tecnicos
cursor.execute("SELECT id, modelo, titulo, causa, procedimento FROM problemas_tecnicos")
problemas = cursor.fetchall()

# Criar os documentos para embedding
documentos = []
for p in problemas:
    conteudo = f"Modelo: {p['modelo']}\nProblema: {p['titulo']}\nCausa: {p['causa']}\nProcedimento: {p['procedimento']}"
    documentos.append(Document(page_content=conteudo, metadata={"id": p['id']}))

# Gerar os embeddings com OpenAI
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Criar banco vetorial FAISS local
vectorstore = FAISS.from_documents(documentos, embedding)

# Salvar localmente
vectorstore.save_local("embeddings/faiss_index")

print("✅ Banco vetorial criado e salvo em 'embeddings/faiss_index'")
