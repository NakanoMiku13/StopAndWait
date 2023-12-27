import socket
import platform
import time
import random
import argparse
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
        self._correct = False
        self._last = False
        self._timeout = random.randint(1, 15)
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
    def SetResponse(self, response = "ACK"):
        self._header = 1 if "ACK" in response else 0
        self._received = response
    def GetHeader(self):
        return self._header
    def SetHeader(self, header):
        self._header = header
    def LastFrame(self):
        return self._last
    def SetLast(self):
        self._last = True
    def GetTimeOut(self):
        return self._timeout
    def SetTimeOut(self):
        self._timeout = random.randint(1, 15)
    def _VerifyError(self):
        # Create method to verify the error on the frame message
        pass
    def __str__(self):
        return f"{self.message}"
    def __repr__(self):
        return f"{self.message}"
    def encode(self):
        binary = str(bin(self._timeout)).replace('0b','')
        if len(binary) < 5:
            while len(binary) < 5:
                binary = '0' + binary
        return f"{str(self._header)}{'1' if self._correct else '0'}{'1' if self._last == True else '0'}{binary}{self.message}".encode()
    def decode(self, codedContent : str):
        self._header = codedContent[0]
        self._header = int(self._header)
        self._correct = codedContent[1]
        self._last = True if codedContent[2] == '1' else False
        self._timeout = int(codedContent[3:7],2)
        self.message = codedContent[8:]
class Client:
    def __init__(self, message : Frame, port = 8001, server = "localhost", timeout = 15 ):
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
        self.service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
    def SetTimeout(self, timeout):
        self._timeout = timeout
    def GetMyIp(self):
        return self._myIp
    def SetIp(self, ip : str = "127.0.0.0"):
        self._myIp = ip
    def SendMessage(self, message : str):
        # Section to codificate the message into small frames 8 bits per frame
        frames = list()
        header = 1
        lastElement = len(message) - 1
        count = 0
        for i in message:
            frame = Frame(str(bin(ord(i))).replace('0b',''), header)
            if count < lastElement:
                count += 1
            else:
                frame.SetLast()
            frames.append(frame)
            header = 0 if header == 1 else 1
        buffer = ""
        lastHeader = 0
        lastFrame = None
        count = 0
        lastSent = None
        while(len(frames) > 0):
            self.service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.service.connect((self.server, self.port))
            try:
                frame = frames[0]
                if frame.LastFrame() == True:
                    lastSent = frame
                print(lastFrame, frame, buffer)
                if "NACK" in buffer:
                    lastFrame.SetTimeOut()
                    frame = lastFrame
                    count -= 1
                else:
                    lastFrame = frame
                    count += 1
                    frames.pop(0)
                encoded = frame.encode()
                self.service.send(encoded)
                buffer = self.service.recv(1024).decode("utf-8")
            except Exception as ex:
                print(str(ex))
            self.service.close()
        buffer = ""
        while not "ACK" in buffer:
            self.service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.service.connect((self.server, self.port))
            encoded = lastSent.encode()
            self.service.send(encoded)
            buffer = self.service.recv(1024).decode("utf-8")
            self.service.close()
        if "ACK" in buffer:
            print("Message sent")
        else:
            print("Error on sending message")
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--client", action="store_true", help="Set the program to client mode")
parser.add_argument("-s", "--server", action="store_true", help="Set the program to server mode")
parser.add_argument("-ts", "--testserver", action="store_true", help="Set the program to test server")
parser.add_argument("-i", "--ip", type=str, help="Set the ip to connect to the server; default (localhost)")
parser.add_argument("-p", "--port", type=int, help="Set the server port default 8011")
parser.add_argument("-m", "--message", type=str, help="Set the message to send")
parser.add_argument("-t", "--timeout", type=str, help="Defines a maximum timeout to receive a message on the server (max 12)(default 5)")
args = parser.parse_args()
if args.client or args.message:
    print(args.ip)
    client = Client(None, 8001 if not args.port else args.port , "localhost" if not args.ip else args.ip)
    client.SendMessage("Hello, world!" if not args.message else args.message)
elif args.server:
    service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    service.bind(("0.0.0.0" if not args.testserver else "", 8001 if not args.port else args.port ))
    print("Waiting for connection...")
    clientName = ""
    service.listen(1)
    buffer = 0
    messages = list()
    timeout = 6 if not args.timeout else int(args.timeout)
    decodedMessage = ""
    nackCount = 0
    while 1:
        connection, address = service.accept()
        data = connection.recv(1024*5)
        message = data.decode().split(' ')[0]
        if nackCount > 20:
            print("Connection error, restart server...\nToo many errors: ", nackCount)
            connection.close()
            exit()
        if data:
            if message != "":
                frame = Frame("s")
                frame.decode(message)
                if(frame.GetTimeOut() > timeout):
                    connection.sendall("NACK".encode())
                    nackCount += 1
                else:
                    print(f"Client: {address} Sends: {frame.GetMessage()} {frame.GetHeader()} {buffer} {frame.LastFrame()}")
                    if (frame.GetHeader() == buffer):
                        connection.sendall("NACK".encode())
                        nackCount += 1
                    else:
                        messages.append(bytearray(frame.GetMessage(), "utf-8"))
                        connection.sendall(f"ACK{str(frame.GetHeader())}".encode())
                        buffer = frame.GetHeader()
                        nackCount = 0
                    if frame.LastFrame() == True or message[2] == '1':
                        for i in messages:
                            decodedMessage += chr(int(i, 2))
                        print(decodedMessage)
                        decodedMessage = ""
                        buffer = 0
                        messages = list()
            else:
                connection.sendall("NACK3".encode())
    connection.close()
else:
    print("Please set an argument -h for help")
