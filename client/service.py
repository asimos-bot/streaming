from tkinter import Frame
import cv2
import json
import socket
import numpy as np
import threading, queue
import base64
from tkinter import ttk
from PIL import Image, ImageTk

__BUFFSIZE = 65536

socketServerFront = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socketServerFront.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, __BUFFSIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 5050
socketServerFront.bind((host_ip, port))

video_queue = queue.Queue() 
audio_queue = queue.Queue()

def listVideos ():
    socketServerFront.sendto( bytes(json.dumps({'id': 'user1', 'command': 'LIST_VIDEOS'}), 'utf-8'), (host_ip,6000))
    msg, _ = socketServerFront.recvfrom(__BUFFSIZE)
    msg = json.loads(msg)
    return msg


def separate_data():
    while True:
        packet, addr = socketServerFront.recvfrom(__BUFFSIZE) # LINHA PROBLEMÁTICA
        if len(packet)>1: # checar cond
            if packet[:1] == b'v':
                video_queue.put(packet[1:])
            elif packet[:1] == b'a':
                #audio_queue.put(packet[1:])
                #print("audio queue:", audio_queue.qsize())
                pass

def video_stream(label):

    while video_queue.empty():
        pass

    while True:
        data = base64.b64decode(video_queue.get(),' /')
        npdata = np.fromstring(data,dtype = np.uint8)
        print("pos npdata")
        frame = cv2.imdecode(npdata, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        try:
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
            print("VAI RENDERIZAR NÂO, P&*@?")
            label.configure(image=imgtk)
            label.image = imgtk 
        except:
            print("TO PULANDO ESSE ENTÂO")
            continue

def showVideo(videoTitle, label):
    socketServerFront.sendto(bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg': videoTitle}), 'utf-8'),(host_ip,6000))

    t1 = threading.Thread(target=separate_data)
    t2 = threading.Thread(target=video_stream, args=(label, ))
    
    t1.setDaemon(True) # daemon = True for background jobs
    t2.setDaemon(True)

    t1.start()
    t2.start()
