from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from openai import OpenAI
import os
from dotenv import load_dotenv
from db import get_connection
import re

mensagem_bp = Blueprint('mensagem', __name__)

# ✅ Carregar a chave da OpenAI do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
OPENAI_MODEL = "gpt-4o"

client = OpenAI(api_key=OPENAI_API_KEY)

def obter_dados_do_banco():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 🔗 Consulta completa unindo todas as tabelas
        sql = """
        SELECT 
            f.idfazenda, f.nome AS fazenda_nome, f.municipio, f.estado,
            a.idanimal_inseminado, a.numero_animal, a.lote, a.raca AS raca_animal, a.categoria, a.ECC, a.ciclicidade,
            i.idinseminacao, i.protocolo, i.touro, i.raca_touro, i.empresa_touro, i.inseminador, 
            i.numero_IATF, i.DG, i.vazia_com_ou_sem_CL, i.perda
        FROM fazenda f
        JOIN animal_inseminado a ON f.idfazenda = a.idfazenda
        JOIN inseminacao i ON a.idanimal_inseminado = i.idanimal_inseminado
        """

        print(f"📌 CONSULTA SQL: {sql}")  # 👀 Ver consulta
        cursor.execute(sql)
        registros = cursor.fetchall()

        # 🔍 Formatando os dados para o prompt
        dados_formatados = "\n\n".join([
            f"🏡 **Fazenda:** {r['fazenda_nome']} ({r['municipio']}, {r['estado']})\n"
            f"🐂 Animal: {r['numero_animal']} (Lote: {r['lote']}, Raça: {r['raca_animal']}, ECC: {r['ECC']})\n"
            f"🧬 Protocolo: {r['protocolo']} (Touro: {r['touro']}, Raça do Touro: {r['raca_touro']}, Empresa: {r['empresa_touro']})\n"
            f"Inseminador: {r['inseminador']}, Nº IATF: {r['numero_IATF']}, DG: {r['DG']}, Perda: {r['perda']}"
            for r in registros
        ])

        return dados_formatados        

    except Exception as e:
        print("❌ ERRO AO BUSCAR DADOS DO BANCO:", str(e))
        return "Não foi possível acessar os dados do banco."

    finally:
        cursor.close()
        conn.close()

