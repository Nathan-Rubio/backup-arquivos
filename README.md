# BACKUP DE ARQUIVOS
Este projeto implementa um sistema distribuído para backups de arquivos com
suporte a replicação de conteúdo. O sistema é composto por um gerenciador
(manager) e vários servidores (4 implementados inicialmente) que armazenam
os arquivos enviados pelos clientes (2 implementados inicialmente). O
gerenciador distribui a carga entre os servidores e coordena a replicação dos
arquivos para garantir a redundância dos dados.

O sistema é composto por 3 componentes principais, cada um é representado
em seu próprio diretório:

   **1. Cliente:** Possuí uma interface para o usuário e 3 arquivos pré-estabelecidos para servirem como demonstração.  
   
   **2. Manager (Gerenciador):** Coordena a replicação dos arquivos e
   conexão de cliente-servidor e servidor-servidor.  
   
   **3. Servidor:** Recebe e armazena os arquivos em seu diretório raiz,
   dependendo da situação, replica o arquivo recebido a outro servidor por
   intermédio do manager.  

## FLUXO DA OPERAÇÃO

   **1.** O cliente se conecta ao manager para obter o servidor onde o arquivo
   será armazenado.  
   
   **2.** O cliente envia o arquivo para o servidor designado.  
   
   **3.** O servidor armazena o arquivo e solicita ao manager um servidor de
   backup.  
   
   **4.** O servidor envia o arquivo para o servidor de backup e confirma o envio
   para o cliente.  

## OBSERVAÇÕES

Cada componente é implementada com um código dentro do seu próprio
diretório com algumas mudanças específicas:

   **1.** A mudança do cliente é apenas no nome e nos arquivos pré-implementados,
   mudando o campo FILE_1, FILE_2 e FILE_3.  

```python
FILE_1 = 'texto.txt'
FILE_2 = 'imagem.png'
FILE_3 = 'livro.pdf'
```

   **2.** A mudança no servidor é feita utilizando um arquivo geral config.py, onde é
   mantido o nome e a porta de cada um dos servidores, assim como o do
   manager, sendo necessário apenas mudar o número do servidor apenas em
   um ponto específico (A variável server_number):  

```python
# ESPECÍFICO PARA CADA SERVIDOR #
server_number = 0
server_name = SERVIDORES[server_number][0]
server_port = SERVIDORES[server_number][1]
#################################
```

## INSTRUÇÕES DE USO

Para o uso, é necessário inicializar o manager e servidores suficientes para a
implementação do backup em múltiplas instâncias para assim executar o
arquivo do cliente, que gerará uma interface no terminal para o envio do
arquivo. Aqui um exemplo da execução de cada componente, dentro de cada diretório raiz:

```bash
python manager.py
```

```bash
python server.py
```

```bash
python client.py
```

Caso haja conflito na porta utilizada, é possível alterar a porta no config.py,
assim como os nomes dos servidores e do manager.
