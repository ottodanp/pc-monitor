from typing import Dict
from uuid import uuid4

from quart import Quart, request

from util import hash_auth_code


class MonitoredClient:
    _id: str
    _auth_code: str

    def __init__(self, auth_code: str):
        self._id = str(uuid4())
        self._auth_code = auth_code

    @property
    def id(self) -> str:
        return self._id

    @property
    def auth_code(self) -> str:
        return self._auth_code

    def __eq__(self, other):
        return self.id == other.id


class MonitorServer(Quart):
    _monitored_clients: Dict[str, MonitoredClient] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialize_monitored_client(self):
        auth_code = request.args.get('auth_code')
        if auth_code is None:
            return "No auth code provided", 400
        client = MonitoredClient(hash_auth_code(auth_code))

        self._monitored_clients[client.id] = client
        return {"id": client.id}

    async def receive_snapshot(self):
        return {"status": "success"}

    def run(self, *args, **kwargs):
        self.route('/init')(self.initialize_monitored_client)
        self.route('/snapshot', methods=["POST"])(self.receive_snapshot)
        super().run(*args, **kwargs)


if __name__ == '__main__':
    server = MonitorServer(__name__)
    server.run()
