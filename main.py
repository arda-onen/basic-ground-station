from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import socket
import threading
import cv2
import numpy
from PyQt5.uic import *

class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow,self).__init__()
        loadUi("main.ui",self)
        self.setIPAuto()
        self.setPort(9999)
        self.setResolution((600,480))
        self.setButtons()
        self.setMenuBarButtons()
        self.serverStarted = False
        self.clientConnected = False

    def setIPAuto(self):
        self.currentIP = socket.gethostbyname(socket.gethostname())
        self.printOrange("INFO : Current IP is changed to " + self.currentIP)

    def printOrange(self,text):
        x = "<span style=\" color:orange;\" >"
        x += text
        x += "</span>"
        self.textEdit.append(x)

    def printNormal(self,text):
        self.textEdit.append(text)

    def printRed(self,text):
        x = "<span style=\" color:red;\" >"
        x += text
        x += "</span>"
        self.textEdit.append(x)

    def printGreen(self,text):
        x = "<span style=\" color:green;\" >"
        x += text
        x += "</span>"
        self.textEdit.append(x)

    def setIPLocal(self):
        self.currentIP = "127.0.0.1"
        self.printOrange("INFO : Current IP is changed to " + self.currentIP)

    def setPort(self,value):
        self.currentPort = value
        self.printOrange("INFO : Current PORT is changed to " + str(self.currentPort))

    def setResolution(self,value):
        self.currentResolutionWidth = value[0]
        self.currentResolutionHeigth = value[1]
        self.printOrange("INFO : Current Resolution is set to " + str(self.currentResolutionWidth) + "x" + str(self.currentResolutionHeigth))

    def clearConsole(self):
        self.textEdit.clear()

    def setButtons(self):
        self.startButton.clicked.connect(self.startServer)
        self.stopButton.clicked.connect(self.stopServer)
        self.listenButton.clicked.connect(self.startListening)
        self.clearButton.clicked.connect(self.clearConsole)
        self.resolutionButton.clicked.connect(self.sendResolution)

    def setMenuBarButtons(self):
        self.actionAuto.triggered.connect(self.setIPAuto)
        self.actionLocalhost.triggered.connect(self.setIPLocal)
        self.action9999.triggered.connect(lambda: self.setPort(9999))
        self.action9990.triggered.connect(lambda: self.setPort(9990))
        self.action9900.triggered.connect(lambda: self.setPort(9900))
        self.action9000.triggered.connect(lambda: self.setPort(9000))
        self.action8000.triggered.connect(lambda: self.setPort(8000))
        self.action600x480.triggered.connect(lambda: self.setResolution((600,480)))
        self.action800x600.triggered.connect(lambda: self.setResolution((800,600)))
        self.action1024x768.triggered.connect(lambda: self.setResolution((1024,768)))
        self.action1680x1050.triggered.connect(lambda: self.setResolution((1680,1050)))
    
    def startServer(self):
        try:
            if(self.serverStarted):
                self.printOrange("ALERT : You need to close the current connection to create a new one...")
                return
            self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSocket.bind((self.currentIP,self.currentPort))
            self.printNormal("INFO : Server is created on " + self.currentIP + ":" + str(self.currentPort))
            self.serverStarted = True
        except Exception as e:
            self.printRed("ERROR : There was an error occured when creating the server socket. The error message is : " + str(e))

    def stopServer(self):
        try:
            if(not self.serverStarted):
                self.printOrange("ALERT : There is no active socket that could be closed...")
                return
            self.sendClose()
            self.serverSocket.close()
            self.printGreen("INFO : Server is closed succesfully.")
            self.serverStarted = False
        except Exception as e:
            self.printRed("ERROR : There was an error occured when closing the server socket. The error message is : " + str(e))

    def startListening(self):
        try:
            if(not self.serverStarted):
                self.printOrange("ALERT : You need to create a server first to listen connections...")
                return
            if(self.clientConnected):
                self.printOrange("ALERT : You already have a connection!")
                return
            self.serverSocket.listen(0)
            self.printGreen("INFO : Server started listening succesfully.")
            self.acceptThread = threading.Thread(target=self.acceptConnection,args=())
            self.acceptThread.start()
        except Exception as e:
            self.printRed("ERROR : There was an error occured when starting the listening process. The error message is : " + str(e))

    def acceptConnection(self):
        try:
            if(not self.serverStarted):
                self.printOrange("Alert : There is no server to accept any connection!")
                return
            self.clientSocket, self.clientAddr = self.serverSocket.accept()
            self.clientConnected = True
            self.printNormal("INFO : Got connection from " + self.clientAddr[0] + ":" + str(self.clientAddr[1]))
            self.sendResolution()
            x = threading.Thread(target=self.getResponse)
            x.start()
        except WindowsError:
            pass
        except Exception as e:
            self.printRed("ERROR : There was an error occured while finding the client. The error message is : " + str(e))

    def sendResolution(self):
        try:
            if(not self.serverStarted):
                self.printOrange("ALERT : There is no server to send data'")
                return
            self.clientSocket.send(("res" + str(self.currentResolutionWidth) + "x" + str(self.currentResolutionHeigth)).encode("utf-8"))
            self.printGreen("Resolution Values sent succesfully!")
        except Exception as e:
            self.printRed("ERROR There was an error occured while sending camera request. The error code is : " + str(e))
    
    def sendCameraRequest(self):
        try:
            if(not self.serverStarted):
                self.printOrange("ALERT : There is no server to send data!")
                return
            self.clientSocket.send("camera".encode("utf-8"))
            self.printGreen("INFO : Request sent to raspberry succesfully!")
        except Exception as e:
            self.printRed("ERROR : There was an error occured while sending camera request. The error code is : " + str(e))

    def sendClose(self):
        try:
            self.clientSocket.send("close".encode("utf-8"))
            self.clientSocket.close()
            self.clientConnected = False
        except Exception as e:
            self.printRed("ERROR : There was an error occured while sending close info to raspberry. The error code is : " + str(e))

    def getResponse(self):
        while True and self.clientConnected:
            try:
                number_data = b""
                while len(number_data) < 10:
                    number_data += self.clientSocket.recv(10)

                self.numberLabel.setText("Raspberrys Random Number : " + number_data.decode("utf-8"))

                frame_size = b""
                while len(frame_size) < 10:
                    frame_size += self.clientSocket.recv(10)

                frame_size = int(frame_size.decode("utf-8"))

                frame_data = b""
                while len(frame_data) < frame_size:
                    frame_data += self.clientSocket.recv(8192)
                
                frame = cv2.imdecode(numpy.frombuffer(frame_data,numpy.uint8),cv2.IMREAD_COLOR)
                frame = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                self.cameraLabel.setPixmap(QtGui.QPixmap.fromImage(frame))
            except:
                self.clientSocket.recv(65768)
                print("trying")
                continue
            
if(__name__ == "__main__"):
    app = QApplication(sys.argv)   # starting app
    main = MyMainWindow()
    main.show()
    sys.exit(app.exec_())
