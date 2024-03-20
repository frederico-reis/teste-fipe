import sqlite3

# Conectando ao banco de dados SQLite
conn = sqlite3.connect('login_data.db')
cursor = conn.cursor()


def insere_info(user, modelo):
    cursor.execute("INSERT INTO login_details (USER_ID, PASSWORD) \
          VALUES (?, ?)", (user, modelo))


# Função para consultar informações do usuário
def consultar_usuario(id_usuario):
    cursor.execute("SELECT * FROM login_details WHERE USER_ID = ?", (id_usuario,))
    usuario = cursor.fetchone()  # Obtém o primeiro resultado da consulta
    return usuario

# Função para exibir informações do usuário
def exibir_informacoes(usuario):
    if usuario:
        print("ID:", usuario[0])
        print("Nome:", usuario[1])
        # print("Email:", usuario[2])
        # Adicione mais campos conforme necessário
    else:
        print("Usuário não encontrado.")

# Função principal
def main():
    # Solicitar ao usuário o ID do usuário a ser consultado
    id_usuario = input("Digite o ID do usuário: ")
    
    # Consultar informações do usuário
    usuario = consultar_usuario(id_usuario)
    
    # Exibir informações do usuário
    exibir_informacoes(usuario)

    # Fechar conexão com o banco de dados
    conn.close()

if __name__ == "__main__":
    main()
