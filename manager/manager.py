from socket import *
import sys
sys.path.append("..")
from config import MANAGER, SERVIDORES


def retorna_tamanho_servidor(server):
   server_ip, server_port = server
   try:
      server_socket = socket(AF_INET, SOCK_STREAM)
      server_socket.connect((server_ip, server_port))
      server_socket.send('MANAGER'.encode())
      tamanho = int(server_socket.recv(1024).decode())
      print(f'Tamanho do Servidor {server_ip} - {tamanho}')
      server_socket.close()
      return tamanho
   except Exception as e:
      print(f'Erro ao obter uso de armazenamento do servidor {server}: {e}')
      return None


# Escolhe o servidor para o cliente
def escolher_servidor_cliente():
  try:
    tamanho_servidores = {}
    for server in SERVIDORES:
      tamanho = retorna_tamanho_servidor(server)
      if tamanho is not None:
        tamanho_servidores[server] = tamanho
    
    servidor = min(tamanho_servidores, key=tamanho_servidores.get)
    return servidor
  except Exception as e:
     print(f'Erro na escolha do Servidor: {e}')
     return None


# Escolhe o servidor para o backup
def escolher_servidor_backup(servidor_principal):
  servidores_disponiveis = [s for s in SERVIDORES if s != servidor_principal]
  tamanho_servidores = {server: retorna_tamanho_servidor(server) for server in servidores_disponiveis}
  servidor_backup = min(tamanho_servidores, key=tamanho_servidores.get)
  print(f'Servidor Escolhido para Backup: {servidor_backup}')
  return servidor_backup


# Inicia o manager
def iniciar_manager():
  manager_socket = socket(AF_INET, SOCK_STREAM)
  manager_socket.bind(MANAGER)
  manager_socket.listen()

  print('Manager Pronto')

  while True:
    try:
      connection_socket, addr = manager_socket.accept()
      identificacao = connection_socket.recv(1024).decode() # Recebe uma identificação para saber se trata-se de um cliente ou um servidor
      print(f'IDENTIFICAÇÃO: {identificacao}')

      if identificacao == 'CLIENTE': # Caso seja cliente, envia o servidor escolhido para o cliente
          servidor = escolher_servidor_cliente()
          response = f'{servidor[0]}:{servidor[1]}'
          print(f'Servidor: {servidor[0]} - {servidor[1]}')
          connection_socket.send(response.encode())
      elif identificacao == 'SERVIDOR': # Caso seja servidor, envia o servidor backup escolhido para o servidor
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
        break

if __name__ == '__main__':
  iniciar_manager()