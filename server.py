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
    requisicoes = client_socket.recv(1024).decode('utf-8')
    print(f'Received request from {client_address[0]}:{client_address[1]}')

    # Analisa a requisição para determinar o caminho solicitado
    request_parts = requisicoes.split(' ')
    metodo = request_parts[0]
    caminho = request_parts[1]

    if metodo == 'GET':
        if caminho == '/':
            # Retorna a página HTML com o áudio MP3 e o trecho de JavaScript para reprodução automática
            resposta = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            resposta += '<!DOCTYPE html>\n<html>\n<head>\n<title>Meu Servidor</title>\n<style>\n'
            arquivos = os.listdir(DIRECTORY)
            resposta = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            resposta += '<h1>Arquivos no diretorio:</h1>\n'
            for file in arquivos:
                file_path = os.path.join(DIRECTORY, file)
                if os.path.isdir(file_path):
                    file_link = f'<a href="{file}/">{file}/</a><br>'
                else:
                    file_link = f'<a href="{file}">{file}</a><br>'
                resposta += file_link
            resposta += '</style>\n<script>\n'
            resposta += 'window.addEventListener("DOMContentLoaded", function() {\n'
            resposta += '  var audio = document.getElementById("myAudio");\n'
            resposta += '  audio.play();\n'
            resposta += '});\n'
            resposta += '</script>\n</head>\n<body>\n<h1>You got...</h1>\n'
            resposta += '<audio id="myAudio" controls autoplay>\n'
            resposta += '<source src="audio.mp3" type="audio/mpeg">\n'
            resposta += '</audio>\n</body>\n</html>'
        elif caminho == '/HEADER':
            # Retorna o cabeçalho HTTP da requisição
            resposta = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            resposta += requisicoes
        elif caminho == '/info':
            # Retorna informações sobre o servidor e o computador
            resposta = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            resposta += '<h1>Informacoes sobre o servidor e o computador:</h1>\n'
            resposta += f'Data: {datetime.datetime.now()}<br>'
            resposta += f'Usuário: {os.getlogin()}<br>'
            resposta += f'SO: {os.name}<br>'
        elif caminho == '/hello':
            # Responde com "hello"
            resposta = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            resposta += 'hello\n'
        else:
            # Tenta ler o arquivo solicitado
            try:
                with open(DIRECTORY + caminho, 'rb') as file:
                    file_data = file.read()
                resposta = 'HTTP/1.1 200 OK\nContent-Type: application/octet-stream\n\n'
                response_binary = bytes(resposta, 'utf-8') + file_data
                client_socket.sendall(response_binary)
                client_socket.close()
                return
            except FileNotFoundError:
                resposta = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\n'
                resposta += '404 Not Found\n'
    else:
        resposta = 'HTTP/1.1 501 Not Implemented\nContent-Type: text/plain\n\n'
        resposta += '501 Not Implemented\n'

    # Envia a resposta ao cliente
    response_bytes = bytes(resposta, 'utf-8')
    client_socket.sendall(response_bytes)
    client_socket.close()


# Função principal para iniciar o servidor
def rodar_server():
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
    rodar_server()
