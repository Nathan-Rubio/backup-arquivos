from socket import *
import os
import sys
sys.path.append("..")
from config import MANAGER, SERVIDORES

# assign size
size = 0
 
# assign folder path
Folderpath = os.path
 
# get size
for path, dirs, files in os.walk(Folderpath):
    for f in files:
        fp = os.path.join(path, f)
        size += os.stat(fp).st_size

print(size)

# Copia o arquivo no diretório
def copiar_arquivo(arquivo, conteudo):
  with open(arquivo, 'wb') as novo_arquivo:
    novo_arquivo.write(conteudo)

# Lê o arquivo e o envia ao socket
def ler_arquivo(PATH, socket):
  with open(PATH, 'rb') as file:
    while True:
      dados = file.read(1024) 
      if not dados:
        break
      socket.send(dados)

  socket.shutdown(SHUT_WR)

# Recebe os dados do arquivo em porções de 1024 bytes
def receber_arquivo(socket):
  dados_recebidos = b""
  while True:
    dados = socket.recv(1024)
    if not dados:
        break
    dados_recebidos += dados
  return dados_recebidos

# Conecta o Servidor ao manager
def conectar_manager(server_name, server_port):
  try:
    manager_socket = socket(AF_INET, SOCK_STREAM)  # Socket TCP
    manager_socket.connect(MANAGER)                # Conecta Socket ao Manager

    manager_socket.send('SERVIDOR'.encode())       # Envia uma confirmação que se trata de um servidor ao manager
    response = manager_socket.recv(1024).decode()  # Recebe qual servidor será usado
    if response == 'CONFIRMADO':
      manager_socket.send(f'{server_name}:{server_port}'.encode())
      response = manager_socket.recv(1024).decode()
      manager_socket.close()
    else:
      print(f'Erro na resposta: {response}')

    servidor_backup_name, servidor_backup_port = response.split(':')
    return (servidor_backup_name, int(servidor_backup_port))
  except Exception as e:
    print(f'Erro ao conectar ao manager: {e}')

# Conecta o servidor a outro servidor
def conectar_servidor(server_name, server_port):
  try:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.connect((server_name, server_port))

    return server_socket
  except Exception as e:
    print(f'Erro ao conectar ao servidor: {e}')


def iniciar_servidor():
  # ESPECÍFICO PARA CADA SERVIDOR #
  server_number = 1
  server_name = SERVIDORES[server_number][0]
  server_port = SERVIDORES[server_number][1]
  #################################

  server_socket = socket(AF_INET, SOCK_STREAM)   
  server_socket.bind((server_name, server_port))
  server_socket.listen()                         

  print('Servidor Pronto')

  while True:
    # Aceita a conexão
    connection_socket, addr = server_socket.accept()

    # Identifica se trata-se de um cliente ou um servidor e também o nome do arquivo
    identificacao_mensagem = connection_socket.recv(1024).decode()
    print(f'MENSAGEM: {identificacao_mensagem}')
    identificacao, file_name = identificacao_mensagem.split('::')
    print(f'IDENTIFICAÇÃO: {identificacao}')

    # Avisa que está pronto para receber o arquivo
    connection_socket.send(b"READY")

    # Recebe o arquivo
    dados_recebidos = receber_arquivo(connection_socket)

    # Copia o arquivo no diretório do servidor
    novo_arquivo_path = os.path.join('./', file_name)
    copiar_arquivo(novo_arquivo_path, dados_recebidos)

    if identificacao == 'CLIENTE':
      # Requisita outro servidor para o manager
      servidor_backup = conectar_manager(server_name, server_port)
      print(f'Servidor Backup escolhido: {servidor_backup[0]} - Porta: {servidor_backup[1]}\n')

      # Conecta-se com o outro servidor
      server_backup_socket = conectar_servidor(servidor_backup[0], servidor_backup[1])

      # Envia o arquivo a este outro servidor
      server_backup_socket.send(f"SERVIDOR::{file_name}".encode())

      response = server_backup_socket.recv(1024)
      if response.decode() == 'READY':
        ler_arquivo(novo_arquivo_path, server_backup_socket)

      # Envia uma confirmação de envio ao cliente
      connection_socket.send(b"ENVIO CONCLUIDO")

    #Fecha a conexão
    connection_socket.close()


if __name__ == '__main__':
  iniciar_servidor()