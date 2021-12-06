import socket

localIP = "0.0.0.0"
localPort = "44110"

# Create a datagram socket
socketServerFront = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socketServerFront.bind((localIP, localPort))

def listVideos ():
    socketServerFront.connect_ex(localIP,localPort)
    videos = socketServerFront.send( None,'LISTAR_VIDEO')
    print(videos)

def playVideos():
    print('play')