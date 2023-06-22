import socket
import os
import threading
import datetime
import urllib.parse

HOST = '172.20.192.1'
PORT = 8000
DIRECTORY = 'D:\\User\\Desktop\\Meu-Servidor\\Descubra'  
AUDIO_PATH = 'D:\\User\\Desktop\\Meu-Servidor\\Descubra\\audio.mp3'  

def handle_request(client_socket, client_address):
    request = client_socket.recv(1024).decode('utf-8')
    print(f'Requisição: {client_address[0]}:{client_address[1]}')
    request_parts = request.split(' ')
    method = request_parts[0]
    path = urllib.parse.unquote(request_parts[1])

    if method == 'GET':
        if path == '/':
            files = os.listdir(DIRECTORY)
            response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += '<h1>Arquivos no diretorio:</h1>\n'
            for file in files:
                file_path = os.path.join(DIRECTORY, file)
                if os.path.isdir(file_path):
                    directory_name = file.replace(' ', '%20')  # Substituir espaços por %20
                    file_link = f'<a href="/{urllib.parse.quote(directory_name)}/">{file}/</a><br>'
                else:
                    file_link = f'<a href="/{urllib.parse.quote(file)}">{file}</a><br>'
                response += file_link
            response += '<h1>You got...</h1>\n'
            response += f'<audio controls autoplay><source src="/audio" type="audio/mpeg"></audio>'
        elif path == '/HEADER':
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += request
        elif path == '/INFO':
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += f'Data: {datetime.datetime.now()}\n'
            response += f'Usuário: {os.getlogin()}\n'
            response += f'SO: {os.name}\n'
        elif path == '/hello':
            response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'
            response += 'hello\n'
        elif path == '/audio':
            with open(AUDIO_PATH, 'rb') as file:
                audio_data = file.read()
            response = 'HTTP/1.1 200 OK\nContent-Type: audio/MP3\n\n'
            response_binary = bytes(response, 'utf-8') + audio_data
            client_socket.sendall(response_binary)
            client_socket.close()
            return
        else:
            file_path = os.path.join(DIRECTORY, urllib.parse.unquote(path.lstrip('/')))
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                response = 'HTTP/1.1 200 OK\nContent-Type: application/octet-stream\n\n'
                response_binary = bytes(response, 'utf-8') + file_data
                client_socket.sendall(response_binary)
                client_socket.close()
                return
            elif os.path.isdir(file_path):
                files = os.listdir(file_path)
                response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                response += f'<h1>Arquivos no diretorio {path}:</h1>\n'
                for file in files:
                    file_link = f'<a href="{os.path.join(path, urllib.parse.quote(file))}">{file}</a><br>'
                    response += file_link
            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\n'
                response += '404 Not Found\n'
    else:
        response = 'HTTP/1.1 501 Not Implemented\nContent-Type: text/plain\n\n'
        response += '501 Not Implemented\n'


    response_bytes = bytes(response, 'utf-8')
    client_socket.sendall(response_bytes)
    client_socket.close()

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f'Server rodando no {HOST}:{PORT}')

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_request, args=(client_socket, client_address))
        client_thread.start()

if __name__ == '__main__':
    run_server()
