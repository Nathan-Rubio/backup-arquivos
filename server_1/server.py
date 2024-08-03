from socket import *
import os
import sys
sys.path.append("..")
from config import MANAGER, SERVIDORES


# Retorna o tamanho do diretório
def retornaTamanho():
  try:
    size = 0
    Folderpath = './' # Diretório raiz do servidor
    
    # Passa por todos os arquivos no diretório somando o tamanho de cada arquivo
    for path, dirs, files in os.walk(Folderpath):
        for f in files:
            fp = os.path.join(path, f)
            size += os.stat(fp).st_size

    return size
  except Exception as e:
    print(f'Erro ao retornar o tamanho do diretório: {e}')
    return None


# Copia o arquivo no diretório
def copiar_arquivo(arquivo, conteudo):
  try:
    with open(arquivo, 'wb') as novo_arquivo:
      novo_arquivo.write(conteudo)
  except Exception as e:
    print(f'Erro ao copiar o arquivo {arquivo}: {e}')


# Lê o arquivo e o envia ao socket
def ler_arquivo(path, socket):
  try:
    with open(path, 'rb') as file:
      while (dados := file.read(1024)):
        socket.send(dados)
    socket.shutdown(SHUT_WR)
  except Exception as e:
    print(f'Erro ao ler o arquivo: {e}')


# Recebe os dados do arquivo em porções de 1024 bytes
def receber_arquivo(socket):
  try:
    dados_recebidos = b""
    while (dados := socket.recv(1024)):
      dados_recebidos += dados
    return dados_recebidos
  except Exception as e:
    print(f'Erro ao receber os dados: {e}')
    return None

# Conecta o Servidor ao manager para receber o Servidor de Backup
def conectar_manager(server_name, server_port):
  try:
    with socket(AF_INET, SOCK_STREAM) as manager_socket:
      manager_socket.connect(MANAGER)
      manager_socket.send('SERVIDOR'.encode())                        # Envia uma confirmação que se trata de um servidor ao manager
      response = manager_socket.recv(1024).decode()                   # Recebe a resposta do servidor

      if response == 'CONFIRMADO':
        manager_socket.send(f'{server_name}:{server_port}'.encode())  # Envia os dados do servidor ao manager
        response = manager_socket.recv(1024).decode()                 # Recebe os dados do servidor backup
      else:
        print(f'Erro na resposta: {response}')
        return None

    servidor_backup_name, servidor_backup_port = response.split(':')
    return (servidor_backup_name, int(servidor_backup_port))
  except Exception as e:
    print(f'Erro ao conectar ao manager: {e}')
    return None


# Conecta o servidor a outro servidor
def conectar_servidor(server_name, server_port):
  try:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.connect((server_name, server_port))
    return server_socket
  except Exception as e:
    print(f'Erro ao conectar ao servidor: {e}')
    return None


# Função Principal de Servidor
def iniciar_servidor():
  # ESPECÍFICO PARA CADA SERVIDOR #
  server_number = 0
  server_name = SERVIDORES[server_number][0]
  server_port = SERVIDORES[server_number][1]
  #################################

  server_socket = socket(AF_INET, SOCK_STREAM)   
  server_socket.bind((server_name, server_port))
  server_socket.listen()                         

  print('Servidor Pronto')

  while True:
    connection_socket, addr = server_socket.accept()

    try:
      # Tentará primeiramente verificar se trata de um manager, caso sim, retorna apenas o tamanho do diretório e volta o loop ao início
      identificacao_mensagem = connection_socket.recv(1024).decode()

      if identificacao_mensagem == 'MANAGER':
        tamanho = retornaTamanho()
        print(f'Tamanho do diretório: {tamanho}')
        connection_socket.send(str(tamanho).encode())
        continue

      # Identifica se trata-se de um cliente ou um servidor e também o nome do arquivo
      identificacao, file_name = identificacao_mensagem.split('::')
      print(f'IDENTIFICAÇÃO: {identificacao}')
      print(f'ARQUIVO: {file_name}')

      connection_socket.send(b"READY")                     # Avisa que está pronto para receber o arquivo
      dados_recebidos = receber_arquivo(connection_socket) # Recebe o arquivo
      novo_arquivo_path = os.path.join('./', file_name)    # Cria um novo caminho para o arquivo
      copiar_arquivo(novo_arquivo_path, dados_recebidos)   # Copia o arquivo neste caminho

      # Caso se trate de um cliente, requisita outro servidor para servir de backup ao manager
      if identificacao == 'CLIENTE':
        servidor_backup = conectar_manager(server_name, server_port)
        print(f'Servidor Backup escolhido: {servidor_backup[0]} - Porta: {servidor_backup[1]}\n')

        server_backup_socket = conectar_servidor(servidor_backup[0], servidor_backup[1]) # Conecta-se com o servidor backup
        server_backup_socket.send(f"SERVIDOR::{file_name}".encode())                     # Envia o nome do arquivo e que se trata de outro servidor
        response = server_backup_socket.recv(1024)                                       # Obtém resposta do outro servidor

        if response.decode() == 'READY':
          ler_arquivo(novo_arquivo_path, server_backup_socket) # Lê o arquivo para o Servidor Backup quando ele estiver pronto

        connection_socket.send(b"ENVIO CONCLUIDO") # Envia uma confirmação de envio ao cliente
    except Exception as e:
      print(f'Erro no servidor: {e}')
    finally:
      connection_socket.close()


if __name__ == '__main__':
  iniciar_servidor()