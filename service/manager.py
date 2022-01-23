import socket
import json
from multiprocessing import Process, Lock, Manager
from .user import User
from .utils import Utils

class ServiceManager:

    # TODO: automatizar checagem de permissões / verificar checagens atuais de permissão
    # TODO: configurar logger

    __BUFF_SIZE=65536

    def __init__(self, port):
        # setup TCP server
        self.__server = self.setup_server(port)
        
        # setup User/Group DS
        self.user_list = []
        self.group_list = []
        
        # setup commands
        self.api_commands = {
            'GET_USER_INFORMATION': self.get_user_information,
            'ENTRAR_NA_APP': self.entrar_na_app,
            'SAIR_DA_APP': self.sair_da_app,
            'CRIAR_GRUPO': self.criar_grupo,
            'ADD_USUARIO_GRUPO': self.add_usuario_grupo,
            'REMOVE_USUARIO_GRUPO': self.remove_usuario_grupo,
            'VER_GRUPO': self.ver_grupo
        }
        self.server_main_loop()

    def setup_server(self, port):
        # get TCP socket
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, ServiceManager.__BUFF_SIZE)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # srv.setblocking(False)
        srv.bind(('', port))
        return srv

    def sendto(self, packet, client_addr):
        print("addr :", client_addr)
        self.__server.sendto(packet, client_addr)

    def get_json(self, data):
        try:
            packet = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            return None
        if 'id' not in packet.keys() or 'command' not in packet.keys() or packet['command'] not in self.api_commands.keys():
            return None
        return packet

    def server_main_loop(self):

        self.__server.listen()
        conn, client_addr = self.__server.accept()
        print("")

        while True:
            try:
                msg = conn.recv(ServiceManager.__BUFF_SIZE)
                packet = self.get_json(msg)
                if not packet:
                    continue
                client = User(packet['id'], client_addr)
                self.api_commands[packet['command']](packet, client, conn)
            except KeyboardInterrupt:
                break
    
    def get_user_information(self, packet, user, conn):
        arg = packet['arg']
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, arg)
        
        if retrieved_client:
            user_information = retrieved_client.to_json()
            conn.sendto(bytes(user_information, 'utf-8'), user.addr)
        else:
            conn.sendto(bytes(json.dumps({'msg': 'ERROR: RESOURCE NOT FOUND!'}), 'utf-8'), user.addr)

    def entrar_na_app(self, packet, user, conn):
        arg = packet['arg']
        if not Utils.retrieve_client_from_list(self.user_list, user.name):
            user.access = arg  # revisar
            self.user_list.append(user) # check access type
            conn.sendto(bytes(json.dumps({'STATUS_DO_USUARIO': user.to_json()
            }), 'utf-8'), user.addr)
        else: 
            conn.sendto(bytes(json.dumps({'ENTRAR_NA_APP_ACK': user.name}), 'utf-8'), user.addr)

    def sair_da_app(self, packet, user, conn):

        if Utils.retrieve_client_from_list(self.user_list, user.name):
            print(self.user_list)
            pos = Utils.find_element_index(self.user_list, 'name', user.name)
            self.user_list.pop(pos)
            conn.sendto(bytes(json.dumps({'SAIR_DA_APP_ACK': user.name}), 'utf-8'), user.addr)
        else:
            conn.sendto(bytes(json.dumps({'msg': 'ERROR: RESOURCE NOT FOUND!'}), 'utf-8'), user.addr)        

    def criar_grupo(self, packet, user, conn):
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)

        if retrieved_client and retrieved_client.is_premium():
            self.group_list.append(retrieved_client.create_group())
            conn.sendto(bytes(json.dumps({'CRIAR_GRUPO_ACK': self.group_list[-1].id}), 'utf-8'), user.addr)
        else:
            conn.sendto(bytes(json.dumps({'msg': 'ERROR: ACCESS DENIED!'}), 'utf-8'), user.addr)

    def add_usuario_grupo(self, packet, user, conn):
        arg = packet['arg'] # guest name
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)
        guest = Utils.retrieve_client_from_list(self.user_list, arg)
        print("group_id: ", user.group_id)
        group = Utils.retrieve_group_from_list(self.group_list, retrieved_client.group_id)

        if retrieved_client and retrieved_client.group_id and retrieved_client.is_premium() and guest and group:
            index = Utils.find_element_index(self.group_list, 'id', group.id)
            print(index)
            guest.join_group(self.group_list[index])
            conn.sendto(bytes(json.dumps({'ADD_USUARIO_GRUPO_ACK': [guest.addr, guest.group_id]}), 'utf-8'), user.addr)
        else:
            conn.sendto(bytes(json.dumps({'msg': 'ERROR: ACCESS DENIED!'}), 'utf-8'), user.addr)

    def remove_usuario_grupo(self, packet, user, conn):
        arg = packet['arg'] # guest name
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)
        guest = Utils.retrieve_client_from_list(self.user_list, arg)
        group = Utils.retrieve_group_from_list(self.group_list, retrieved_client.group_id)

        if retrieved_client and retrieved_client.is_premium() and guest and group:
            index = Utils.find_element_index(self.group_list, 'id', group.id)
            guest.leave_group(self.group_list[index])
            conn.sendto(bytes(json.dumps({'REMOVER_USUARIO_GRUPO_ACK': [guest.addr, guest.group_id]}), 'utf-8'), user.addr)
        else:
            conn.sendto(bytes(json.dumps({'msg': 'ERROR: ACCESS DENIED!'}), 'utf-8'), user.addr)

    def ver_grupo(self, packet, user, conn):
        arg = packet['arg'] # group_id
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)
        group = Utils.retrieve_group_from_list(self.group_list, arg)
        
        if retrieved_client and group and retrieved_client.is_premium():
            conn.sendto(bytes(group.to_json(), 'utf-8'), user.addr)
        else:
            conn.sendto(bytes(json.dumps({'msg': 'ERROR: ACCESS DENIED!'}), 'utf-8'), user.addr)

if __name__ == '__main__':
    import sys
    def parse_loglevel_from_cli(args):
        for arg in sys.argv:
            if(arg.startswith('--log=')):
                return arg.split('=')[1]
        return 'INFO' # default
    loglevel = parse_loglevel_from_cli(sys.argv)
    streaming = ServiceManager(5000)
