import socket, enum
import cv2, wave, pyaudio, imutils, base64, logging

# don't use 'threading' module, as it doesn't really create other threads except
# when one is waiting for an I/O response
# (https://stackoverflow.com/questions/3310049/proper-use-of-mutexes-in-python)
from multiprocessing import Process, Lock

class StreamingServer():

    class State(enum.Enum):
        SHUTTING_DOWN=1,
        SHOWING_STREAM=2,
        STREAM_PAUSED=3

    __BUFF_SIZE=65536
    def __init__(self, port, loglevel=logging.INFO):

        # store this machine's hostname, ip and desired port
        # this attribute is protected by _state_lock and a @property decorator
        # feel free to use without fearing to run into race conditions
        self._state = StreamingServer.State.STREAM_PAUSED
        self._state_lock = Lock()

        # setup logging service
        self.setup_logging(port, loglevel)
        # setup UDP server
        self.server = self.setup_server(port)
        logging.info("Listening for streaming clients at UDP socket")
        self.server_main_loop()

    def setup_logging(self, port, loglevel):
        logging.getLogger(__name__)
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        logging.basicConfig(
                filename='streaming.log',
                encoding='utf-8',
                format="%(asctime)s|%(levelname)s:{}({}:{}):%(message)s".format(hostname, ip, port),
                datefmt='%m/%d/%Y|%H:%M:%S',
                level=loglevel)

    def setup_server(self, port):
        # get UDP socket
        srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set socket capabilities at the API level
        # here we are setting the size of the receiving buffer
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, StreamingServer.__BUFF_SIZE)
        # bind socket to a port, in order to create a server
        # '' (INADDR_ANY) means that the server is listening to all interfaces,
        # in the pyshine example they use the machine's IP, meaning only
        # localhost would be able to access the server
        srv.bind(('', port))
        return srv

    def server_main_loop(self):
        vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
        fps,st,frames_to_count,cnt = (0,0,20,0)

        while True:
            # get client and its message
            msg,client_addr = self.server.recvfrom(StreamingServer.__BUFF_SIZE)
            print('GOT connection from ',client_addr)
            WIDTH=400
            while(vid.isOpened()):
                _,frame = vid.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
                message = base64.b64encode(buffer)
                self.server.sendto(message, client_addr)
                frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                cv2.imshow('TRANSMITTING VIDEO',frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.server.close()
                    break
                if cnt == frames_to_count:
                    try:
                        fps = round(frames_to_count/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass
                cnt+=1

    @property
    def state(self):
        self._state_lock.acquire()
        s = self._state
        self._state_lock.release()
        return s
    @state.setter
    def state(self, value):
        self._state_lock.acquire()
        self._state = value
        self._state_lock.release()

if __name__ == "__main__":
    import sys
    def parse_loglevel_from_cli(args):
        for arg in sys.argv:
            if(arg.startswith("--log=")):
                return arg.split('=')[1]
        return "INFO" # default
    loglevel = parse_loglevel_from_cli(sys.argv)
    streaming = StreamingServer(1100, loglevel)
