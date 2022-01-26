import socket, json, os
import logging
from service import user
from . import video
from enum import Enum
# from .. import service

# don't use 'threading' module, as it doesn't really create other threads except
# when one is waiting for an I/O response
# (https://stackoverflow.com/questions/3310049/proper-use-of-mutexes-in-python)
from multiprocessing import Process, Manager

class StreamQuality(Enum):
    VIDEO_720P=(1280, 720)
    VIDEO_480P=(854, 480)
    VIDEO_240P=(426, 240)

class StreamingServer():

    __BUFF_SIZE=65536

    def __init__(self, port, service_manager_addr, loglevel=logging.INFO):
        self.api_commands = {
            "LIST_VIDEOS": self.list_videos,
            "STREAM_VIDEO": self.stream_video,
            "PARAR_STREAMING": self.stop_stream,
            "PLAY_STREAM_TO_GROUP": self.play_stream_to_group
        }
        self.service_manager = self.setup_service_manager_skt(service_manager_addr)
        # setup logging service
        self.setup_logging(port, loglevel)
        # setup UDP server
        self.__server = self.setup_server(port)
        logging.info("Listening for streaming clients at UDP socket {}".format(port))
        self.server_main_loop()

    def setup_service_manager_skt(self, service_manager_addr):
        skt = socket.create_connection(service_manager_addr)
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, StreamingServer.__BUFF_SIZE)
        skt.sendall(bytes(json.dumps({"id": "admin", "command": "ENTRAR_NA_APP", "arg": "premium"}), 'utf-8'))

        return skt

    def setup_logging(self, port, loglevel):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        logging.basicConfig(
                handlers=[
                    logging.FileHandler(filename='streaming.log',
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
        self.__server.sendto(packet, client_addr)

    def recvfrom(self):
        msg = b''
        addr = b''
        try:
            msg, addr = self.__server.recvfrom(StreamingServer.__BUFF_SIZE)
        except BlockingIOError:
            pass
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

    def list_videos(self, manager, active_streams, packet, user):
        logging.info("LIST_VIDEOS called by '{}'".format(user.name))
        video_list = list(filter(lambda name: name.endswith(".mp4"), os.listdir('streaming/videos')))
        print(video_list)
        corrected_list = list(set([v.split("_")[0] for v in video_list]))
        self.sendto(bytes(json.dumps({"videos": corrected_list}), 'utf-8'), user.addr)

    def stream_video(self, manager, active_streams, packet, user):
        logging.info("STREAM_VIDEO called by '{}'".format(user.name))

        video_filename = packet['arg']
        quality = StreamQuality['VIDEO_{}P'.format(packet['resolution'])]
        user_info = self.get_user_information(user.name)
        print("name being sent to auth: '{}'".format(user.name))
        if user.name not in active_streams.keys() and "USER_INFORMATION" in user_info.keys():
            filename = video_filename.split(".")[0]
            vd = video.Video(filename + "_{}".format(quality.value[1]) + ".mp4", user, quality.value[0], quality.value[1], self.sendto, manager)
            print("vd: ", vd.__dict__)
            active_streams[user.name] = vd
            Process(target=vd.start).start()

    def stop_stream(self, manager, active_streams, packet, user):
        # check if user has an active stream
        if user.name in active_streams.keys():
            active_streams[user.name].close()
            active_streams.pop(user.name)

    def play_stream_to_group(self, manager, active_streams, packet, user):
        user_info = self.get_user_information(user.name)['USER_INFORMATION']
        group_id = user_info['group_id']
        members = 
        if not group_id is None:
            for member in members:
                # 1. close transmission for everybody in the group (except owner)
                if member.name in active_streams.keys():
                    active_streams[member.name].close()
                # 2. add users to owner's transmission
                active_streams[member.name].active_users.append(member)
        
    def get_user_information(self, username):
        logging.info("USER_INFORMATION called by '{}'".format(username))
        self.service_manager.sendall(bytes(json.dumps({"id": "admin", "command": "GET_USER_INFORMATION", "arg": username}), 'utf-8'))
        return json.loads(self.service_manager.recv(StreamingServer.__BUFF_SIZE).decode('utf-8'))

    def server_main_loop(self):

        '''
        expects a json like this ("arg" is optional):
        {
            "id": "unique username",
            "command": "STREAM_VIDEO",
            "arg": "sample1"
        }
        '''
        with Manager() as manager:
            active_streams = manager.dict()
            while True:
                try:
                    # get client
                    msg, client_addr = self.recvfrom()
                    packet = self.get_json(msg)
                    if packet == None:
                        continue
                    logging.info("{}".format(packet))
                    client = user.User(packet["id"], client_addr)
                    self.api_commands[packet['command']](manager, active_streams, packet, client)
                    self.get_user_information("admin")
                except KeyboardInterrupt:
                    break

if __name__ == "__main__":
    import sys
    def parse_loglevel_from_cli(args):
        for arg in sys.argv:
            if(arg.startswith("--log=")):
                return arg.split('=')[1]
        return "INFO" # default
    loglevel = parse_loglevel_from_cli(sys.argv)
    streaming = StreamingServer(6000, ('127.0.0.1', 5000), loglevel)
