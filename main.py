import socket
import platform
try:
    import psutil
except:
    import pip
    pip.main(["install","psutil"])
    import psutil
class Frame:
    def __init__(self, message,):
        self._header = 1
        self.message = message
        self._correct = False
        self._received = False
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
class Client:
    def __init__(self, message : Frame, timeout = 15):
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
    def SetTimeout(self, timeout):
        self._timeout = timeout
    def GetMyIp(self):
        return self._myIp
    def SetIp(self, ip : str = "127.0.0.0"):
        self._myIp = ip
    def SendMessage(self, message : str):
        # Section to codificate the message into small frames 8 bits per frame
        frames = list()
client = Client(None)
print(client.GetMyIp())