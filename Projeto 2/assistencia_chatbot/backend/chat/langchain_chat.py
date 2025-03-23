from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Caminho para os arquivos de embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
faiss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../embeddings/faiss_index"))
vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

# LLM
chat = ChatOpenAI(temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))

def responder_ao_cliente(pergunta: str):
    try:
        if not pergunta.strip() or len(pergunta.strip()) < 4:
            return "Olá! Como posso ajudar você com sua impressora hoje?", False

        # Inicializa componentes
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        faiss_path = os.path.abspath("embeddings/faiss_index")
        vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
        chat = ChatOpenAI(temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))

        # Busca no FAISS
        docs = vectorstore.similarity_search(pergunta, k=3)
        contexto = "\n\n".join([doc.page_content for doc in docs])

        # Prompt inteligente
        prompt = f"""
Você é um assistente técnico de impressoras industriais da empresa XYZ Tech Solutions.

Antes de responder, avalie se a pergunta do cliente tem conteúdo técnico. Se for apenas um cumprimento ou algo genérico, cumprimente de volta e pergunte como pode ajudar. Se for uma pergunta técnica, use o contexto abaixo para responder.

### CONTEXTO:
{contexto}

### PERGUNTA:
{pergunta}

### RESPOSTA:
"""

        resposta = chat.predict(prompt)

        # Checagem se é caso de agendamento
        palavras_chave = ["visita técnica", "encaminhar técnico", "agendamento", "técnico irá até o local"]
        mostrar_agendamento = any(p in resposta.lower() for p in palavras_chave)

        return resposta, mostrar_agendamento

    except Exception as e:
        print("Erro:", e)
        return "Erro ao processar a resposta. Tente novamente em instantes.", False



def resposta_necessita_agendamento(resposta: str) -> bool:
    """Verifica se a resposta indica necessidade de agendamento"""
    padroes = [
        "agendar visita",
        "encaminhar para técnico",
        "não foi possível resolver",
        "um técnico especializado",
        "visita presencial",
        "será necessário enviar um técnico",
    ]
    resposta_lower = resposta.lower()
    return any(p in resposta_lower for p in padroes)

def processar_pergunta(pergunta: str):
    resposta = responder_ao_cliente(pergunta)
    mostrar_agendamento = resposta_necessita_agendamento(resposta)
    return {
        "resposta": resposta,
        "mostrar_agendamento": mostrar_agendamento
    }
