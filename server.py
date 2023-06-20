import socket
import os
import threading
import datetime
import urllib.parse

HOST = 'localhost'
PORT = 8000
DIRECTORY = '/path/to/directory'  # Diretório que será servido
AUDIO_PATH = '/path/to/audio.mp3'  # Caminho do arquivo de áudio

def handle_request(client_socket, client_address):
    # Recebe a requisição do cliente
    request = client_socket.recv(1024).decode('utf-8')
    print(f'Received request from {client_address[0]}:{client_address[1]}')

    # Analisa a requisição para determinar o caminho solicitado
    request_parts = request.split(' ')
    method = request_parts[0]
    path = urllib.parse.unquote(request_parts[1])

    if method == 'GET':
        if path == '/':
            # Retorna a lista de arquivos do diretório com links clicáveis para os diretórios
            files = os.listdir(DIRECTORY)
            response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += '<h1>Arquivos no diretório:</h1>\n'
            for file in files:
                file_path = os.path.join(DIRECTORY, file)
                if os.path.isdir(file_path):
                    directory_name = file.replace(' ', '_')  # Substituir espaços por underlines
                    file_link = f'<a href="/{directory_name}/">{file}/</a><br>'
                else:
                    file_link = f'<a href="/{file}">{file}</a><br>'
                response += file_link

            # Adiciona a reprodução automática do áudio
            response += '<h1>You got...</h1>\n'
            response += f'<audio controls autoplay><source src="/audio" type="audio/mpeg"></audio>'
        elif path == '/HEADER':
            # Retorna o cabeçalho HTTP da requisição
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += request
        elif path == '/info':
            # Retorna informações sobre o servidor e o computador
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += f'Data: {datetime.datetime.now()}\n'
            response += f'Usuário: {os.getlogin()}\n'
            response += f'SO: {os.name}\n'
        elif path == '/hello':
            # Responde com "hello"
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += 'hello\n'
        elif path == '/audio':
            # Retorna o arquivo de áudio
            with open(AUDIO_PATH, 'rb') as file:
                audio_data = file.read()
            response = 'HTTP/1.1 200 OK\nContent-Type: audio/mpeg\n\n'
            response_binary = bytes(response, 'utf-8') + audio_data
            client_socket.sendall(response_binary)
            client_socket.close()
            return
        else:
            # Tenta ler o arquivo ou abrir o diretório solicitado
            file_path = os.path.join(DIRECTORY, path.lstrip('/'))
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                response = 'HTTP/1.1 200 OK\nContent-Type: application/octet-stream\n\n'
                response_binary = bytes(response, 'utf-8') + file_data
                client_socket.sendall(response_binary)
                client_socket.close()
                return
            elif os.path.isdir(file_path):
                # Retorna a lista de arquivos e diretórios dentro do diretório solicitado
                files = os.listdir(file_path)
                response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                response += f'<h1>Arquivos no diretório {path}:</h1>\n'
                for file in files:
                    file_link = f'<a href="{os.path.join(path, file)}">{file}</a><br>'
                    response += file_link
            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\n'
                response += '404 Not Found\n'
    else:
        response = 'HTTP/1.1 501 Not Implemented\nContent-Type: text/plain\n\n'
        response += '501 Not Implemented\n'

    # Envia a resposta ao cliente
    response_bytes = bytes(response, 'utf-8')
    client_socket.sendall(response_bytes)
    client_socket.close()

# Função principal para iniciar o servidor
def run_server():
    # Cria o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f'Server listening on {HOST}:{PORT}')

    # Loop principal para aceitar conexões dos clientes
    while True:
        # Aguarda uma conexão
        client_socket, client_address = server_socket.accept()

        # Cria uma thread para tratar a requisição do cliente
        client_thread = threading.Thread(target=handle_request, args=(client_socket, client_address))
        client_thread.start()

if __name__ == '__main__':
    run_server()
