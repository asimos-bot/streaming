import secrets, string
import json

DEFAULT_HASH_SIZE = 8

class Group:

    def __init__(self, owner, members=[]):
        self.id = self.generate_hash_id()
        self.owner = owner
        self.members = members

    def generate_hash_id(self):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(DEFAULT_HASH_SIZE))  

    def get_member_ids(self):
        return [u.name for u in self.members]

    def to_json(self):
        print(self.members)
        return json.dumps({'GRUPO_DE_STREAMING': {'id': self.id, 'owner': self.owner.name, 'members': self.get_member_ids()}})
