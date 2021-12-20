from multiprocessing.context import Process
import cv2, imutils, socket
import numpy as np
import time, os
import base64
import queue
import pyaudio,pickle,struct

BUFF_SIZE = 65536

BREAK = False
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
port = 6000
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
message = b'{"id":"mr hello", "command": "STREAM_VIDEO", "arg":"andre_marques_religion.mp4"}'
client_socket.sendto(message,(host_ip,port))

video_queue = queue.Queue() # MAXSIZE OK?
audio_queue = queue.Queue()


def separate_data():
    while True:
        packet, addr = client_socket.recvfrom(BUFF_SIZE) # LINHA PROBLEMÁTICA

        if len(packet)>1: # checar cond
            if packet[:1] == b'v':
                video_queue.put(packet[1:])
            elif packet[:1] == b'a':
                audio_queue.put(packet[1:])
        else:
            print("nothing")

def video_stream():
   
    cv2.namedWindow('RECEIVING VIDEO')        
    cv2.moveWindow('RECEIVING VIDEO', 10,360) 
    fps,st,frames_to_count,cnt = (0,0,30,0)
    while True:
        data = base64.b64decode(video_queue.get(),' /')
        npdata = np.fromstring(data,dtype=np.uint8)

        frame = cv2.imdecode(npdata,1)
        if cnt == frames_to_count:
            try:
                fps = (frames_to_count/(time.time() - st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt+=1
        frame = cv2.putText(frame,'CLIENT FPS: '+ str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.imshow("RECEIVING VIDEO",frame)
        #cv2.imshow('TRANSMITTING VIDEO', frame)
        cv2.waitKey(1)

    client_socket.close()
    cv2.destroyAllWindows() 

def audio_stream():
    
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
                packet = audio_queue.get() # client_socket.recv(4*1024) # 4K
                if not packet: 
                    break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q",packed_msg_size)[0]
            while len(data) < msg_size:
                data += audio_queue.get() # client_socket.recv(4*1024)

            # TODO: verificar se tamanho recebido é ok ou grande demais

            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)
            stream.write(frame)

        except:
            
            break

    client_socket.close()
    os._exit(1)

from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    executor.submit(video_stream)
    executor.submit(audio_stream)
    executor.submit(separate_data)
