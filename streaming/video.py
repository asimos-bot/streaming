import cv2
import imutils
import queue
import os
import time
import base64
import wave
import pickle
import subprocess
import struct
from multiprocessing import Lock
from concurrent.futures import ThreadPoolExecutor

import user

class Video():

    __CHUNK = 1024

    def __init__(self, filename: str,  user: user.User, width: int, height: int, sendto):
        self.sendto = sendto
        self.filename = filename
        self.video = cv2.VideoCapture("videos/" + filename)
        self.width = width
        self.height = height
        self.FPS = self.video.get(cv2.CAP_PROP_FPS)
        self.TS = 0.5/self.FPS
        self.BREAK = False
        self.total_num_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration_secs = float(self.total_num_frames) / float(self.FPS)
        self.d = self.video.get(cv2.CAP_PROP_POS_MSEC)
        self.queue = queue.Queue(maxsize=10)
        self.active_users = [user]
        self.__video_is_running = True
        self.__video_is_running_lock = Lock()

        self.extract_audio(filename)

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.audio_stream)
            executor.submit(self.video_stream_gen)
            executor.submit(self.video_stream)

    def extract_audio(self, file_name):
        command = "ffmpeg -i ./videos/{0} -vn ./videos/{0}.wav -y".format(file_name)
        subprocess.call(command, shell=True)

    # @property
    # def active_users(self):
    #     self.__active_users_lock.acquire()
    #     l = self.__active_users.copy()
    #     self.__active_users_lock.release()
    #     return l
    # @active_users.setter
    # def active_users(self, value):
    #     self.__active_users_lock.acquire()
    #     self.__active_users = value
    #     self.__active_users_lock.release()
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

    def _round(self, x):
        if abs(x) < 1:
            if x < 0:
                x = -1
            elif x > 0:
                x = 1
            else:
                return 0
        return x

    def video_stream(self):
        fps, st, frames_to_count, cnt = (self.FPS, time.time(), 5, 0)

        while self.video_is_running:#not self.queue.empty() and self.video_is_running:
            frame = self.queue.get()
            encoded, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            for client in self.active_users:
                self.sendto(b'v' + message, client.addr)
            #frame = cv2.putText(frame, 'SERVER FPS: ' + str(round(fps, 1)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if cnt == frames_to_count:
                try:
                    fps = (frames_to_count/(time.time()-st))
                    st=time.time()
                    cnt=0
                    if fps>self.FPS:
                        self.TS+=0.001
                    elif fps<self.FPS:
                        self.TS-=0.001
                    else:
                        pass
                except:
                    pass
            cnt+=1
            #cv2.imshow('TRANSMITTING VIDEO', frame)
            # cv2.waitKey(int(2000*self.TS))
            time.sleep(self.TS)
        self.video_is_running = False

    def audio_stream(self):

        wf = wave.open("{}.wav".format("videos/" + self.filename), 'rb') # TODO: trocar por filename

        sample_rate = wf.getframerate()

        while self.video_is_running:
            data = wf.readframes(Video.__CHUNK)
            a = pickle.dumps(data)
            message = struct.pack("Q",len(a))+a
            for client in self.active_users:
                self.sendto(b'a' + message, client.addr)
            time.sleep(0.8*Video.__CHUNK/sample_rate)
