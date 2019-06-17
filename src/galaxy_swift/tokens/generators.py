import uuid


class UUIDTokenGenerator:

    def generate(self):
        return uuid.uuid4().hex
