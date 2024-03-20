import sqlite3

# Conectando ao banco de dados SQLite
conn = sqlite3.connect('login_data.db')
cursor = conn.cursor()

def table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS favoritos
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            USER_NAME TEXT NOT NULL,
            MODELO TEXT NOT NULL,
            ANO INTEGER NOT NULL);''')

def insere_info(user, modelo, ano):
    table()
    cursor.execute("INSERT INTO favoritos (USER_NAME, MODELO, ANO) \
          VALUES (?, ?, ?)", (user, modelo, ano))
    conn.commit()
    
def main():
    user = "teste@teste.com"
    modelo = "Uno"
    ano = 2001
    insere_info(user, modelo, ano)


if __name__ == "__main__":
    main()
