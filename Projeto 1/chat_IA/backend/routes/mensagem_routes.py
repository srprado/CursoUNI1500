# OPENAI
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from openai import OpenAI
import os
from dotenv import load_dotenv
from db import get_connection
import re
import numpy as np

mensagem_bp = Blueprint('mensagem', __name__)

# ✅ Carregar a chave da OpenAI do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
OPENAI_MODEL = "gpt-4o"
#ou 4o-mini

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Embeddings da mensagem do usuário
def gerar_embedding(texto):
    """ Gera um embedding para um texto usando OpenAI """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=texto
        )
        return response.data[0].embedding  # Retorna a lista de embeddings
    
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None

# ✅ Função para obter o nome de fazenda mais similar ao digitado pelo usuário
def encontrar_fazenda_similar(nome_fazenda_digitado):
    """
    Encontra a fazenda mais similar ao nome digitado pelo usuário usando embeddings armazenados no banco.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Gerar embedding para o nome digitado pelo usuário
        embedding_usuario = gerar_embedding(nome_fazenda_digitado)
        if embedding_usuario is None:
            return None
        
        # Buscar todas as fazendas e seus embeddings no banco
        cursor.execute("SELECT idfazenda, nome, embedding FROM fazenda")
        fazendas = cursor.fetchall()

        # Converter embeddings do banco para arrays NumPy e calcular a similaridade
        melhor_fazenda = None
        maior_similaridade = -1

        for fazenda in fazendas:
            if fazenda["embedding"]:
                embedding_fazenda = np.array(eval(fazenda["embedding"]))  # Converter string para array NumPy
                similaridade = np.dot(embedding_usuario, embedding_fazenda) / (
                    np.linalg.norm(embedding_usuario) * np.linalg.norm(embedding_fazenda)
                )

                if similaridade > maior_similaridade:
                    melhor_fazenda = fazenda
                    maior_similaridade = similaridade
        
        # Retorna a fazenda mais similar, se a similaridade for alta o suficiente
        if melhor_fazenda and maior_similaridade > 0.80:
            return melhor_fazenda
        
        return None  # Nenhuma fazenda identificada com precisão suficiente

    except Exception as e:
        print(f"Erro ao encontrar fazenda similar: {e}")
        return None
    
    finally:
        cursor.close()
        conn.close()

# ✅ Função para obter dados do banco de dados
def obter_dados_do_banco(mensagem_usuario):
    """
    Obtém dados do banco dependendo do tipo de pergunta do usuário:
    - Se a pergunta mencionar fazenda, busca a fazenda correta e seus dados.
    - Se não mencionar fazenda, busca normalmente todas as informações do banco.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        fazenda_identificada = encontrar_fazenda_similar(mensagem_usuario)

        if fazenda_identificada:
            id_fazenda = fazenda_identificada["idfazenda"]
            nome_fazenda = fazenda_identificada["nome"]

            sql = """
            SELECT 
                f.idfazenda, f.nome AS fazenda_nome, f.municipio, f.estado,
                a.idanimal_inseminado, a.numero_animal, a.lote, a.raca AS raca_animal, a.categoria, a.ECC, a.ciclicidade,
                i.idinseminacao, i.protocolo, i.implante_p4, i.empresa, i.gnrh_na_IA, i.pgf_no_d0, i.dose_pgf_retirada, i.marca_pgf_retirada, 
                i.dose_ce, i.ECG, i.dose_ecg, i.touro, i.raca_touro, i.empresa_touro, i.inseminador, i.numero_IATF, i.DG, 
                i.vazia_com_ou_sem_CL, i.perda
            FROM fazenda f
            JOIN animal_inseminado a ON f.idfazenda = a.idfazenda
            JOIN inseminacao i ON a.idanimal_inseminado = i.idanimal_inseminado
            WHERE f.idfazenda = %s
            """

            # print(f"📌 CONSULTA SQL: {sql} - Parâmetro: {id_fazenda}")  #Print no terminal
            cursor.execute(sql, (id_fazenda,))
        
        else:
            # Caso a pergunta NÃO mencione fazenda, pega TODOS os dados sem filtro específico
            sql = """
            SELECT 
                f.idfazenda, f.nome AS fazenda_nome, f.municipio, f.estado,
                a.idanimal_inseminado, a.numero_animal, a.lote, a.raca AS raca_animal, a.categoria, a.ECC, a.ciclicidade,
                i.idinseminacao, i.protocolo, i.implante_p4, i.empresa, i.gnrh_na_IA, i.pgf_no_d0, i.dose_pgf_retirada, i.marca_pgf_retirada, 
                i.dose_ce, i.ECG, i.dose_ecg, i.touro, i.raca_touro, i.empresa_touro, i.inseminador, i.numero_IATF, i.DG, 
                i.vazia_com_ou_sem_CL, i.perda
            FROM fazenda f
            JOIN animal_inseminado a ON f.idfazenda = a.idfazenda
            JOIN inseminacao i ON a.idanimal_inseminado = i.idanimal_inseminado
            """
            # print(f"📌 CONSULTA SQL: {sql}")
            cursor.execute(sql)

        registros = cursor.fetchall()

        if not registros:
            return "Nenhum dado encontrado no banco."

        # 🔹 Formatar os dados para exibição
        dados_formatados = "\n\n".join([
            f"🏡 **Fazenda:** {r['fazenda_nome']} ({r['municipio']}, {r['estado']})\n"
            f"🐂 Animal Inseminado: {r['numero_animal']} (Lote: {r['lote']}, Raça: {r['raca_animal']}, Categoria: {r["categoria"]}, ECC: {r['ECC']}, Ciclicidade: {r['ciclicidade']})\n"
            f"🧬 Protocolo: {r['protocolo']} | Implante P4: {r['implante_p4']} | Empresa: {r['empresa']}\n"
            f"GnRH na IA: {r['gnrh_na_IA']} | PGF no D0: {r['pgf_no_d0']} | Dose PGF Retirada: {r['dose_pgf_retirada']} | Marca PGF: {r['marca_pgf_retirada']}\n"
            f"Dose CE: {r['dose_ce']} | ECG: {r['ECG']} | Dose ECG: {r['dose_ecg']}\n"
            f"Touro: {r['touro']} (Raça: {r['raca_touro']}, Empresa: {r['empresa_touro']})\n"
            f"Inseminador: {r['inseminador']} | Nº IATF: {r['numero_IATF']} | DG: {r['DG']} | Vazia com/s CL: {r['vazia_com_ou_sem_CL']} | Perda: {r['perda']}"
            for r in registros
        ])

        return dados_formatados

    except Exception as e:
        print(f"❌ ERRO AO BUSCAR DADOS DO BANCO: {e}")
        return "Erro ao acessar os dados do banco."

    finally:
        cursor.close()
        conn.close()

