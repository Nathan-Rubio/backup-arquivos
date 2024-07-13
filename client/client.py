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
  

def iniciar_cliente():
  server_name = '127.0.0.1'                         # Nome do Servidor
  server_port = 65432                               # Nome da Porta
  client_socket = socket(AF_INET, SOCK_STREAM)      # Socket TCP
  client_socket.connect((server_name, server_port)) # Conecta socket ao servidor

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