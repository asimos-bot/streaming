from tkinter import Frame
import cv2
import json
import socket
import numpy as np
import base64

__BUFFSIZE = 65536

socketServerFront = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 11000

def listVideos ():
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'LIST_VIDEOS'}), 'utf-8'), (host_ip,port))
    msg, _ = socketServerFront.recvfrom(__BUFFSIZE)
    socketServerFront.close()
    msg = json.loads(msg)
    return msg

def streamVideo(video):
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg1':video }), 'utf-8'), ('0.0.0.0', 1100))
    video = socketServerFront.recvfrom(__BUFFSIZE)
    data = base64.b64decode(video,' /')
    npdata = np.fromstring(data,dtype=np.uint8)
    frame = cv2.imdecode(npdata,1)
    return frame

def stopVideo():
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'STOP_STREAM'}), 'utf-8'), ('0.0.0.0', 1100))
    socketServerFront.close()