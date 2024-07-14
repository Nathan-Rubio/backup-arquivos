from socket import *
import random

SERVIDORES = [
  ('127.0.0.1', 65433),
  ('127.0.0.1', 65434)
]

def escolher_servidor_cliente():
  servidor = random.choice(SERVIDORES)
  return servidor

def escolher_servidor_backup(servidor):
  servidor_backup = random.choice([s for s in SERVIDORES if s != servidor])
  return servidor_backup

def iniciar_manager():
  server_port = 65432
  manager_socket = socket(AF_INET, SOCK_STREAM)
  manager_socket.bind(('localhost', server_port))
  manager_socket.listen()

  print('Manager is ready to receive')

  while True:
    # Aceita a conexão do cliente
    connection_socket, addr = manager_socket.accept()

    # Escolhe o servidor
    servidor = escolher_servidor_cliente()
    response = f'{servidor[0]}:{servidor[1]}'
    connection_socket.send(response.encode())

    connection_socket.close()

if __name__ == '__main__':
  iniciar_manager()