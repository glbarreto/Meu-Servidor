import socket
import os
import threading
import datetime

HOST = '172.20.192.1'
PORT = 7000
DIRECTORY = 'D:\\User\\Desktop\\2023-1\\Redes\\Descubra'  # Diretório que será servido

# Função para tratar as requisições dos clientes
def handle_request(client_socket, client_address):
    # Recebe a requisição do cliente
    request = client_socket.recv(1024).decode('utf-8')
    print(f'Received request from {client_address[0]}:{client_address[1]}')

    # Analisa a requisição para determinar o caminho solicitado
    request_parts = request.split(' ')
    method = request_parts[0]
    path = request_parts[1]

    if method == 'GET':
        if path == '/':
            # Retorna a página HTML com o áudio MP3 e o trecho de JavaScript para reprodução automática
            response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += '<!DOCTYPE html>\n<html>\n<head>\n<title>Meu Servidor</title>\n<style>\n'
            files = os.listdir(DIRECTORY)
            response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += '<h1>Arquivos no diretorio:</h1>\n'
            for file in files:
                file_path = os.path.join(DIRECTORY, file)
                if os.path.isdir(file_path):
                    file_link = f'<a href="{file}/">{file}/</a><br>'
                else:
                    file_link = f'<a href="{file}">{file}</a><br>'
                response += file_link
            response += '</style>\n<script>\n'
            response += 'window.addEventListener("DOMContentLoaded", function() {\n'
            response += '  var audio = document.getElementById("myAudio");\n'
            response += '  audio.play();\n'
            response += '});\n'
            response += '</script>\n</head>\n<body>\n<h1>You got...</h1>\n'
            response += '<audio id="myAudio" controls autoplay>\n'
            response += '<source src="audio.mp3" type="audio/mpeg">\n'
            response += '</audio>\n</body>\n</html>'
        elif path == '/HEADER':
            # Retorna o cabeçalho HTTP da requisição
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += request
        elif path == '/info':
            # Retorna informações sobre o servidor e o computador
            response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += '<h1>Informações sobre o servidor e o computador:</h1>\n'
            response += f'Data: {datetime.datetime.now()}<br>'
            response += f'Usuário: {os.getlogin()}<br>'
            response += f'SO: {os.name}<br>'
            response += f'Link: <a href="http://r.mtdv.me/wmyXd4o28f">r.mtdv.me/wmyXd4o28f</a><br>'
        elif path == '/hello':
            # Responde com "hello"
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += 'hello\n'
        else:
            # Tenta ler o arquivo solicitado
            try:
                with open(DIRECTORY + path, 'rb') as file:
                    file_data = file.read()
                response = 'HTTP/1.1 200 OK\nContent-Type: application/octet-stream\n\n'
                response_binary = bytes(response, 'utf-8') + file_data
                client_socket.sendall(response_binary)
                client_socket.close()
                return
            except FileNotFoundError:
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
