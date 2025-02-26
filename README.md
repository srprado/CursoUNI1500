# UNI1500 - Curso de Inteligência Artificial 
![Banner.](https://ravel.com.br/blog/wp-content/uploads/2023/04/IA-no-Cotidiano-Banner.jpg)

### 📋Projeto 1: 
Criar um chat integrado com LLM para melhorar as vendas sobre protocolos de inseminação. A planilha de dados foi apresentada e foi necessário entender os dados da planilha e preenchê-los com dados coerentes sobre protocolos de inseminação e os resulltados obtidos, a partir disso foi necessário criar o banco de dados, alimentar com os dados da planilha, criar a interface do chat, configurar front e backend e configurar a LMM para que ela consulte os dados e responda o usuário de forma correta e coerente com os dados e também manter o histórico das conversas.

**🛠️ Tecnologias Utilizadas**
**Backend**
- Linguagem: Python 3.10+
- Framework: Flask
- Banco de Dados: MySQLWorkbench
- Autenticação: JWT (Flask-JWT-Extended)
- LLM: OpenAI GPT-4o
- Gerenciamento de variáveis: Dotenv
- Gerenciador de pacotes: pip
  **Frontend**
- Linguagem: Python
- Framework: Streamlit
- Comunicação com Backend: Requests (API REST)
- Interface responsiva: Streamlit + CSS

## 🚀 Como executar o Projeto 1:
```
> No terminal ou git bash(onde o projeto vai ficar) execute:
1. git clone git@github.com:sabrinarprado/Curso-Uni1500.git
2. Abra no terminal o projeto(dentro da pasta "chat_IA")

> Se quiser rodar o backend de forma isolada, crie um ambiente virtual(se não, só pular):
1. python -m venv venv
2. source venv/bin/activate  # Linux/Mac
3. venv\Scripts\activate     # Windows

> Instalar as dependências do backend(verifique o arquivo antes e veja se quer instalar tudo mesmo)/ Para o frontend é o mesmo passo, porém abra o fronted e depois execute o pip install:
1. cd backend
2. pip install -r requirements.txt

> Crie um arquivo .env dentro da pasta backend com o seguinte conteúdo:
1. OPENAI_API_KEY=coloque-sua-chave aqui

> Configurar Banco de dados:
1. execute o script do banco para criar as tabelas do banco de dados(ignore os select)
2. No arquivo db.py no backend altere os dados necessários(host, user, password, database)

> Agora execute o projeto:
- backend: py app.py
- frontend: streamlit run app.py
```




