import sqlite3
import re
from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SECRET_KEY = "fipe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tempo de expiração do token em minutos

def generate_token(user_id):
    expiration_date = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"user_id": user_id, "exp": expiration_date}
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return "Expirado"
    except jwt.InvalidTokenError:
        return "Invalido"

# Create tables if they do not exist
def init_db():
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS login_details2 (
                    USER_ID TEXT PRIMARY KEY,
                    PASSWORD TEXT NOT NULL,
                    NOME TEXT NOT NULL,
                    ESTADO TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites3 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    vehicle_url TEXT NOT NULL,
                    tipo_veiculo TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES login_details2 (USER_ID)
                )''')
    conn.commit()
    c.close()
    conn.close()

# Initialize the database
init_db()

# For conditions in user id for registration
def user_id_check_func(u):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, u))

# For conditions in password for registration
def password_check_func(p):
    pattern = r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[~`!@#$%^&*()_\-+={[}\]|\\:;"\'<,>.?/]).{8,}'
    return bool(re.match(pattern, p))

# For Registration
def register(user_id: str, password: str, nome: str, estado: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    if not user_id_check_func(user_id):
        return {"message": "Email inválido"}, 400

    if len(password) < 8 or len(password) > 15 or not password_check_func(password):
        return {"message": "Senha fraca"}, 400

    exist = c.execute("SELECT USER_ID FROM login_details2 WHERE USER_ID = ?", (user_id,)).fetchone()
    if exist:
        return {"message": "Usuário já registrado"}, 400

    c.execute("INSERT INTO login_details2 (USER_ID, PASSWORD, NOME, ESTADO) VALUES (?, ?, ?, ?)", (user_id, password, nome, estado))
    conn.commit()
    c.close()
    conn.close()
    return {"message": "Registro feito com sucesso"}

# For Login
def login(user_id: str, password: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    user = c.execute("SELECT * FROM login_details2 WHERE USER_ID = ?", (user_id,)).fetchone()
    if user and user[1] == password:
        jwt_token = generate_token(user_id)
        c.close()
        conn.close()
        return {"message": "Login feito com sucesso", "token": jwt_token}
    else:
        c.close()
        conn.close()
        return {"message": "Email ou senha incorretos"}, 401

# For adding a car model to favorites
def add_to_favorites(user_id: str, vehicle_url: str, tipo_veiculo: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    user = c.execute("SELECT USER_ID FROM login_details2 WHERE USER_ID = ?", (user_id,)).fetchone()
    if not user:
        return {"message": "Usuário não encontrado"}, 404

    existing_favorite = c.execute("SELECT * FROM favorites3 WHERE user_id = ? AND vehicle_url = ?", (user_id, vehicle_url)).fetchone()
    if existing_favorite:
        return {"message": "Veículo já está nos favoritos"}, 400

    c.execute("INSERT INTO favorites3 (user_id, vehicle_url, tipo_veiculo) VALUES (?, ?, ?)", (user_id, vehicle_url, tipo_veiculo))
    conn.commit()
    c.close()
    conn.close()
    return {"message": "Veículo adicionado aos favoritos"}

# For removing a car model from favorites
def remove_from_favorites(user_id: str, vehicle_url: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    user = c.execute("SELECT USER_ID FROM login_details2 WHERE USER_ID = ?", (user_id,)).fetchone()
    if not user:
        return {"message": "Usuário não encontrado"}, 404

    existing_favorite = c.execute("SELECT * FROM favorites3 WHERE user_id = ? AND vehicle_url = ?", (user_id, vehicle_url)).fetchone()
    if not existing_favorite:
        return {"message": "Veículo não está nos favoritos"}, 400

    c.execute("DELETE FROM favorites3 WHERE user_id = ? AND vehicle_url = ?", (user_id, vehicle_url))
    conn.commit()
    c.close()
    conn.close()
    return {"message": "Removido dos favoritos com sucesso"}

# For retrieving all favorite car models for a user
def get_favorites(user_id: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    favorites = c.execute("SELECT vehicle_url, tipo_veiculo FROM favorites3 WHERE user_id = ?", (user_id,)).fetchall()
    c.close()
    conn.close()

    return [{"vehicle_url": fav[0], "tipo_veiculo": fav[1]} for fav in favorites]

# For retrieving user profile
def get_user_profile(user_id: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    user = c.execute("SELECT NOME, USER_ID, ESTADO FROM login_details2 WHERE USER_ID = ?", (user_id,)).fetchone()
    if not user:
        c.close()
        conn.close()
        return {"message": "Usuário não encontrado"}, 404

    favorites = get_favorites(user_id)

    c.close()
    conn.close()

    return {
        "nome": user[0],
        "email": user[1],
        "estado": user[2],
        "favoritos": favorites
    }

@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")
    nome = data.get("nome")
    estado = data.get("estado")
    return register(user_id, password, nome, estado)

@app.route("/login", methods=["POST"])
def login_user():
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")
    return login(user_id, password)

@app.route("/favorite", methods=["POST"])
# @token_required
def add_favorite():
    data = request.json
    vehicle_url = data.get("vehicle_url")
    tipo_veiculo = data.get("tipo_veiculo")
    token = request.headers.get('Authorization')
    token = token.split(" ")[1]
    data_token = verify_token(token)
    user_id = data_token.get("user_id")
    if not verify_token(token):
        return {"message": "Token ou usuário inválidos"}, 401
    return add_to_favorites(user_id, vehicle_url, tipo_veiculo)

@app.route("/favorites", methods=["GET"])
# @token_required
def list_favorites():
    token = request.headers.get('Authorization')
    token = token.split(" ")[1]
    data = verify_token(token)
    user_id = data.get("user_id")
    favorites = get_favorites(user_id)
    return jsonify(favorites)

@app.route("/favorite", methods=["DELETE"])
# @token_required
def delete_favorite():
    data = request.json
    vehicle_url = data.get("vehicle_url")
    token = request.headers.get('Authorization')
    token = token.split(" ")[1]
    data_token = verify_token(token)
    user_id = data_token.get("user_id")
    if not verify_token(token):
        return {"message": "Token ou usuário inválidos"}, 401
    return remove_from_favorites(user_id, vehicle_url)

@app.route("/perfil", methods=["GET"])
# @token_required
def get_profile():
    token = request.headers.get('Authorization')
    token = token.split(" ")[1]
    data = verify_token(token)
    user_id = data.get("user_id")
    profile = get_user_profile(user_id)
    return jsonify(profile)

def isentar_ipva(state, ano_fabricacao):
    # lista de isenção por tempo de ipva
    a10_anos = ["AP", "RN", "RR"]
    a15_anos = ["AM", "BA", "CE", "DF", "ES", "GO", "MA", "PA", "PB", "PI", "RJ", "RO", "SE"]
    a18_anos = ["MT"]
    a20_anos = ["AC", "MS", "PR", "RS", "SP"]
    a30_anos = ["SC", "TO"]
    a31_de_dezembro_2002 = ["AL"]

    current_year = datetime.now().year
    idade_veiculo = current_year - ano_fabricacao

    if (state in a10_anos) and idade_veiculo >= 10:
        return True
    elif (state in a15_anos) and idade_veiculo >= 15:
        return True
    elif (state in a18_anos) and idade_veiculo >= 18:
        return True
    elif (state in a20_anos) and idade_veiculo >= 20:
        return True
    elif (state in a30_anos) and idade_veiculo >= 30:
        return True
    elif (state in a31_de_dezembro_2002) and ano_fabricacao <= 2002:
        return True

    return False

def calculate_ipva():
    data = request.json
    ano_fabricacao = data.get("ano_id")
    price = data.get("price")
    state = data.get("state").upper()
    tipo = data.get("tipo")
    # Dicionário para Carros de passeio

    ipva_carros = {
        "AC": 0.02,
        "AL": 0.03,
        "AP": 0.03,
        "AM": 0.03,
        "BA": 0.03,
        "CE": 0.03,
        "DF": 0.04,
        "ES": 0.02,
        "GO": 0.04,
        "MA": 0.03,
        "MT": 0.03,
        "MS": 0.04,
        "MG": 0.04,
        "PA": 0.03,
        "PB": 0.03,
        "PR": 0.04,
        "PE": 0.03,
        "PI": 0.03,
        "RJ": 0.04,
        "RN": 0.03,
        "RS": 0.03,
        "RO": 0.03,
        "RR": 0.03,
        "SC": 0.02,
        "SP": 0.04,
        "SE": 0.03,
        "TO": 0.02
    }

    # Dicionário para Caminhonetes e utilitários
    ipva_utilitarios = {
        "AC": 0.01,
        "AL": 0.03,
        "AP": 0.03,
        "AM": 0.03,
        "BA": 0.03,
        "CE": 0.03,
        "DF": 0.01,
        "ES": 0.02,
        "GO": 0.03,
        "MA": 0.03,
        "MT": 0.03,
        "MS": 0.04,
        "MG": 0.03,
        "PA": 0.03,
        "PB": 0.03,
        "PR": 0.04,
        "PE": 0.03,
        "PI": 0.03,
        "RJ": 0.03,
        "RN": 0.03,
        "RS": 0.03,
        "RO": 0.03,
        "RR": 0.02,
        "SC": 0.02,
        "SP": 0.02,
        "SE": 0.03,
        "TO": 0.03
    }

    # Dicionário para Motocicletas
    ipva_motos = {
        "AC": 0.01,
        "AL": 0.03,
        "AP": 0.02,
        "AM": 0.02,
        "BA": 0.03,
        "CE": 0.02,
        "DF": 0.02,
        "ES": 0.01,
        "GO": 0.03,
        "MA": 0.01,
        "MT": 0.01,
        "MS": 0.02,
        "MG": 0.02,
        "PA": 0.01,
        "PB": 0.03,
        "PR": 0.04,
        "PE": 0.03,
        "PI": 0.02,
        "RJ": 0.02,
        "RN": 0.02,
        "RS": 0.02,
        "RO": 0.02,
        "RR": 0.02,
        "SC": 0.01,
        "SP": 0.02,
        "SE": 0.02,
        "TO": 0.02
    }

    if tipo == "carros":
        ipva_rates = ipva_carros
    elif tipo == "motos":
        ipva_rates = ipva_motos
    elif tipo == "caminhoes":
        ipva_rates = ipva_utilitarios
    else:
        return jsonify({"message": "Tipo deve ser carros, motos ou caminhoes"}), 401

    if state not in ipva_rates:
        return jsonify({"message": "Estado inválido"}), 401

    # Verificar se o veículo é isento de IPVA
    if isentar_ipva(state, ano_fabricacao):
        return jsonify({"ipva": 0})

    ipva = price * ipva_rates[state]
    return jsonify({"ipva": ipva})

# Adicionar a função à rota do Flask
@app.route("/ipva", methods=["POST"])
def calculate_ipva_route():
    return calculate_ipva()

@app.route("/test", methods=["GET"])
def api():
    return {}

if __name__ == '__main__':
    app.run(debug=True)
