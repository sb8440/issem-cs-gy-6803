import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import math
import socket

class SimpleNetworkClient :
    def __init__(self, port1, port2) :
        self.fig, self.ax = plt.subplots()
        now = time.time()
        self.lastTime = now
        self.times = [time.strftime("%H:%M:%S", time.localtime(now-i)) for i in range(30, 0, -1)]
        self.infTemps = [0]*30
        self.incTemps = [0]*30
        self.infLn, = plt.plot(range(30), self.infTemps, label="Infant Temperature")
        self.incLn, = plt.plot(range(30), self.incTemps, label="Incubator Temperature")
        plt.xticks(range(30), self.times, rotation=45)
        plt.ylim((20,50))
        plt.legend(handles=[self.infLn, self.incLn])
        self.infPort = port1
        self.incPort = port2

        self.infToken = None
        self.incToken = None

        self.ani = animation.FuncAnimation(self.fig, self.updateInfTemp, interval=500)
        self.ani2 = animation.FuncAnimation(self.fig, self.updateIncTemp, interval=500)

    def updateTime(self) :
        now = time.time()
        if math.floor(now) > math.floor(self.lastTime) :
            t = time.strftime("%H:%M:%S", time.localtime(now))
            self.times.append(t)
            #last 30 seconds of of data
            self.times = self.times[-30:]
            self.lastTime = now
            plt.xticks(range(30), self.times,rotation = 45)
            plt.title(time.strftime("%A, %Y-%m-%d", time.localtime(now)))

    def getTemperatureFromPort(self, p, tok) :
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.sendto(b"%s;GET_TEMP" % tok, ("127.0.0.1", p))
        msg, addr = s.recvfrom(1024)
        m = msg.decode("utf-8")
        return (float(m))

    def authenticate(self, p, pw) :
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.sendto(b"AUTH %s" % pw, ("127.0.0.1", p))
        msg, addr = s.recvfrom(1024)
        return msg.strip()

    # NEW METHOD to invoke logout command 
    # p is port, tok is token , inf = 0 for inf operations, 1 for inc operations
    def logout(self, p, tok, inf) :
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.sendto(b"LOGOUT %s" % tok, ("127.0.0.1", p))
        msg, addr = s.recvfrom(1024)
        print("Logged out")
        m = msg.decode("utf-8")
        if m == "Token revoked":
            if (inf == 0):
                self.infToken = None
            else:
                self.incToken = None
        return msg.strip()

    def updateInfTemp(self, frame) :
        self.updateTime()
        if self.infToken is None : #not yet authenticated
            print("Not authenticated")
            self.infToken = self.authenticate(self.infPort, b"!Q#E%T&U8i6y4r2w")

        self.infTemps.append(self.getTemperatureFromPort(self.infPort, self.infToken)-273)
        #self.infTemps.append(self.infTemps[-1] + 1)
        self.infTemps = self.infTemps[-30:]
        self.infLn.set_data(range(30), self.infTemps)
        self.logout(self.infPort, self.infToken, 0)
        return self.infLn,

    def updateIncTemp(self, frame) :
        self.updateTime()
        if self.incToken is None : #not yet authenticated
            self.incToken = self.authenticate(self.incPort, b"!Q#E%T&U8i6y4r2w")

        self.incTemps.append(self.getTemperatureFromPort(self.incPort, self.incToken)-273)
        #self.incTemps.append(self.incTemps[-1] + 1)
        self.incTemps = self.incTemps[-30:]
        self.incLn.set_data(range(30), self.incTemps)
        self.logout(self.incPort, self.incToken, 1)
        return self.incLn,
"""
snc = SimpleNetworkClient(23456, 23457)

plt.grid()
plt.show()
"""