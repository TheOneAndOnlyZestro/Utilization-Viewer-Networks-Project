import socket
import os
import psutil
import subprocess
import time

class Client:
    def __init__(self, HOST, PORT):
        self.retryAttempts = 5
        self.data = {"Status: Not Finished"}
        self.result = ""
        #query data
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Connect to Server
        self.socket.connect((HOST, PORT))
        print(f"Connect to Main Server Succesfully with addres: {(HOST, PORT)}")
        #Connect to HTTP server
        self.httpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.httpSocket.connect((HOST, 8000)) 
        print(f"Connect to HTTP Server Succesfully")
        while True:
            try:
                self.queryForData()
                time.sleep(1)                
                self.socket.send(self.result.encode())
                
                info = self.socket.recv(1024).decode('utf-8')

                print(info)
                self.httpSocket.send(info.encode('utf-8'))
            except (ConnectionResetError, BrokenPipeError):
                if self.retryAttempts == 0:
                    #We reached limit so we close the program
                    break
                print("Connection lost. Reconnecting...")
                time.sleep(5)
                self.retryAttempts -=1
                self.socket.close()

    def queryForData(self):
        #run subprocess to return GPU info (WORKS ON NIVIDIA GPUs)
        res = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], stdout=subprocess.PIPE)
        res = res.stdout.decode('utf-8').strip()

        self.data = {"Status": "Finished"}
        self.data["CPUutilization"] = psutil.cpu_percent(0.5)
        res = res.split(',')
        self.data["GPUutilization1"] = res[0]
        self.data["Memory-Utilization"] = psutil.virtual_memory().percent
        self.result =""
        
        for k,v in self.data.items():
            self.result += f"{k}:{v}"
            self.result += "\n"

Client('localhost', 8080)

         