from tkinter import Frame
import cv2
import json
import socket
import numpy as np
import queue
import pyaudio,pickle,struct
import time, os
import base64

__BUFFSIZE = 65536

socketServerFront = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 11000
video_queue = queue.Queue() 
audio_queue = queue.Queue()

def listVideos ():
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'LIST_VIDEOS'}), 'utf-8'), (host_ip,port))
    msg, _ = socketServerFront.recvfrom(__BUFFSIZE)
    socketServerFront.close()
    msg = json.loads(msg)
    return msg


def separate_data():
    while True:
        packet, addr = socketServerFront.recvfrom(__BUFFSIZE) # LINHA PROBLEMÁTICA
        if len(packet)>1: # checar cond
            if packet[:1] == b'v':
                video_queue.put(packet[1:])
            elif packet[:1] == b'a':
                audio_queue.put(packet[1:])

def video_stream(videoTitle):
    teste = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    teste.sendto(bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg': videoTitle}), 'utf-8'),(host_ip,port))
    while True:
        data = base64.b64decode(video_queue.get(),' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)


from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:

    executor.submit(separate_data)