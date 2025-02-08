import asyncio
from os import mkdir
from os.path import isdir, isfile
from typing import Dict, Optional
from uuid import uuid4

from quart import Quart, request

from .util import hash_auth_code


class MonitoredClient:
    _id: str
    _auth_code: str
    _snapshots: asyncio.Queue

    def __init__(self, auth_code: str):
        self._id = str(uuid4())
        self._auth_code = auth_code
        self._snapshots = asyncio.Queue()

    @property
    def id(self) -> str:
        return self._id

    @property
    def auth_code(self) -> str:
        return self._auth_code

    @property
    def snapshots(self) -> asyncio.Queue:
        return self._snapshots

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

        nickname = request.args.get('nickname')
        if nickname is None:
            return "No nickname provided", 400

        client = MonitoredClient(hash_auth_code(auth_code))

        self._monitored_clients[nickname] = client
        return {"id": client.id}

    async def initialize_client(self):
        auth_code = request.args.get('auth_code')
        if auth_code is None:
            return "No auth code provided", 400

        nickname = request.args.get('nickname')
        if nickname is None:
            return "No nickname provided", 400

        client = self._monitored_clients.get(nickname)
        if client is None:
            return "Invalid nickname", 400

        if client.auth_code != hash_auth_code(auth_code):
            return "Invalid auth code", 400

        return {"id": client.id}

    async def receive_snapshot(self):
        args = request.args
        client_id = args.get('id')
        if client_id is None:
            return "No client id provided", 400

        client = self.find_client(client_id)
        if client is None:
            return "Invalid client id", 400

        files = await request.files
        body = await request.form
        image = files['file']
        if not isdir("image_grabs"):
            mkdir("image_grabs")

        await image.save(f"image_grabs/{client_id}.jpg")
        await client.snapshots.put(body)
        return {"status": "success"}

    async def send_snapshot(self):
        args = request.args
        client_id = args.get('id')
        if client_id is None:
            return "No client id provided", 400

        client = self.find_client(client_id)
        if client is None:
            return "Invalid client id", 400

        snapshot = await client.snapshots.get()
        return snapshot

    @staticmethod
    async def send_screen_grab():
        args = request.args
        client_id = args.get('id')
        if client_id is None:
            return "No client id provided", 400

        if not isfile(f"image_grabs/{client_id}.jpg"):
            return "No image available", 400

        with open(f"image_grabs/{client_id}.jpg", "rb") as f:
            image = f.read()

        return image

    def find_client(self, client_id) -> Optional[MonitoredClient]:
        for client in self._monitored_clients.values():
            if client.id == client_id:
                return client
        return None

    def run(self, *args, **kwargs):
        self.route('/init')(self.initialize_monitored_client)
        self.route('/init_client')(self.initialize_client)
        self.route('/snapshot', methods=["POST"])(self.receive_snapshot)
        self.route('/get_snapshot', methods=["GET"])(self.send_snapshot)
        self.route('/screen_grab', methods=["GET"])(self.send_screen_grab)
        super().run(*args, **kwargs)


if __name__ == '__main__':
    server = MonitorServer(__name__)
    server.run()
