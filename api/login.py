import sqlite3
import re
from fastapi import FastAPI, HTTPException
from tokens import generate_token, verify_token
app = FastAPI()

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

@app.post("/register")
def register_user(user_id: str, password: str):
    return register(user_id, password)

@app.post("/login")
def login_user(user_id: str, password: str):
    return login(user_id, password)

@app.get("/test")
def api():
    return {}
