import json
from .group import Group

class User():
    def __init__(self, name, addr, access='guest'):
        self.name = name # IDENTIFICADOR
        self.addr = addr
        self.access = access # guest | premium
        self.group_id = None

    def to_json(self):
        return json.dumps({'USER_INFORMATION': {'name': self.name, 'access': self.access, 'addr': self.addr, 'group_id': self.group_id}})

    def create_group(self, members=[]):
        print("entrou")
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

    def is_premium(self):
        return self.access == 'premium'
