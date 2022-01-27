import json
from service.utils import Utils
from .group import Group

class User():
    def __init__(self, name, addr, udp_port=None, access='guest', group_id=None):
        self.name = name # IDENTIFICADOR
        self.addr = addr
        self.udp_port = udp_port
        self.access = access # guest | premium
        self.group_id = group_id

    def to_json(self):
        return json.dumps({'USER_INFORMATION': {'name': self.name, 'access': self.access, 'addr': self.addr, 'udp_port': self.udp_port, 'group_id': self.group_id}})

    def create_group(self, members=[]):
        new_group = Group(self, members)
        self.group_id = new_group.id
        return new_group

    def join_group(self, group):
        group.members.append(self)
        self.group_id = group.id

    def leave_group(self, group):
        index = group.members.index(self)
        group.members.pop(index)
        self.group_id = None

    def destroy_group(group_list, group_id):
        group = Utils.retrieve_group_from_list(group_list, group_id)
        for member in group.members:
            member.leave_group(group)
        group_list.pop(Utils.find_element_index(group_list, 'id', group_id))

    def is_premium(self):
        return self.access == 'premium'
