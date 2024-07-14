from socket import *
import os

def copiar_arquivo(arquivo, conteudo):
  with open(arquivo, 'wb') as novo_arquivo:
    novo_arquivo.write(conteudo)

def conectar_manager():
  manager_name = '127.0.0.1'                            # Nome do Manager
  manager_port = 65432                                  # Nome da Porta
  manager_socket = socket(AF_INET, SOCK_STREAM)         # Socket TCP
  manager_socket.connect((manager_name, manager_port))  # Conecta Socket ao Manager

  response = manager_socket.recv(1024).decode()         # Recebe qual servidor será usado
  manager_socket.close()

  principal_name, principal_port = response.split(':')
  return (principal_name, int(principal_port))

def iniciar_servidor():
  server_port = 65433                            # Porta do servidor
  server_socket = socket(AF_INET, SOCK_STREAM)   # Socket TCP
  server_socket.bind(('localhost', server_port)) # Conecta o Socket ao localhost
  server_socket.listen()                         # Inicia a escuta do servidor

  print('The server is ready to receive')

  while True:
    # Aceita a conexão
    connection_socket, addr = server_socket.accept()

    file_name = connection_socket.recv(1024).decode()
    connection_socket.send(b"READY")

    # Recebe o arquivo
    received_data = b""
    while True:
      data = connection_socket.recv(1024)
      if not data:
          break
      received_data += data

    # Copia o arquivo no diretório do servidor
    novo_arquivo_path = os.path.join('./', file_name)
    copiar_arquivo(novo_arquivo_path, received_data)

    # Envia o arquivo para o outro servidor

    # Envia o arquivo de volta ao cliente
    connection_socket.send(received_data)

    #Fecha a conexão
    connection_socket.close()


if __name__ == '__main__':
  iniciar_servidor()