from socket import *
import sys
sys.path.append("..")
from config import MANAGER, SERVIDORES

# Função para obter o tamanho do servidor
def retorna_tamanho_servidor(server):
  server_ip, server_port = server
  try:
    with socket(AF_INET, SOCK_STREAM) as server_socket:
      server_socket.connect((server_ip, server_port))
      server_socket.send('MANAGER'.encode())                # Identifica que se trata do manager ao servidor
      tamanho = int(server_socket.recv(1024).decode())      # Obtém o tamanho do diretório do servidor
      print(f'Tamanho do Servidor {server_ip} - {tamanho}')
      return tamanho
  except Exception as e:
    print(f'Erro ao obter uso de armazenamento do servidor {server}: {e}')
    return None

# Função para escolher o servidor com o menor uso de armazenamento
def escolher_servidor(servidores):
  try:
    tamanho_servidores = {}
    for server in servidores:
      tamanho = retorna_tamanho_servidor(server)
      if tamanho is not None:
        tamanho_servidores[server] = tamanho

    if not tamanho_servidores:
      raise Exception('Nenhum servidor disponível.')
    
    servidor = min(tamanho_servidores, key=tamanho_servidores.get)
    return servidor
  except Exception as e:
    print(f'Erro na escolha do Servidor: {e}')
    return None

# Função para iniciar o manager
def iniciar_manager():
  manager_socket = socket(AF_INET, SOCK_STREAM)
  manager_socket.bind(MANAGER)
  manager_socket.listen()

  print('Manager Pronto')

  while True:
    connection_socket, addr = manager_socket.accept()
    try:
      identificacao = connection_socket.recv(1024).decode() # Recebe uma identificação para saber se trata-se de um cliente ou um servidor
      print(f'IDENTIFICAÇÃO: {identificacao}')

      if identificacao == 'CLIENTE':                        # Caso seja cliente, envia o servidor escolhido para o cliente
        servidor = escolher_servidor(SERVIDORES)
        if servidor:
          response = f'{servidor[0]}:{servidor[1]}'
          print(f'Servidor: {servidor[0]} - {servidor[1]}')
          connection_socket.send(response.encode())
        else:
          connection_socket.send(b'ERRO: NENHUM SERVIDOR DISPONIVEL')

      elif identificacao == 'SERVIDOR':                     # Caso seja servidor, envia o servidor backup escolhido para o servidor
        connection_socket.send(b"CONFIRMADO")
        servidor_principal = connection_socket.recv(1024).decode()
        servidor_principal_ip, servidor_principal_port = servidor_principal.split(':')
        servidor_principal = (servidor_principal_ip, int(servidor_principal_port))
        servidores_disponiveis = [s for s in SERVIDORES if s != servidor_principal] # Escolhe todos os servidores, exceto o principal
        servidor_backup = escolher_servidor(servidores_disponiveis)
        if servidor_backup:
          response = f'{servidor_backup[0]}:{servidor_backup[1]}'
          print(f'Servidor Backup: {servidor_backup[0]} - {servidor_backup[1]}')
          connection_socket.send(response.encode())
        else:
          connection_socket.send(b'ERRO: NENHUM SERVIDOR DISPONIVEL')

    except Exception as e:
        print(f"Erro no manager: {e}")
    finally:
        connection_socket.close()

if __name__ == '__main__':
    iniciar_manager()