# ---------------------------
# ✅ Função para obter histórico do chat do usuário
# ---------------------------
def obter_historico(chat_id, usuario_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT conteudo, origem FROM mensagem 
            WHERE idchat = %s AND idusuario = %s
            ORDER BY enviado_em ASC
        """, (chat_id, usuario_id))
        mensagens = cursor.fetchall()

        # Formatar o histórico para o prompt da LLM
        historico_formatado = "\n".join([
            f"{'Usuário' if msg['origem'] == 'usuario' else 'LLM'}: {msg['conteudo']}"
            for msg in mensagens
        ])

        return historico_formatado

    except Exception as e:
        print("❌ ERRO AO BUSCAR HISTÓRICO:", str(e))
        return ""

    finally:
        cursor.close()
        conn.close()

# ---------------------------
# ✅ Enviar mensagem e obter resposta da OpenAI
# ---------------------------
@mensagem_bp.route('/mensagens', methods=['POST'])
@jwt_required()
def enviar_mensagem():
    usuario_id = get_jwt_identity()
    data = request.json
    chat_id = data.get('idchat')
    conteudo = data.get('conteudo')

    if not conteudo or not chat_id:
        return jsonify({'message': 'Chat ID e conteúdo são obrigatórios'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1️⃣ Salvar a mensagem do usuário no banco
        cursor.execute("INSERT INTO mensagem (conteudo, origem, enviado_em, idusuario, idchat) VALUES (%s, 'usuario', NOW(), %s, %s)",
                       (conteudo, usuario_id, chat_id))
        conn.commit()

        # 2️⃣ Obter histórico do chat
        historico = obter_historico(chat_id, usuario_id)

        # 3️⃣ Obter informações do banco de TODAS AS TABELAS
        dados_banco = obter_dados_do_banco()

        # 4️⃣ Enviar a mensagem para a OpenAI
        resposta_llm = obter_resposta_da_llm(conteudo, historico, dados_banco)

        # 5️⃣ Salvar a resposta da OpenAI no banco
        cursor.execute("INSERT INTO mensagem (conteudo, origem, enviado_em, idusuario, idchat) VALUES (%s, 'LLM', NOW(), %s, %s)",
                       (resposta_llm, usuario_id, chat_id))
        conn.commit()

        return jsonify({'message': 'Mensagem enviada!', 'resposta': resposta_llm}), 201

    except Exception as e:
        conn.rollback()
        print("❌ ERRO NO BACKEND:", str(e))
        return jsonify({'message': 'Erro ao processar mensagem', 'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ---------------------------
# ✅ Função extrair SQL da resposta da IA (OpenAI)
# ---------------------------
def extrair_sql(texto):
    padrao = r"SELECT .*? FROM .*?(?: WHERE .*?)?(?: GROUP BY .*?)?(?: ORDER BY .*?)?"
    correspondencias = re.findall(padrao, texto, re.DOTALL | re.IGNORECASE)

    if correspondencias:
        return correspondencias[0]  # Retorna a primeira consulta SQL encontrada
    return None

# ---------------------------
# ✅ Função executar SQL extraida da resposta da IA (OpenAI)
# ---------------------------
def executar_consulta_sql(sql_query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        print(f"📌 EXECUTANDO CONSULTA SQL: {sql_query}")  # Debug
        cursor.execute(sql_query)
        resultados = cursor.fetchall()

        if not resultados:
            return "Nenhum dado encontrado."

        return "\n".join([str(linha) for linha in resultados])

    except Exception as e:
        print("❌ ERRO NA CONSULTA SQL:", str(e))
        return "Erro ao executar a consulta SQL."

    finally:
        cursor.close()
        conn.close()

# ---------------------------
# ✅ Função para chamar a API do ChatGPT (OpenAI)
# ---------------------------
def obter_resposta_da_llm(mensagem_usuario, historico, dados_banco):
    try:
        prompt = f"""
        Você é um assistente especializado em análise de protocolos de inseminação bovina.
        Você pode consultar o banco de dados e responder perguntas baseadas nas informações armazenadas.

        **Estrutura do banco de dados:**
        - Tabela `fazenda`: contém as fazendas cadastradas, incluindo `idfazenda`, `nome`, `municipio`, `estado`.
        - Tabela `animal_inseminado`: contém os animais inseminados, incluindo `idanimal_inseminado`, `numero_animal`, `lote`, `raca`, `categoria`, `ECC`, `ciclicidade`, `idfazenda`.
        - Tabela `inseminacao`: contém os detalhes da inseminação, incluindo `idinseminacao`, `protocolo`, `touro`, `raca_touro`, `empresa_touro`, `inseminador`, `numero_IATF`, `DG`, `vazia_com_ou_sem_CL`, `perda`, `idanimal_inseminado`.

        **Histórico da conversa:**
        {historico}

        **Dados disponíveis:**
        {dados_banco}

        Se necessário, você pode gerar uma consulta SQL para obter informações mais detalhadas.
        """

        # print("📌 PROMPT ENVIADO PARA A OPENAI:", prompt)  # 👀 Ver prompt enviado

        resposta = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensagem_usuario}
            ]
        )

        resposta_texto = resposta.choices[0].message.content
        # print("✅ RESPOSTA DA OPENAI:", resposta_texto)

        # 🛠 Verificar se a resposta contém um SQL gerado
        if "SELECT" in resposta_texto and "FROM" in resposta_texto:
            sql_query = extrair_sql(resposta_texto)
            resultado_sql = executar_consulta_sql(sql_query)
            return f"Resultado da consulta:\n{resultado_sql}"
        
        return resposta_texto

    except Exception as e:
        print("❌ ERRO NA OPENAI:", str(e))
        return f"Erro ao conectar com a LLM (OpenAI): {str(e)}"

# ---------------------------
# ✅ Listar mensagens de um chat específico
# ---------------------------
@mensagem_bp.route('/mensagens/<int:chat_id>', methods=['GET'])
@jwt_required()
def listar_mensagens(chat_id):
    usuario_id = get_jwt_identity()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT conteudo, origem, enviado_em FROM mensagem WHERE idchat = %s AND idusuario = %s ORDER BY enviado_em ASC",
            (chat_id, usuario_id)
        )
        mensagens = cursor.fetchall()

        return jsonify({'mensagens': mensagens}), 200

    except Exception as e:
        print("❌ ERRO AO RECUPERAR MENSAGENS:", str(e))
        return jsonify({'message': 'Erro ao recuperar mensagens', 'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()
