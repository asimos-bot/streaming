import cv2
import imutils
import os
from collections import deque
import time
import wave
import subprocess
import zlib
from multiprocessing import Manager
from concurrent.futures import ThreadPoolExecutor

import service.user as user

class Video():

    __CHUNK = 1024

    def __init__(self, filename: str,  user: user.User, width: int, height: int, sendto, manager : Manager):
        self.sendto = sendto
        self.filename = "videos/" + filename
        self.width = width
        self.height = height
        self.queue = deque(maxlen=10)#queue.Queue(maxsize=10)
        self.active_users = manager.list([user])

        self.ns = manager.Namespace()
        self.ns.video_is_running = False

        self.extract_audio(filename)

    def close(self):
        self.queue.clear()
        self.ns.video_is_running = False

    def start(self):
        self.ns.video_is_running = True
        video = cv2.VideoCapture(self.filename)

        self.FPS = video.get(cv2.CAP_PROP_FPS)
        self.TS = 0.5/self.FPS
        self.total_num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.audio_stream)
            executor.submit(self.video_stream)
            executor.submit(self.video_stream_gen, video)

    def extract_audio(self, file_name):
        command = "ffmpeg -i ./videos/{0} -ab 160k -ac 2 -ar 44100 -vn ./videos/{0}.wav -y > /dev/null 2>&1".format(file_name)
        subprocess.call(command, shell=True)

    def put(self, value):
        self.queue.appendleft(value)

    def get(self):
        while len(self.queue) == 0:
            time.sleep(0.01)
        return self.queue.pop()

    def video_stream_gen(self, video):
        fps, st, frames_to_count, cnt = (self.FPS, time.time(), 5, 0)
        while(video.isOpened() and self.ns.video_is_running):
            try:
                _, frame = video.read()
                frame = imutils.resize(frame, width=self.width, height=self.height)
                self.put(frame)
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
                time.sleep(self.TS)
            except:
                os._exit(1)
        self.ns.video_is_running = False
        video.release()

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

        while self.ns.video_is_running:#not self.queue.empty() and self.video_is_running:
            frame = self.get()
            _, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 20])
            message = buffer
            for client in self.active_users:
                self.sendto(b'v' + zlib.compress(message), client.addr)

    def audio_stream(self):

        wf = wave.open("{}.wav".format(self.filename), 'rb') # TODO: trocar por filename

        sample_rate = wf.getframerate()
        while self.ns.video_is_running:
            data = wf.readframes(Video.__CHUNK)
            for client in self.active_users:
                self.sendto(b'a' + data, client.addr)
            time.sleep(0.8*Video.__CHUNK/sample_rate)
