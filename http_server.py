import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import os
import socket
import time
class DynamicHTTPRequestHandler(BaseHTTPRequestHandler):
    client1_switch = "FFF"
    client1_shared_data = ""

    client2_switch = "FFF"
    client2_shared_data = ""
    def do_GET(self):
        if self.path == '/client1/updates':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(DynamicHTTPRequestHandler.client1_shared_data.encode('utf-8'))

        elif self.path == '/client1/check':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(DynamicHTTPRequestHandler.client1_switch.encode('utf-8'))

        elif self.path == '/client2/updates':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(DynamicHTTPRequestHandler.client2_shared_data.encode('utf-8'))

        elif self.path == '/client2/check':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.wfile.write(DynamicHTTPRequestHandler.client2_switch.encode('utf-8'))

        elif self.path == '/client1' or self.path == '/client2':
            # Serve the main HTML file
            print("Handling Client Main")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("index.html", "r") as f:
                mainPage = ""
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if "#CLIENT#" in line:
                        p = line.split("#CLIENT#")
                        line = p[0] + self.path[1:].capitalize() + p[1]
                    mainPage +=line
                self.wfile.write(mainPage.encode('utf-8'))
        else:
            print(self.path)
            self.send_error(404, "Path Not Found")
class http_Server:
    def __init__ (self):
        self.clients = []
        #create a socket for this server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 8000))
        self.socket.listen()

        for i in range(2):
            client_conn, client_addr = self.socket.accept()
            self.clients.append([client_conn,client_addr])
            Thread(target=self.handle_client, args=(client_conn, client_addr, i)).start()
            
            if i ==0:
                Thread(target=self.start_http_server).start()

            time.sleep(1)
            url = f"http://localhost:8888/client{i+1}"
            print(f"This is the url: {url}")
            webbrowser.open(url)

        
        

    def start_http_server(self):
        os.chdir(os.getcwd())
        httpd = HTTPServer(('localhost', 8888), DynamicHTTPRequestHandler)

        #handle sockets
        print("HTTP server running on http://localhost:8888")
        httpd.serve_forever()

    def handle_client(self, CONN, ADDR, index):
        while True:
            info = CONN.recv(1024).decode('utf-8')
            switch = info[0:3]
            info = info[3:]
            print(info)
            if index == 0:
                #serve client 1
                DynamicHTTPRequestHandler.client1_switch = switch
                DynamicHTTPRequestHandler.client1_shared_data = info
            else:
                DynamicHTTPRequestHandler.client2_switch = switch
                DynamicHTTPRequestHandler.client2_shared_data = info


http_Server()