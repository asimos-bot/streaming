import cv2
import json
import socket
import numpy as np
import threading, queue
import base64
import pyaudio
import struct, zlib
import pickle
import time
from PIL import Image, ImageTk

class ClientService:

    __BUFFSIZE = 65536
    __CHUNK = 1024

    def __init__(self, client_ip, client_port, server_ip, server_port, widget, service_manager_ip,service_manager_port):
        self.client_addr = (client_ip, client_port)
        self.server_addr = (server_ip, server_port)
        self.service_manager_addr = (service_manager_ip,service_manager_port)

        self.client_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.client_udp.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, ClientService.__BUFFSIZE)
        self.client_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_udp.bind(self.client_addr)
        self.client_udp.settimeout(2)

        self.service_manager = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.service_manager.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.service_manager.connect(self.service_manager_addr)

        self.username = ""
        self.usertype = ""

        self.widget = widget
        self.videoTitle = ""

        self.video_queue = queue.Queue(maxsize=10)
        self.audio_queue = queue.Queue(maxsize=10)

        self.threads_are_running = False

        self.group = None

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

        self.video_queue = queue.Queue(maxsize=10)
        self.audio_queue = queue.Queue(maxsize=10)

        self.separation_thread.join()
        self.audio_thread.join()
        self.video_thread.join()

    def listVideos (self):
        self.client_udp.sendto( bytes(json.dumps({'id': self.username, 'command': 'LIST_VIDEOS'}), 'utf-8'), self.server_addr)
        msg, _ = self.client_udp.recvfrom(ClientService.__BUFFSIZE)
        msg = json.loads(msg)
        return msg
        
    def separate_data(self):
        while self.threads_are_running:
            try:
                packet, _ = self.client_udp.recvfrom(ClientService.__BUFFSIZE) # LINHA PROBLEMÁTICA
                if len(packet) > 1: # checar cond
                    if packet[:1] == b'v':
                        self.video_queue.put(packet[1:])
                    elif packet[:1] == b'a':
                        self.audio_queue.put(packet[1:])
            except socket.timeout:
                # check if stream ended or the client stopped it
                self.threads_are_running = False
                break

    def video_stream(self):

        while self.video_queue.empty():
            pass

        while self.threads_are_running:
            try:
                decompressed_data = zlib.decompress(self.video_queue.get(True, 1))
                data = decompressed_data
            except queue.Empty:
                if(not self.threads_are_running): break
                continue
            self.npdata = np.fromstring(data,dtype = np.uint8)
            self.frame = cv2.imdecode(self.npdata, 1)
            self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            self.img = Image.fromarray(self.cv2image)
            self.img = self.img.resize((426,240))
            self.imgtk = ImageTk.PhotoImage(image=self.img)

            self.widget.configure(image=self.imgtk)
            self.widget.image = self.imgtk

    def audio_stream(self):

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True,
                        frames_per_buffer=ClientService.__CHUNK)
                        
        self.data = b''
        silence = (chr(0)*ClientService.__CHUNK*4).encode('utf-8')

        while self.audio_queue.empty():
            pass

        while self.threads_are_running:
            try:
                '''
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
                '''
                self.data = self.audio_queue.get()
                self.stream.write(self.data)
            except IOError:
                self.stream.write(silence)
            except:
                  break

    def showVideo(self, videoTitle,quality):
        self.videoTitle = videoTitle
        if( self.threads_are_running ):
            self.stop_receiving_transmission()
        self.client_udp.sendto(bytes(json.dumps({'id': self.username, 'command': 'STREAM_VIDEO','arg': self.videoTitle,'resolution': quality}), 'utf-8'), self.server_addr)
 
        self.start_receiving_transmission()

    def stopVideo(self):
        if( not self.threads_are_running ): return
        self.stop_receiving_transmission()
        self.client_udp.sendto(bytes(json.dumps({'id': self.username, 'command': 'PARAR_STREAMING'}), 'utf-8'), self.server_addr)

    def entrarNaApp(self, userID, typeUser):
        packet = json.dumps({'id': userID, 'command': 'ENTRAR_NA_APP','arg': typeUser})
        print(packet)
        self.service_manager.sendall( bytes(packet, 'utf-8'))
        msg = self.service_manager.recv(4096)
        msg = json.loads(msg)
        self.username = userID
        self.usertype = typeUser
        return msg
    
    def seeGroup(self,userID):
        self.service_manager.send( bytes(json.dumps({'id': userID, 'command': 'VER_GRUPO', 'arg': self.group}), 'utf-8'))
        msg = self.service_manager.recv(ClientService.__BUFFSIZE)
        msg = json.loads(msg)
        print(msg)
        return msg

    def exitApp(self, userID):
        self.service_manager.sendto( bytes(json.dumps({'id': userID, 'command': 'SAIR_DA_APP'}), 'utf-8'), self.service_manager_addr)
        msg = self.service_manager.recv(ClientService.__BUFFSIZE)
        print(msg)

    def createGroup(self, userID):
        self.service_manager.sendto( bytes(json.dumps({'id': userID, 'command': 'CRIAR_GRUPO', 'arg':userID}), 'utf-8'), self.service_manager_addr)
        msg = self.service_manager.recv(ClientService.__BUFFSIZE)
        msg = json.loads(msg)

        self.group = msg['CRIAR_GRUPO_ACK']
        print(msg)
        return msg

    def addUserToGroup(self, userID, name):
        self.service_manager.sendto( bytes(json.dumps({'id': userID, 'command': 'ADD_USUARIO_GRUPO','arg':'g'}), 'utf-8'), self.service_manager_addr)
        msg = self.service_manager.recv(ClientService.__BUFFSIZE)
        print("name: ", name)
        msg = json.loads(msg)
        print(msg)
        return msg

    def removeUserFromGroup(self, userID, name):
        self.service_manager.sendto( bytes(json.dumps({'id': userID, 'command': 'REMOVE_USUARIO_GRUPO', 'arg':name}), 'utf-8'), self.service_manager_addr)
        msg = self.service_manager.recv(ClientService.__BUFFSIZE)
        msg = json.loads(msg)
        print(msg)
        return msg

    def listUsers(self, userID):
        self.service_manager.sendto( bytes(json.dumps({'id': userID, 'command': 'LIST_USERS'}), 'utf-8'), self.service_manager_addr)
        listUser = self.service_manager.recv(ClientService.__BUFFSIZE)
        listUser = json.loads(listUser)
        print(listUser)
        return listUser
