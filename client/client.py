from socket import *

TEXT_PATH = './file.txt'
IMAGE_PATH = './yoru.jpg'
BOOK_PATH = './book.pdf'

def ler_arquivo(PATH, client_socket):
  with open(PATH, 'rb') as file:
    while True:
      data = file.read(1024) 
      if not data:
        break
      client_socket.send(data)

  client_socket.shutdown(SHUT_WR)
  
def conectar_manager():
  manager_name = '127.0.0.1'                            # Nome do Manager
  manager_port = 65432                                  # Nome da Porta
  manager_socket = socket(AF_INET, SOCK_STREAM)         # Socket TCP
  manager_socket.connect((manager_name, manager_port))  # Conecta Socket ao Manager

  response = manager_socket.recv(1024).decode()         # Recebe qual servidor será usado
  manager_socket.close()

  principal_name, principal_port, replica_name, replica_port = response.split(':')
  return (principal_name, int(principal_port)), (replica_name, int(replica_port))

def conectar_servidor(server_name, server_port):
  client_socket = socket(AF_INET, SOCK_STREAM)       # Socket TCP
  client_socket.connect((server_name, server_port))  # Conecta socket ao servidor

  return client_socket

def iniciar_cliente():
  # Cliente Conecta-se ao Manager, que escolhe o servidor e retorna ele
  servidor_principal, servidor_replica = conectar_manager()
  print(f'Servidor escolhido: {servidor_principal[0]} - Porta: {servidor_principal[1]}\n')

  client_socket = conectar_servidor(servidor_principal[0], servidor_principal[1])

  print('Escolha qual arquivo será enviado ao servidor:\n\nA - Arquivo txt\nB - imagem jpg\nC - Livro pdf\n\n')
  opcao = input('Digite a letra para selecionar a opção(Maiúsculo ou minúsculo): ')
  opcao = opcao.lower()

  match opcao:
    case 'a':
      print('Arquivo txt selecionado')
      file_name = 'text.txt'
      file_path = TEXT_PATH
    case 'b':
      print('Arquivo jpg selecionado')
      file_name = 'yoru.jpg'
      file_path = IMAGE_PATH
    case 'c':
      print('Arquivo pdf selecionado')
      file_name = 'book.pdf'
      file_path = BOOK_PATH
    case _:
      print(f'Opção Inválida: {opcao}')

  
  client_socket.send(file_name.encode())

  response = client_socket.recv(1024)
  if response.decode() == 'READY':
    ler_arquivo(file_path, client_socket)

  print(f'From Server: Envio Concluido')
  client_socket.close()


if __name__ == '__main__':
  iniciar_cliente()