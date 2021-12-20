import cv2
import json
import socket
import numpy as np
import threading, queue
import base64
import pyaudio
import struct
import pickle
from PIL import Image, ImageTk

class ClientService:

    __BUFFSIZE = 65536

    def __init__(self, client_ip, client_port, server_ip, server_port):
        self.client_addr = (client_ip, client_port)
        self.server_addr = (server_ip, server_port)

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, ClientService.__BUFFSIZE)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.client_addr)

        self.video_queue = queue.Queue() 
        self.audio_queue = queue.Queue()

    def listVideos (self):
        self.socket.sendto( bytes(json.dumps({'id': 'user1', 'command': 'LIST_VIDEOS'}), 'utf-8'), self.server_addr)
        msg, _ = self.socket.recvfrom(ClientService.__BUFFSIZE)
        msg = json.loads(msg)
        return msg

    def separate_data(self):
        while True:
            packet, _ = self.socket.recvfrom(ClientService.__BUFFSIZE) # LINHA PROBLEMÁTICA
            if len(packet) > 1: # checar cond
                if packet[:1] == b'v':
                    self.video_queue.put(packet[1:])
                elif packet[:1] == b'a':
                    self.audio_queue.put(packet[1:])

        socket.close()

    def video_stream(self, label):

        while self.video_queue.empty():
            pass

        while True:
            data = base64.b64decode(self.video_queue.get()," /")
            npdata = np.fromstring(data,dtype = np.uint8)
            frame = cv2.imdecode(npdata, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
            label.configure(image=imgtk)
            label.image = imgtk 

    def audio_stream(self):

        p = pyaudio.PyAudio()
        CHUNK = 1024
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)
                        
        data = b''
        payload_size = struct.calcsize("Q")
        while True:
            try:
                while len(data) < payload_size:
                    packet = self.audio_queue.get() # client_socket.recv(4*1024) # 4K
                    if not packet: 
                        break
                    data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]
                #while len(data) < msg_size:
                #    data += audio_queue.get() # client_socket.recv(4*1024)

                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)
                stream.write(frame)

            except:
                  break


    def showVideo(self, videoTitle, label):
        self.socket.sendto(bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg': videoTitle}), 'utf-8'), self.server_addr)


        t1 = threading.Thread(target=self.video_stream, args=(label, ))
        t2 = threading.Thread(target=self.audio_stream)
        t3 = threading.Thread(target=self.separate_data)
        
        t1.setDaemon(True) # daemon = True for background jobs
        t2.setDaemon(True)
        t3.setDaemon(True)

        t1.start()
        t2.start()
        t3.start()
