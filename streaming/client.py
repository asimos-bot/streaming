# This is client code to receive video frames over UDP
from sys import maxsize
import cv2, imutils, socket, pyaudio, threading, queue
import numpy as np
import time
import base64
import pickle, struct
from streaming_server import StreamingServer

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 1100
message = b'{"id":"hello mr", "command":"STREAM_VIDEO", "arg":"sample2.mp4"}'
client_socket.sendto(message,(host_ip,port))
q = queue.Queue(maxsize=2000)

def audio():
	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(2),
		channels=2,
		rate=44100,
		output=True,
		frames_per_buffer=StreamingServer.CHUNK)
	
	def recv_audio():
		while True:
			frame,_ = client_socket.recvfrom(StreamingServer.CHUNK * 8) # frame, addr
			q.put(frame)

	nested_audio_thread = threading.Thread(target=recv_audio)
	nested_audio_thread.start()

	while True:
		frame = q.get()
		stream.write(frame)
	
	client_socket.close()

def video():	
	fps,st,frames_to_count,cnt = (0,0,20,0)

	while True:
		packet,_ = client_socket.recvfrom(BUFF_SIZE)
		data = base64.b64decode(packet,' /')
		npdata = np.fromstring(data,dtype=np.uint8)
		frame = cv2.imdecode(npdata,1)
		frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
		cv2.imshow("RECEIVING VIDEO",frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			client_socket.close()
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

audio_t = threading.Thread(target=audio)
# video_t = threading.Thread(target=video)

audio_t.start()
#video_t.start()