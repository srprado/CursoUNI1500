from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.mensagem_routes import mensagem_bp

app = Flask(__name__)
CORS(app)  # Permite acesso do frontend ao backend

# Configuração da chave secreta para autenticação JWT
app.config['SECRET_KEY'] = 'minha_chave_secreta_super_segura'
app.config['JWT_SECRET_KEY'] = 'chave_jwt_super_secreta'  # Adicione essa linha

# Inicializa o JWT Manager
jwt = JWTManager(app)  # Aqui está o que estava faltando

# Registrar os blueprints (módulos de rotas)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(mensagem_bp, url_prefix='/mensagem')


if __name__ == '__main__':
    app.run(debug=True)


# ESSE CÓDIGO CRIA E INICIA O SERVIDOR FLASK
