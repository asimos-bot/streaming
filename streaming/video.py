import cv2
import imutils
import queue
import os
import time
import base64
import wave
import pickle
import pyaudio
import struct
from multiprocessing import Lock
from concurrent.futures import ThreadPoolExecutor

import user

class Video():

    __BUFF_SIZE=65536
    __CHUNK = 1024

    def __init__(self, filename: str, owner: user.User, width: int, height: int, sendto):
        self.sendto = sendto
        self.video = cv2.VideoCapture(filename)
        self.width = width
        self.height = height
        self.FPS = self.video.get(cv2.CAP_PROP_FPS)
        self.TS = (0.5/self.FPS)
        self.BREAK = False
        self.total_num_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration_secs = float(self.total_num_frames) / float(self.FPS)
        self.d = self.video.get(cv2.CAP_PROP_POS_MSEC)
        self.queue = queue.Queue(maxsize=10)
        self.__active_users = [owner]
        self.__active_users_lock = Lock()
        self.__video_is_running = True
        self.__video_is_running_lock = Lock()

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.audio_stream)
            executor.submit(self.video_stream_gen)
            executor.submit(self.video_stream)        
    @property
    def active_users(self):
        self.__active_users_lock.acquire()
        l = self.__active_users.copy()
        self.__active_users_lock.release()
        return l
    @active_users.setter
    def active_users(self, value):
        self.__active_users_lock.acquire()
        self.__active_users = value
        self.__active_users_lock.release()
    @property
    def video_is_running(self):
        self.__video_is_running_lock.acquire()
        r = self.__video_is_running
        self.__video_is_running_lock.release()
        return r
    @video_is_running.setter
    def video_is_running(self, value):
        self.__video_is_running_lock.acquire()
        self.__video_is_running = value
        self.__video_is_running_lock.release()

    def video_stream_gen(self):
        while(self.video.isOpened()):
            try:
                _, frame = self.video.read()
                frame = imutils.resize(frame, width=self.width, height=self.height)
                self.queue.put(frame)
            except:
                os._exit(1)
        BREAK=True
        self.video.release()

    def video_stream(self):
        fps, st, frames_to_count, cnt = (0, 0, 1, 0)
        cv2.namedWindow('TRANSMITTING VIDEO')
        cv2.moveWindow('TRANSMITTING VIDEO', 10, 30)

        while self.video_is_running:#not self.queue.empty() and self.video_is_running:
            frame = self.queue.get()
            encoded, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            for client in self.active_users:
                self.sendto(b'v' + message, client.addr)
                print(len(message))
            frame = cv2.putText(frame, 'SERVER FPS: ' + str(round(fps, 1)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if cnt == frames_to_count:
                try:
                    fps = (frames_to_count/(time.time()-st))
                    st = time.time()
                    cnt = 0
                    if fps > self.FPS:
                        self.TS += 0.001
                    elif fps > self.FPS:
                        self.TS -= 0.001
                except:
                    pass
            cnt+=1
            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(int(1000*self.TS)) & 0xFF
        self.video_is_running = False

    def audio_stream(self):
        wf = wave.open("temp.wav", 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        frames_per_buffer=Video.__CHUNK)

        while self.video_is_running:
            data = wf.readframes(Video.__CHUNK)
            a = pickle.dumps(data)
            message = struct.pack("Q",len(a))+a
            for client in self.active_users:
                self.sendto(b'a' + message, client.addr)
