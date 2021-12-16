import socket, enum, json, os
import cv2, wave, pyaudio, imutils, base64, logging, subprocess, time, wave
import pickle, struct
import numpy as np
from user import User

# don't use 'threading' module, as it doesn't really create other threads except
# when one is waiting for an I/O response
# (https://stackoverflow.com/questions/3310049/proper-use-of-mutexes-in-python)
from multiprocessing import Process, Lock

class StreamQuality():
    VIDEO_720P=[1280, 720],
    VIDEO_480P=[854, 480],
    VIDEO_240P=[426, 240]

class StreamingServer():

    __BUFF_SIZE=65536
    CHUNK = 1024

    def __init__(self, port, loglevel=logging.INFO):
        self.api_commands = {
            "LIST_VIDEOS": self.list_videos,
            "STREAM_VIDEO": self.stream_video,
            "USER_INFORMATION": self.user_information,
            "STOP_STREAM": self.stop_stream,
            "PLAY_STREAM_TO_GROUP": self.play_stream_to_group
        }
        # dictionary with stream owners as keys and streams as values
        self.__active_streams = dict()
        self.__stream_lock = Lock()
        # setup logging service
        self.setup_logging(port, loglevel)
        # setup UDP server
        self.__server = self.setup_server(port)
        self.__server_lock = Lock()
        logging.info("Listening for streaming clients at UDP socket")
        self.server_main_loop()

    def setup_logging(self, port, loglevel):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        logging.basicConfig(
                handlers=[
                    logging.FileHandler(filename='srv.log',
                    encoding='utf-8',
                )],
                format="%(asctime)s|%(levelname)s:{}({}:{}):%(message)s".format(hostname, ip, port),
                datefmt='%m/%d/%Y|%H:%M:%S',
                level=loglevel)

    def setup_server(self, port):
        # get UDP socket
        srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set socket capabilities at the API level
        # here we are setting the size of the receiving buffer
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, StreamingServer.__BUFF_SIZE)
        srv.setblocking(False)
        # bind socket to a port, in order to create a server
        # '' (INADDR_ANY) means that the server is listening to all interfaces,
        # in the pyshine example they use the machine's IP, meaning only
        # localhost would be able to access the server
        srv.bind(('', port))
        return srv
    def sendto(self, packet, client_addr):
        self.__server_lock.acquire()
        self.__server.sendto(packet, client_addr)
        self.__server_lock.release()
    def extract_audio(self, file_name):
        command = "ffmpeg -i ./videos/{0}.mp4 -vn ./videos/{0}.wav -y".format(file_name.split(".")[0])
        subprocess.call(command, shell=True)
    def close_stream(self, key):
        self.__stream_lock.acquire()
        if key in self.__active_streams.keys():
            self.__active_streams.pop(key)
        self.__stream_lock.release()
    def add_stream(self, user, video, quality):
        self.__stream_lock.acquire()
        res=None
        if user.name not in self.__active_streams.keys():
            res = self.__active_streams[user.name] = Stream(self, user, video, quality)
            self.extract_audio(video)
        self.__stream_lock.release()
        return res
    def recvfrom(self):
        msg = b''
        addr = b''
        self.__server_lock.acquire()
        try:
            msg, addr = self.__server.recvfrom(StreamingServer.__BUFF_SIZE)
        except BlockingIOError:
            pass
        self.__server_lock.release()
        return msg, addr
    def get_json(self, data):

        try:
            packet = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            return None
        if "id" not in packet.keys() or "command" not in packet.keys() or packet['command'] not in self.api_commands.keys():
            return None
        if packet['command'] == "STREAM_VIDEO" and "arg" not in packet.keys():
            return None
        return packet

    def list_videos(self, packet, user):
        logging.info("LIST_VIDEOS called by '{}'".format(user.name))
        video_list = list(filter(lambda name: name.endswith(".mp4"), os.listdir('videos')))
        self.sendto(bytes(json.dumps({"videos": video_list}), 'utf-8'), user.addr)
    def stream_video(self, packet, user):
        logging.info("STREAM_VIDEO called by '{}'".format(user.name))
        stream = self.add_stream(user, packet["arg"], StreamQuality.VIDEO_240P)
        stream.broadcast(packet["arg"].split(".")[0])
        stream.close()
    def user_information(self, packet, user):
        logging.info("USER_INFORMATION called by '{}'".format(user.name))
        logging.warning("USER_INFORMATION is not implemented yet!")
        pass
    def stop_stream(self, packet, user):
        logging.info("STOP_STREAM called by '{}'".format(user.name))
        logging.warning("STOP_STREAM is not implemented yet!")
        pass
    def play_stream_to_group(self, packet, user):
        logging.info("PLAY_STREAM_TO_GROUP called by '{}'".format(user.name))
        logging.warning("PLAY_STREAM_TO_GROUP is not implemented yet!")
    def server_main_loop(self):

        '''
        expects a json like this ("arg" is optional):
        {
            "id": "unique username",
            "command": "STREAM_VIDEO",
            "arg": "sample1"
        }
        '''
        while True:
            # get client
            msg, client_addr = self.recvfrom()
            packet = self.get_json(msg)
            if packet == None:
                continue
            print(packet)
            user = User(packet["id"], client_addr)
            Process(target=self.api_commands[packet['command']], args=(packet, user)).start()

class Stream():

    class StreamState(enum.Enum):
        PAUSED=1,
        UNPAUSED=2,

    def __init__(self, server: StreamingServer, owner : User, video: str, quality : StreamQuality):
        # constant
        self.__owner = owner
        self.active_users = [owner]
        self.video = cv2.VideoCapture("videos/" + video)
        self.quality = quality
        self.server = server
        self.audio_sample_rate = 0
    @property
    def owner(self):
        return self.__owner
    @owner.setter
    def owner(self, value):
        raise Exception("Stream.owner is supposed to be a constant value!")
    def close(self):
        self.server.close_stream(self.owner)
    def send_stream_piece(self, client_addr):
        # get frame
        _, frame = self.video.read()
        # resize it to desired quality
        if not isinstance(frame, np.ndarray): return False
        frame = imutils.resize(frame, width=self.quality[0], height=self.quality[1])
        # get it as jpg
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        # base64 encode it
        message = base64.b64encode(buffer)
        # send to user
        self.server.sendto(message, client_addr)
        return True
    def send_stream_audio(self, client_addr, wf):
        data = wf.readframes(StreamingServer.CHUNK)
        self.server.sendto(data, client_addr)
        time.sleep(0.8*StreamingServer.CHUNK/self.audio_sample_rate)
        return True
    def broadcast(self, filename):
        wf = wave.open("./videos/{}.wav".format(filename), 'rb')
        self.audio_sample_rate = wf.getframerate()
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=StreamingServer.CHUNK)
        while self.video.isOpened():
            for user in self.active_users:
                if not (self.send_stream_piece(user.addr) or self.send_stream_audio(user.addr, wf)):
                    return

if __name__ == "__main__":
    import sys
    def parse_loglevel_from_cli(args):
        for arg in sys.argv:
            if(arg.startswith("--log=")):
                return arg.split('=')[1]
        return "INFO" # default
    loglevel = parse_loglevel_from_cli(sys.argv)
    streaming = StreamingServer(1100, loglevel)
