import socket
import time
import random
import cv2
import threading
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

WIDTH = 600
HEIGHT = 480

def sendValues():
    video = cv2.VideoCapture(0)

    video.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    while video.isOpened():
        rand = random.randrange(0,10)
        returnVal, image = video.read()
        if(not returnVal):
            print("Couldn't read the image from your webcam. Exiting...")
            break

        returnVal, data = cv2.imencode(".jpg",image)
        frame_data = data.tobytes()
        frame_size = len(frame_data)
        a = f"{rand:10}{frame_size:10}".encode("utf-8") + frame_data
        sock.sendall(a)
while True:


    try:
        sock.connect(("10.44.69.214",9999))
    except:
        time.sleep(1)
        continue

    x = threading.Thread(target=sendValues)
    x.start()

    while True:

        try:
            res = sock.recv(1024)
            res = res.decode("utf-8")

            if("res" in res):
                res = res.replace("res","").split("x")
                WIDTH = int(res[0])
                HEIGHT = int(res[1])
            elif("close" in res):
                break
        except:
            break

    sock.close()
    time.sleep(1)
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
