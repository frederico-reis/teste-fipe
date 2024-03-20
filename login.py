import sqlite3
import re
# Sqlite database and table

def sqllitefile():
    global conn
    conn = sqlite3.connect('login_data.db')
    global c
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS login_details
                (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID TEXT NOT NULL,
                PASSWORD TEXT NOT NULL);''')


# For choosing between register and login
def choose(endpoint):
    sqllitefile()
    nc = True
    while nc:
        if  endpoint == '/login':
            nc = False
            return login()
        elif endpoint == '/register':
            nc = False
            return register()
        else:
            raise Exception("Operação inexistente")

# For conditions in user id for registration
def user_id_check_func(u):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, u):
        return True
    else:
        return False

# For conditions in password for registration
def password_check_func(p):
    pattern = r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[~`!@#$%^&*()_\-+={[}\]|\\:;"\'<,>.?/]).{8,}'
    
    if re.match(pattern, p):
        return True
    else:
        return False

# For Registeration
def register():
    # User Name
    while True:
        print('---------------------------------------')
        user_id = input('Digite o email para registrar: ')
        user_id_check = user_id_check_func(user_id)
        if user_id_check == False:
            print('--------------------------------------')
            print('email inválido:\n')
        else:
            break

    # If user_name already exists
    exist = conn.execute("select USER_ID from login_details where USER_ID like ?", (user_id,)).fetchone()
    if exist:
        print('------------------------------------------')
        print('usuário já registrado')
        print('use outro e-mail, ou recupere a senha')
        register()

    # Password
    np = True
    while np:
        print('----------------------------')
        password = input('insira a senha: ')
        password_check = password_check_func(password)
        if 5 < len(password) < 16 and password_check:
            np = False
        else:
            print('--------------------------------------')
            print('senha não está nos padrões')

    # File Handling
    c.execute("INSERT INTO login_details (USER_ID, PASSWORD) \
          VALUES (?, ?)", (user_id, password))
    conn.commit()
    c.close()
    conn.close()
    print('------------------------')
    print('congratulation....')
    print('Registration is complete')


# For Password in Login
def login_password():
    # Password
    print('--------------------------')
    password = input('Digite a senha: ')
    password_id_exists = c.execute("select password from login_details \
    where user_id = ? and password = ?", (user_id, password,)).fetchone()
    if password_id_exists:
        print('------------------')
        print('Login feito!')
    else:
        print('--------------------------------')
        print('Usuário ou senha incorretos')
        login_password()


# For Username in Login
def login():
    # User Name
   
    global user_id
    print('------------------------------------')
    user_id = input('Digite o email: ')
    user_id_exists = c.execute("select USER_ID from login_details where USER_ID like ?", (user_id,)).fetchone()
    if not user_id_exists:
        print('------------------------------------------------------------------')
        print('usuario ou senha incorretos, tente novamente')
        login()
    # password
    else:
        login_password()


if __name__ == '__main__':
    choose('/login')
