from socket import *
import sys
sys.path.append("..")
from config import MANAGER

TEXT_PATH = './texto.txt'
IMAGE_PATH = './imagem.png'
BOOK_PATH = './livro.pdf'

FILE_OPTIONS = {
  'texto': ('texto.txt', TEXT_PATH),
  'imagem': ('imagem.png', IMAGE_PATH),
  'livro': ('livro.pdf', BOOK_PATH)
}

def ler_arquivo(PATH, client_socket):
  with open(PATH, 'rb') as file:
    while True:
      data = file.read(1024) 
      if not data:
        break
      client_socket.send(data)

  client_socket.shutdown(SHUT_WR)
  
def conectar_manager():
  try:
    manager_socket = socket(AF_INET, SOCK_STREAM) # Socket TCP
    manager_socket.connect(MANAGER)               # Conecta Socket ao Manager

    manager_socket.send('CLIENTE'.encode())       # Envia uma confirmação que se trata de um cliente ao manager
    response = manager_socket.recv(1024).decode() # Recebe qual servidor será usado
    manager_socket.close()

    principal_name, principal_port = response.split(':')
    return (principal_name, int(principal_port))
  except Exception as e:
    print(f'Erro ao conectar ao manager: {e}')

def conectar_servidor(server_name, server_port):
  try:
    server_socket = socket(AF_INET, SOCK_STREAM)       # Socket TCP
    server_socket.connect((server_name, server_port))  # Conecta socket ao servidor

    return server_socket
  except Exception as e:
    print(f'Erro ao conectar ao servidor: {e}')

def iniciar_cliente():
  # Cliente Conecta-se ao Manager, que escolhe o servidor e retorna ele
  servidor_principal = conectar_manager()
  print(f'Servidor escolhido: {servidor_principal[0]} - Porta: {servidor_principal[1]}\n')

  client_socket = conectar_servidor(servidor_principal[0], servidor_principal[1])

  print('Digite o nome do arquivo desejado (Não é necessário adicionar o .tipo de arquivo, apenas o nome):\n\n1 - texto\n2 - imagem\n3 - livro\n\n')
  opcao = input('Digite o nome (Maiúsculo ou minúsculo): ').lower()

  while opcao not in FILE_OPTIONS:
    print(f'Opção Inválida: {opcao}')
    opcao = input('Digite o nome (Maiúsculo ou minúsculo): ').lower()

  file_name, file_path = FILE_OPTIONS[opcao]
  print(f'{file_name} selecionado')

  # Envia o nome do arquivo e que se trata de um cliente
  client_socket.send(f"CLIENTE::{file_name}".encode())

  # Le e envia o arquivo
  response = client_socket.recv(1024)
  if response.decode() == 'READY':
    ler_arquivo(file_path, client_socket)

  # Recebe mensagem de confirmação do envio
  response = client_socket.recv(1024)
  if response.decode() == 'ENVIO CONCLUIDO':
    print(response.decode())
  else:
    print('ERRO NO ENVIO')

  client_socket.close()


if __name__ == '__main__':
  iniciar_cliente()