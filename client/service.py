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

        self.widget = widget
        self.videoTitle = ""

        self.video_queue = queue.Queue() 
        self.audio_queue = queue.Queue()

        self.__threads_are_running = False
        self.__threads_are_running_lock = threading.Lock()

    @property
    def threads_are_running(self):
        self.__threads_are_running_lock.acquire()
        a = self.__threads_are_running
        self.__threads_are_running_lock.release()
        return a
    @threads_are_running.setter
    def threads_are_running(self, value):
        self.__threads_are_running_lock.acquire()
        self.__threads_are_running = value
        self.__threads_are_running_lock.release()

    def start_receiving_transmission(self):

        self.video_queue = queue.Queue()
        self.audio_queue = queue.Queue()

        self.separation_thread = threading.Thread(target=self.video_stream)
        self.audio_thread = threading.Thread(target=self.audio_stream)
        self.video_thread = threading.Thread(target=self.separate_data)

        self.separation_thread.setDaemon(True) # daemon = True for background jobs
        self.audio_thread.setDaemon(True)
        self.video_thread.setDaemon(True)

        self.threads_are_running = True

        self.separation_thread.start()
        self.audio_thread.start()
        self.video_thread.start()

    def stop_receiving_transmission(self):

        self.threads_are_running = False

        self.separation_thread.join()
        self.audio_thread.join()
        self.video_thread.join()

        self.video_queue = queue.Queue()
        self.audio_queue = queue.Queue()

    def listVideos (self):
        self.socket.sendto( bytes(json.dumps({'id': 'user1', 'command': 'LIST_VIDEOS'}), 'utf-8'), self.server_addr)
        msg, _ = self.socket.recvfrom(ClientService.__BUFFSIZE)
        msg = json.loads(msg)
        return msg

    def separate_data(self):
        while self.threads_are_running:
            packet, _ = self.socket.recvfrom(ClientService.__BUFFSIZE) # LINHA PROBLEMÁTICA
            if len(packet) > 1: # checar cond
                if packet[:1] == b'v':
                    self.video_queue.put(packet[1:])
                elif packet[:1] == b'a':
                    self.audio_queue.put(packet[1:])
            else:
                self.threads_are_running = False
        self.stop_receiving_transmission()

    def video_stream(self):

        while self.video_queue.empty():
            pass

        while self.threads_are_running:
            data = base64.b64decode(self.video_queue.get()," /")
            npdata = np.fromstring(data,dtype = np.uint8)
            frame = cv2.imdecode(npdata, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            img = Image.fromarray(cv2image)

            '''
            # resize the best we can taking the screen size into consideration
            resize_ratio = min(self.widget.winfo_screenwidth()/img.width, self.widget.winfo_screenheight()/img.height)
            img.thumbnail((img.width * resize_ratio, img.height * resize_ratio))
            '''
            # resize the best we can taking the screen size into consideration
            resize_ratio = min(self.widget.winfo_screenmmwidth()/img.width, self.widget.winfo_screenmmheight()/img.height)
            print(img.width, img.height, img.width * resize_ratio, img.height * resize_ratio)
            img.thumbnail((img.width * resize_ratio, img.height * resize_ratio))

            imgtk = ImageTk.PhotoImage(image=img)
            self.widget.configure(image=imgtk)
            self.widget.image = imgtk 

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
        while self.threads_are_running:
            try:
                while len(data) < payload_size:
                    packet = self.audio_queue.get() # client_socket.recv(4*1024) # 4K
                    if not packet: 
                        break
                    data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]
                while len(data) < msg_size:
                    data += self.audio_queue.get() # client_socket.recv(4*1024)

                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)
                stream.write(frame)
            except:
                  break

    def showVideo(self, videoTitle):
        self.videoTitle = videoTitle
        if( self.threads_are_running ):
            self.stop_receiving_transmission()
        self.socket.sendto(bytes(json.dumps({'id': "user1", 'command': 'STREAM_VIDEO','arg': self.videoTitle}), 'utf-8'), self.server_addr)
 
        self.start_receiving_transmission()

    def stopVideo(self):

        if( self.threads_are_running ): return
        self.stop_receiving_transmission()
        self.socket.sendto(bytes(json.dumps({'id': "user1", 'command': 'STOP_STREAM'}), 'utf-8'), self.server_addr)