# ✅ Função para obter histórico do chat do usuário
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

# ✅ Enviar mensagem e obter resposta da OpenAI
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
        dados_banco = obter_dados_do_banco(conteudo)

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

# ✅ Função extrair SQL da resposta da IA (OpenAI)
def extrair_sql(texto):
    padrao = r"SELECT .*? FROM .*?(?: WHERE .*?)?(?: GROUP BY .*?)?(?: ORDER BY .*?)?"
    correspondencias = re.findall(padrao, texto, re.DOTALL | re.IGNORECASE)

    if correspondencias:
        return correspondencias[0]  # Retorna a primeira consulta SQL encontrada
    return None

# ✅ Função executar SQL extraida da resposta da IA (OpenAI)
def executar_consulta_sql(sql_query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        print(f"EXECUTANDO CONSULTA SQL: {sql_query}")  # Debug
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

# ✅ Função para chamar a API do ChatGPT (OpenAI)
def obter_resposta_da_llm(mensagem_usuario, historico, dados_banco):
    try:
        prompt = f"""
        Você é um assistente especializado em análise de protocolos de inseminação bovina.
        Você pode consultar o banco de dados e responder perguntas baseadas nas informações armazenadas.

        **IMPORTANTE: ** Responda de modo objetivo. Não retorne ao usuário dados repetidos.
        **INFORMAÇÃO:**Um animal fica prenha quando DG=1 e perda=0, isto indica que o animal ficou prenha e não houve perda gestacional.

        **Estrutura do banco de dados:**
        - Tabela `fazenda`: contém as fazendas cadastradas (`idfazenda`, `nome`, `municipio`, `estado`).
        - Tabela `animal_inseminado`: contém os animais inseminados (`idanimal_inseminado`, `numero_animal`, `lote`, `raca`, `categoria`, `ECC`, `ciclicidade`, `idfazenda`).
        - Tabela `inseminacao`: contém os detalhes da inseminação (`idinseminacao`, `protocolo`, `implante_p4`, `empresa`, `gnrh_na_IA`, `pgf_no_d0`, `dose_pgf_retirada`, `marca_pgf_retirada`, `dose_ce`, `ECG`, `dose_ecg`, `touro`, `raca_touro`, `empresa_touro`, `inseminador`, `numero_IATF`, `DG`, `vazia_com_ou_sem_CL`, `perda`, `idanimal_inseminado`).
        
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

# ✅ Listar mensagens de um chat específico
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
