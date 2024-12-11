import socket
from threading import Thread
class Server:
    def handle_client(self, client_socket, client_address):
        print(f'Connected to {client_address}')
        while True:
            
            data = client_socket.recv(1024).decode('utf-8')

            if self.clients[f"{client_address}"] == "Client 1":
                self.DeviceInfo1 = []
            else:
                self.DeviceInfo2 = []
            for d in data.split("\n"):
                #print(d)
                if "Status" not in d and ":" in d:
                    #print(d.split(':'))
                    if self.clients[f"{client_address}"] == "Client 1": 
                        self.DeviceInfo1.append(float(d.split(':')[1]))
                    else:
                        self.DeviceInfo2.append(float(d.split(':')[1]))
            
            switch = ""
             
            if self.clients[f"{client_address}"] == "Client 1":
                #managing client 1
                if not(len(self.DeviceInfo2) == 0) and not (len(self.ThresholdValues1) == 0):
                    self.checkForThreshold(self.ThresholdValues1, self.DeviceInfo2, 2)
            else:
                if not(len(self.DeviceInfo1) == 0) and not (len(self.ThresholdValues2) == 0):
                    self.checkForThreshold(self.ThresholdValues2, self.DeviceInfo1, 1)

            currentShouldChange = self.shouldChange1 if self.clients[f"{client_address}"] == "Client 1" else self.shouldChange2
            for b in currentShouldChange:
                if b:
                    switch += "T"
                else:
                    switch += "F"

            data = switch + data
            client_socket.sendall(data.encode('utf-8'))

    def handle_http_server(self):
        while True:
            server_socket, server_address = self.socket.accept()
            print(f'Connected to http server with {server_address}')
            print("HANDLING HTTP SERVER")
            data = server_socket.recv(1000).decode('utf-8')
            # Handle POST requests
            if "POST" in data:
                print("Handling POST request")
                
                body_start = data.find("\r\n\r\n") + 4
                body = data[body_start:]  
                print(body)
                raw = body.split(':')
                l = raw[1].split(',')
                p = True;
                for i in l:
                    if i =='':
                        p = False
                if p == True:
                    if raw[0] == "client1":
                        #this is coming from client1 so compare it with deviceinfo2 and choose shouldChange2
                        self.ThresholdValues1 =  list(map(float,l))
                        self.checkForThreshold(self.ThresholdValues1, self.DeviceInfo2, 2) 
                    else:
                        #this is coming from client2 so compare it with deviceinfo1
                        self.ThresholdValues2 =  list(map(float,l))
                        self.checkForThreshold(self.ThresholdValues2, self.DeviceInfo1, 1) 
                    



    def __init__ (self, HOST, PORT, TIMEOUT):
        self.shouldChange1 = [False, False, False];
        self.shouldChange2 = [False, False, False];
        
        self.DeviceInfo1 = []
        self.ThresholdValues1 = []

        self.DeviceInfo2 = []
        self.ThresholdValues2 = []

        self.clients = {}
        #Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #set timeout
        #self.socket.settimeout(TIMEOUT)
        self.socket.bind((HOST,PORT))
        #Listen on PORT
        self.socket.listen()
        print(f'Listening on port {PORT}')
        
        #Accept client1 connection
        client1_socket, client1_address = self.socket.accept()
        self.clients[f"{client1_address}"] = "Client 1"
        thread_client1 = Thread(target=self.handle_client,args=(client1_socket, client1_address))
        thread_client1.start()

        #Accept client2 connection
        client2_socket, client2_address = self.socket.accept()
        self.clients[f"{client2_address}"] = "Client 2"
        thread_client2 = Thread(target=self.handle_client,args=(client2_socket, client2_address))
        thread_client2.start()
        
        thread_http_server = Thread(target=self.handle_http_server)
        thread_http_server.start()

    def checkForThreshold(self,T, D, index):
        res = [D[0] > T[0], D[1] > T[1], D[2] > T[2]]
        print(f"Client {index}: {res} \n [({D[0], T[0]}),({D[1], T[1]}),({D[2], T[2]})]")
        if index == 1:
            self.shouldChange1 = res
        else:
            self.shouldChange2 = res
        
        
        
        



Server('0.0.0.0',8080, 5.0)