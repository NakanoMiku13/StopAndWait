import socket
import platform
import time
import random
try:
    import psutil
except:
    import pip
    pip.main(["install","psutil"])
    import psutil
class Frame:
    def __init__(self, message, header = None):
        self._header = 1 if header == None else header
        self.message = message
        self._received = False
        self.__Damage__()
    def __Damage__(self):
        rand = random.randint(0, 10)
        self._correct = False if rand > 5 else True
        if not self._correct:
            rand = random.randint(0, 10)
            if rand > 5:
                rand = random.randint(0, len(self.message))
                self.message = self.message[:rand] + self.message[rand+1:]
            else:
                rand = random.randint(0, len(self.message))
                self.message = self.message[:rand] + '1' + self.message[rand+1:]
    def SetMessage(self, message):
        self.message = message
    def GetMessage(self):
        return self.message
    def IsCorrect(self):
        return self._correct
    def IsReceived(self):
        return "ACK" if self._received else "NACK"
    def SetResponse(self, response = "ACK"):
        self._header = 1 if "ACK" in response else 0
        self._received = response
    def GetHeader(self):
        return self._header
    def _VerifyError(self):
        # Create method to verify the error on the frame message
        pass
    def __str__(self):
        return f"{self.message}"
    def __repr__(self):
        return f"{self.message}"
    def encode(self):
        return f"{str(self._header)}{'1' if self._correct else '0'}{self.message}".encode()
    def decode(self, codedContent : str):
        self._header = codedContent[0]
        self._correct = codedContent[1]
        self.message = codedContent[2:]
class Client:
    def __init__(self, message : Frame, service : socket.socket, timeout = 15 ):
        self._header = 1
        interfaces = psutil.net_if_addrs()
        if platform.system() == "Windows":
            try:
                ip = interfaces["Wi-Fi"][0].address
            except:
                try:
                    ip = interfaces["Ethernet"][0].address
                except:
                    ip = socket.gethostbyname(socket.gethostname())
        else:
            try:
                ip = interfaces["wlan0"][0].address
            except:
                try:
                    ip = interfaces["eth0"][0].address
                except:
                    ip = socket.gethostbyname(socket.gethostname())
        self._myIp = ip
        self.message = message
        self._correct = False
        self._received = False
        self._timeout = timeout
        self.service = service
    def SetTimeout(self, timeout):
        self._timeout = timeout
    def GetMyIp(self):
        return self._myIp
    def SetIp(self, ip : str = "127.0.0.0"):
        self._myIp = ip
    def SendMessage(self, message : str):
        # Section to codificate the message into small frames 8 bits per frame
        frames = list()
        for i in message:
            frames.append(Frame(str(bin(ord(i))).replace('0b','')))
        for frame in frames:
            self.service.connect(("localhost", 8001))
            try:
                self.service.send(frame.encode())
                response = self.service.recv(1024*5)
                print(response.decode())
            except Exception as ex:
                print(str(ex))
                pass
            self.service.close()
            self.service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
option = int(input("1) Server mode\n2) Client mode\n3) Exit\n"))
if option == 1:
    service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    service.bind(("localhost", 8001))
    print("Waiting for connection...")
    clientName = ""
    service.listen(1)
    while 1:
        connection, address = service.accept()
        data = connection.recv(1024*5)
        message = data.decode().split(' ')[0]
        frame = Frame("s")
        frame.decode(message)
        print(f"Client: {address} Sends: {frame.GetMessage()}")
        connection.sendall("ACK".encode())
    connection.close()
elif option == 2:
    service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = Client(None, service)
    client.SendMessage("Hello, world!")
    service.close()
else:
    exit()
