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
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 11000
message = b'{"id":"mr hello", "command": "STREAM_VIDEO", "arg":"sample2.mp4"}'

client_socket.sendto(message,(host_ip,port))

video_queue = queue.Queue(maxsize=10) # MAXSIZE OK?
audio_queue = queue.Queue(maxsize=10)


def separate_data():
    while True:
        print("antes")
        packet, addr = client_socket.recvfrom(BUFF_SIZE) # LINHA PROBLEMÁTICA
        print("packet: ", packet)
        print("depois")

        if len(packet)>1: # checar cond
            if packet[:1] == b'v':
                video_queue.put(packet[1:])
            elif packet[:1] == b'a':
                audio_queue.put(packet[1:])

def video_stream():
    
    cv2.namedWindow('RECEIVING VIDEO')        
    cv2.moveWindow('RECEIVING VIDEO', 10,360) 
    fps,st,frames_to_count,cnt = (0,0,20,0)
    while True:
        if not video_queue.empty():
            data = base64.b64decode(video_queue.get(0),' /')
            npdata = np.fromstring(data,dtype=np.uint8)
    
            frame = cv2.imdecode(npdata,1)
            frame = cv2.putText(frame,'CLIENT FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.imshow("RECEIVING VIDEO",frame)
        key = cv2.waitKey(1) & 0xFF
    
        if key == ord('q'):
            client_socket.close()
            os._exit(1)
            break

        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st=time.time()
                cnt=0
            except:
                pass
        cnt+=1
        
            
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
                    
    # create socket
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        try:
            while len(data) < payload_size:
                packet = audio_queue.get(0) # client_socket.recv(4*1024) # 4K
                if not packet: 
                    break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q",packed_msg_size)[0]
            while len(data) < msg_size:
                data += audio_queue.get(0) # client_socket.recv(4*1024)

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
with ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(separate_data)
    executor.submit(video_stream)
    executor.submit(audio_stream)
