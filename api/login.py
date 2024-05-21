import sqlite3
import re
from fastapi import FastAPI, HTTPException
from tokens import generate_token, verify_token
app = FastAPI()


# Create tables if they do not exist
def init_db():
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS login_details (
                    USER_ID TEXT PRIMARY KEY,
                    PASSWORD TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    modelo_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES login_details (USER_ID)
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

# For Registeration
def register(user_id: str, password: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    if not user_id_check_func(user_id):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if len(password) < 6 or len(password) > 15 or not password_check_func(password):
        raise HTTPException(status_code=400, detail="Invalid password format")

    exist = c.execute("SELECT USER_ID FROM login_details WHERE USER_ID = ?", (user_id,)).fetchone()
    if exist:
        raise HTTPException(status_code=400, detail="User already registered")

    c.execute("INSERT INTO login_details (USER_ID, PASSWORD) VALUES (?, ?)", (user_id, password))
    conn.commit()
    c.close()
    conn.close()
    return {"message": "Register completed"}

# For Login
def login(user_id: str, password: str):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    user = c.execute("SELECT * FROM login_details WHERE USER_ID = ?", (user_id,)).fetchone()
    if user and user[2] == password:
        jwt_token = generate_token(user_id)
        c.close()
        conn.close()
        return {"message": "Login successful", "token":jwt_token}
    else:
        c.close()
        conn.close()
        raise HTTPException(status_code=401, detail="Incorrect email or password")

# For adding a car model to favorites
def add_to_favorites(user_id: str, modelo_id: int):
    conn = sqlite3.connect('login_data.db')
    c = conn.cursor()

    user = c.execute("SELECT USER_ID FROM login_details WHERE USER_ID = ?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_favorite = c.execute("SELECT * FROM favorites WHERE user_id = ? AND modelo_id = ?", (user_id, modelo_id)).fetchone()
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Model already in favorites")

    c.execute("INSERT INTO favorites (user_id, modelo_id) VALUES (?, ?)", (user_id, modelo_id))
    conn.commit()
    c.close()
    conn.close()
    return {"message": "Model added to favorites"}

@app.post("/register")
def register_user(user_id: str, password: str):
    return register(user_id, password)

@app.post("/login")
def login_user(user_id: str, password: str):
    return login(user_id, password)

@app.post("/favorite")
def add_favorite(user_id: str, modelo_id: int, token: str):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token or user ID")
    return add_to_favorites(user_id, modelo_id)

@app.get("/ipva/{tipo}/{marca_id}/{modelo_id}/{ano_id}/{price}/{state}")
def calculate_ipva(tipo: str, marca_id: int, modelo_id: int, ano_id: str, price:float, state:str):


    ipva_rates = {
        "AC": 0.02,
        "AL": 0.03,
        "AP": 0.03,
        "AM": 0.03,
        "BA": 0.025,
        "CE": 0.03,
        "DF": 0.035,
        "ES": 0.02,
        "GO": 0.0375,
        "MA": 0.025,
        "MT": 0.03,
        "MS": 0.03,
        "MG": 0.04,
        "PA": 0.025,
        "PB": 0.025,
        "PR": 0.035,
        "PE": 0.03,
        "PI": 0.025,
        "RJ": 0.04,
        "RN": 0.03,
        "RS": 0.03,
        "RO": 0.03,
        "RR": 0.03,
        "SC": 0.02,
        "SP": 0.04,
        "SE": 0.025,
        "TO": 0.02
    }

    if state.upper() not in ipva_rates.keys():
        raise HTTPException(status_code=401, detail="Invalid State")
    
    ipva = price * ipva_rates[state.upper()]

    return {
        "tipo": tipo,
        "marca_id": marca_id,
        "modelo_id": modelo_id,
        "ano_id": ano_id,
        "price": price,
        "estado":state.upper(),
        "ipva": ipva
    }


@app.get("/test")
def api():
    return {}
