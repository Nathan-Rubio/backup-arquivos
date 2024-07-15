from socket import *
import random
import sys
sys.path.append("..")
from config import MANAGER, SERVIDORES

def escolher_servidor_cliente():
  servidor = random.choice(SERVIDORES)
  return servidor

def escolher_servidor_backup(servidor_principal):
  servidores_disponiveis = [s for s in SERVIDORES if s != servidor_principal]
  servidor_backup = random.choice(servidores_disponiveis)
  return servidor_backup

def iniciar_manager():
  manager_socket = socket(AF_INET, SOCK_STREAM)
  manager_socket.bind(MANAGER)
  manager_socket.listen()

  print('Manager is ready to receive')

  while True:
    try:
      connection_socket, addr = manager_socket.accept()
      identificacao = connection_socket.recv(1024).decode()
      print(f'IDENTIFICAÇÃO: {identificacao}')

      if identificacao == 'CLIENTE':
          servidor = escolher_servidor_cliente()
          response = f'{servidor[0]}:{servidor[1]}'
          print(f'Servidor: {servidor[0]} - {servidor[1]}')
          connection_socket.send(response.encode())
      elif identificacao == 'SERVIDOR':
          connection_socket.send(b"CONFIRMADO")
          servidor_principal = connection_socket.recv(1024).decode()
          servidor_principal_ip, servidor_principal_port = servidor_principal.split(':')
          servidor_principal = (servidor_principal_ip, int(servidor_principal_port))
          print(f'Servidor: {servidor_principal[0]} - {servidor_principal[1]}')

          servidor_backup = escolher_servidor_backup(servidor_principal)
          response = f'{servidor_backup[0]}:{servidor_backup[1]}'
          print(response)
          connection_socket.send(response.encode())

      connection_socket.close()
    except Exception as e:
        print(f"Erro no manager: {e}")

if __name__ == '__main__':
  iniciar_manager()
