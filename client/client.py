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

# Função para ler e enviar arquivo em partes
def ler_arquivo(PATH, client_socket):
  try:
    with open(PATH, 'rb') as file:
      while True:
        data = file.read(1024) 
        if not data:
          break
        client_socket.send(data)

    client_socket.shutdown(SHUT_WR)
  except Exception as e:
    print(f'Erro ao ler e enviar o arquivo: {e}')
  
# Função para conectar ao manager e obter o servidor
def conectar_manager():
  try:
    manager_socket = socket(AF_INET, SOCK_STREAM)
    manager_socket.connect(MANAGER)

    manager_socket.send('CLIENTE'.encode())              # Envia uma confirmação que se trata de um cliente ao manager
    response = manager_socket.recv(1024).decode()        # Recebe qual servidor será usado
    manager_socket.close()

    principal_name, principal_port = response.split(':') # Divide a resposta, obtendo o nome e a porta
    return (principal_name, int(principal_port))
  except Exception as e:
    print(f'Erro ao conectar ao manager: {e}')
    return None


# Função para conectar ao servidor
def conectar_servidor(server_name, server_port):
  try:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.connect((server_name, server_port))

    return server_socket
  except Exception as e:
    print(f'Erro ao conectar ao servidor: {e}')
    return None


# Função principal de cliente
def iniciar_cliente():
  # Cliente Conecta-se ao Manager, que escolhe o servidor e retorna ele
  servidor_principal = conectar_manager()
  if not servidor_principal:
    print('Erro ao obter o servidor do manager')
    return
  
  print(f'Servidor escolhido: {servidor_principal[0]} - Porta: {servidor_principal[1]}\n')

  # Cliente conecta ao servidor fornecido
  client_socket = conectar_servidor(servidor_principal[0], servidor_principal[1])
  if not client_socket:
    print('Erro ao conectar com o servidor')

  print('Digite o nome do arquivo desejado (Não é necessário adicionar o .tipo de arquivo, apenas o nome):\n\n1 - texto\n2 - imagem\n3 - livro\n\n')
  opcao = input('Digite o nome (Maiúsculo ou minúsculo): ').lower()

  while opcao not in FILE_OPTIONS:
    print(f'Opção Inválida: {opcao}')
    opcao = input('Digite o nome (Maiúsculo ou minúsculo): ').lower()

  file_name, file_path = FILE_OPTIONS[opcao]
  print(f'{file_name} selecionado')

  try:
    # Envia o nome do arquivo e que se trata de um cliente
    client_socket.send(f"CLIENTE::{file_name}".encode())

    # Aguarda a resposta que o servidor está pronto e envia o arquivo
    response = client_socket.recv(1024)
    if response.decode() == 'READY':
      ler_arquivo(file_path, client_socket) 

    # Recebe mensagem de confirmação do envio
    response = client_socket.recv(1024)
    if response.decode() == 'ENVIO CONCLUIDO':
      print(response.decode())
    else:
      print('ERRO NO ENVIO')
  except Exception as e:
    print(f'Erro durante o envio do arquivo: {e}')
  finally:
    client_socket.close()


if __name__ == '__main__':
  iniciar_cliente()