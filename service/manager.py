import socket
import json
from multiprocessing import Process, Lock, Manager
from .user import User
from .utils import Utils
import logging

class ServiceManager:

    # TODO: automatizar checagem de permissões / verificar checagens atuais de permissão
    # TODO: configurar logger

    __BUFF_SIZE=65536

    def __init__(self, port):
        # setup TCP server
        self.setup_logging(port, loglevel=logging.INFO)
        self.__server = self.setup_server(port)
        logging.info("Listening for clients at TCP socket {}".format(port))
        
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
            'VER_GRUPO': self.ver_grupo,
            'LIST_USERS': self.list_users
        }
        self.server_main_loop()
    def setup_logging(self, port, loglevel):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        logging.basicConfig(
                handlers=[
                    logging.FileHandler(filename='manager.log',
                    encoding='utf-8',
                )],
                format="%(asctime)s|%(levelname)s:{}({}:{}):%(message)s".format(hostname, ip, port),
                datefmt='%m/%d/%Y|%H:%M:%S',
                level=loglevel)
    def setup_server(self, port):
        # get TCP socket
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, ServiceManager.__BUFF_SIZE)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.setblocking(False)
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

        self.__server.listen(5)
        clients = []
        while True:
            # check if there is any new connections to be made
            try:
                # return (client_skt, addr)
                clients.append(self.__server.accept())
                clients[-1][0].setblocking(False)
                logging.info("connection established: {}".format(clients[-1][-1]))
            except TimeoutError:
                pass
            except BlockingIOError:
                pass

            for client_info in clients:
                client_skt = client_info[0]
                client_addr = client_info[1]
                try:
                    msg = client_skt.recv(ServiceManager.__BUFF_SIZE)
                    if len(msg) == 0:
                        continue
                    logging.info(msg)
                    packet = self.get_json(msg)
                    if not packet:
                        continue
                    logging.info("packet received: {}|client '{}': {}".format(packet, packet['id'], client_addr))
                    client = User(packet['id'], client_addr)
                    self.api_commands[packet['command']](packet, client, client_skt)
                except KeyboardInterrupt:
                    break
                except BlockingIOError:
                    continue
    
    def list_users(self, packet, user, conn):
        users = [u.name for u in self.user_list if u.group_id != user.group_id]
        msg = json.dumps({'LIST_USERS': users})
        logging.info("LIST_USERS: {}|client '{}':{}".format(users, user.name, user.addr))
        conn.sendto(bytes(msg, 'utf-8'), user.addr)

    def get_user_information(self, packet, user, conn):
        arg = packet['arg']
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, arg)
        
        if retrieved_client:
            user_information = retrieved_client.to_json()
            conn.sendto(bytes(user_information, 'utf-8'), user.addr)
            logging.info("GET_USER_INFORMATION: {}|client '{}': {}".format(user_information, user.name, user.addr))
        else:
            packet = {'msg': 'ERROR: RESOURCE NOT FOUND!'}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("GET_USER_INFORMATION: {} ({})|client '{}': {}".format(packet, arg, user.name, user.addr))

    def entrar_na_app(self, packet, user, conn):
        arg = packet['arg']
        if not Utils.retrieve_client_from_list(self.user_list, user.name):
            user.access = arg  # revisar
            self.user_list.append(user) # check access type
            packet = {'STATUS_DO_USUARIO': user.to_json()}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("ENTRAR_NA_APP: {}|client '{}': {}".format(packet, user.name, user.addr))
        else: 
            packet = {'ENTRAR_NA_APP_ACK': user.name}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("ENTRAR_NA_APP: {}|client '{}': {}".format(packet, user.name, user.addr))

    def sair_da_app(self, packet, user, conn):

        if Utils.retrieve_client_from_list(self.user_list, user.name):
            print(self.user_list)
            pos = Utils.find_element_index(self.user_list, 'name', user.name)

            # grupo é destruído quando usuário sai da aplicação
            if user.is_premium() and user.group_id:
                User.destroy_group(self.group_list, user.group_id)

            self.user_list.pop(pos)
            packet = {'SAIR_DA_APP_ACK': user.name}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("SAIR_DA_APP: {}|client '{}': {}".format(packet, user.name, user.addr))
        else:
            packet = {'msg': 'ERROR: RESOURCE NOT FOUND!'}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("SAIR_DA_APP: {}|client '{}': {}".format(packet, user.name, user.addr))

    def criar_grupo(self, packet, user, conn):
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)

        if retrieved_client and retrieved_client.is_premium():
            self.group_list.append(retrieved_client.create_group())
            packet = {'CRIAR_GRUPO_ACK': self.group_list[-1].id}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("CRIAR_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))
        else:
            packet = {'msg': 'ERROR: ACCESS DENIED!'}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("CRIAR_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))

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
            packet = {'ADD_USUARIO_GRUPO_ACK': [guest.addr, guest.group_id]}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("ADD_USUARIO_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))
        else:
            packet = {'msg': 'ERROR: ACCESS DENIED!'}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("ADD_USUARIO_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))

    def remove_usuario_grupo(self, packet, user, conn):
        arg = packet['arg'] # guest name
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)
        guest = Utils.retrieve_client_from_list(self.user_list, arg)
        group = Utils.retrieve_group_from_list(self.group_list, retrieved_client.group_id)

        if retrieved_client and retrieved_client.is_premium() and guest and group:
            index = Utils.find_element_index(self.group_list, 'id', group.id)
            guest.leave_group(self.group_list[index])
            packet = {'REMOVER_USUARIO_GRUPO_ACK': [guest.addr, guest.group_id]}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("REMOVE_USUARIO_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))
        else:
            packet = {'msg': 'ERROR: ACCESS DENIED!'}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("REMOVE_USUARIO_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))

    def ver_grupo(self, packet, user, conn):
        arg = packet['arg'] # group_id
        retrieved_client = Utils.retrieve_client_from_list(self.user_list, user.name)
        group = Utils.retrieve_group_from_list(self.group_list, arg)
        
        if retrieved_client and group and retrieved_client.is_premium():
            packet = group.to_json()
            conn.sendto(bytes(packet, 'utf-8'), user.addr)
            logging.info("VER_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))
        else:
            packet = {'msg': 'ERROR: ACCESS DENIED!'}
            conn.sendto(bytes(json.dumps(packet), 'utf-8'), user.addr)
            logging.info("VER_GRUPO: {}|client '{}': {}".format(packet, user.name, user.addr))

if __name__ == '__main__':
    import sys
    def parse_loglevel_from_cli(args):
        for arg in sys.argv:
            if(arg.startswith('--log=')):
                return arg.split('=')[1]
        return 'INFO' # default
    loglevel = parse_loglevel_from_cli(sys.argv)
    streaming = ServiceManager(5000)
