from tkinter import Frame
import cv2
import json
import socket
import numpy as np
import queue
import pyaudio,pickle,struct
import time, os
import base64
from tkinter import ttk

__BUFFSIZE = 65536

socketServerFront = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socketServerFront.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, __BUFFSIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 11000
video_queue = queue.Queue() 
audio_queue = queue.Queue()

def listVideos ():
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'LIST_VIDEOS'}), 'utf-8'), (host_ip,port))
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

def video_stream(window):

    time.sleep(3)
    while not video_queue.empty():
        print("getting from queue...")
        data = base64.b64decode(video_queue.get(),' /')
        print("got from queue")
        npdata = np.fromstring(data,dtype = np.uint8)
        frame = cv2.imdecode(npdata, 1)
        label = ttk.Label(window, image=frame)
        label.pack()
    print("acabou")

def showVideo(videoTitle, window):
    socketServerFront.sendto(bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg': videoTitle}), 'utf-8'),(host_ip,port))

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(separate_data)
        executor.submit(video_stream, window)
   
