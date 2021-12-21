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
from tkinter import Widget

class ClientService:

    __BUFFSIZE = 65536

    def __init__(self, client_ip, client_port, server_ip, server_port, widget):
        self.client_addr = (client_ip, client_port)
        self.server_addr = (server_ip, server_port)

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, ClientService.__BUFFSIZE)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.client_addr)
        self.socket.settimeout(2)

        self.widget = widget
        self.videoTitle = ""

        self.video_queue = queue.Queue() 
        self.audio_queue = queue.Queue()

        self.threads_are_running = False

    def start_receiving_transmission(self):

        self.video_queue = queue.Queue()
        self.audio_queue = queue.Queue()

        self.separation_thread = threading.Thread(target=self.separate_data)
        self.video_thread = threading.Thread(target=self.video_stream)
        self.audio_thread = threading.Thread(target=self.audio_stream)

        #self.separation_thread.setDaemon(True) # daemon = True for background jobs
        #self.audio_thread.setDaemon(True)
        #self.video_thread.setDaemon(True)

        self.threads_are_running = True

        self.separation_thread.start()
        self.audio_thread.start()
        self.video_thread.start()

    def stop_receiving_transmission(self):

        self.threads_are_running = False

        self.video_queue = queue.Queue()
        self.audio_queue = queue.Queue()

        self.separation_thread.join()
        self.audio_thread.join()
        self.video_thread.join()

    def listVideos (self):
        self.socket.sendto( bytes(json.dumps({'id': 'user1', 'command': 'LIST_VIDEOS'}), 'utf-8'), self.server_addr)
        msg, _ = self.socket.recvfrom(ClientService.__BUFFSIZE)
        msg = json.loads(msg)
        return msg

    def separate_data(self):
        while self.threads_are_running:
            try:
                packet, _ = self.socket.recvfrom(ClientService.__BUFFSIZE) # LINHA PROBLEMÁTICA
                if len(packet) > 1: # checar cond
                    if packet[:1] == b'v':
                        self.video_queue.put(packet[1:])
                    elif packet[:1] == b'a':
                        self.audio_queue.put(packet[1:])
            except TimeoutError:
                # check if stream ended or the client stopped it
                self.threads_are_running = False
                break
        print("SEPARATE CABÔ")

    def video_stream(self):

        while self.threads_are_running:
            try:
                data = base64.b64decode(self.video_queue.get(True, 1)," /")
            except queue.Empty:
                if(not self.threads_are_running): break
                continue
            self.npdata = np.fromstring(data,dtype = np.uint8)
            self.frame = cv2.imdecode(self.npdata, 1)
            self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            self.img = Image.fromarray(self.cv2image)

            '''
            # resize the best we can taking the screen size into consideration
            resize_ratio = min(self.widget.winfo_screenwidth()/img.width, self.widget.winfo_screenheight()/img.height)
            img.thumbnail((img.width * resize_ratio, img.height * resize_ratio))
            '''
            # resize the best we can taking the screen size into consideration
            #resize_ratio = min(self.widget.winfo_screenmmwidth()/img.width, self.widget.winfo_screenmmheight()/img.height)
            #img.thumbnail((img.width * resize_ratio, img.height * resize_ratio))
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.widget.configure(image=self.imgtk)
            self.widget.image = self.imgtk
        print("VIDEO CABÔ")

    def audio_stream(self):

        self.p = pyaudio.PyAudio()
        CHUNK = 1024
        self.stream = self.p.open(format=self.p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)
                        
        self.data = b''
        payload_size = struct.calcsize("Q")
        while self.threads_are_running:
            try:
                while len(self.data) < payload_size:
                    packet = self.audio_queue.get() # client_socket.recv(4*1024) # 4K
                    if not packet: 
                        break
                    self.data+=packet
                self.packed_msg_size = self.data[:payload_size]
                self.data = self.data[payload_size:]
                msg_size = struct.unpack("Q",self.packed_msg_size)[0]
                while len(self.data) < msg_size:
                    self.data += self.audio_queue.get() # client_socket.recv(4*1024)

                self.frame_data = self.data[:msg_size]
                self.data  = self.data[msg_size:]
                self.stream.write(pickle.loads(self.frame_data))
            except:
                  break

    def showVideo(self, videoTitle,quality):
        self.videoTitle = videoTitle
        if( self.threads_are_running ):
            self.stop_receiving_transmission()
        self.socket.sendto(bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg': self.videoTitle,'resolution': quality}), 'utf-8'), self.server_addr)
 
        self.start_receiving_transmission()

    def stopVideo(self):
        if( not self.threads_are_running ): return
        self.socket.sendto(bytes(json.dumps({'id': "user1", 'command': 'PARAR_STREAMING'}), 'utf-8'), self.server_addr)
        self.stop_receiving_transmission()
        print("GAME OVER :)")
