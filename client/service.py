import socket
import json

localIP = "0.0.0.0"
localPort = 1100
__BUFFSIZE = 65536

socketServerFront = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def listVideos ():
    socketServerFront.connect_ex((localIP,localPort))
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'LIST_VIDEOS'}), 'utf-8'), ('0.0.0.0', 1100))
    msg, _ = socketServerFront.recvfrom(__BUFFSIZE)
    socketServerFront.close()
    return msg

def playVideos(video):
    socketServerFront.connect_ex((localIP,localPort))
    socketServerFront.sendto( bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg1':video}), 'utf-8'), ('0.0.0.0', 1100))
    
    socketServerFront.close()
