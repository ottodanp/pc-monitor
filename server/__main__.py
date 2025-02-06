from quart import Quart


class MonitorServer(Quart):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def receive_snapshot(self):
        return "hi"

    def run(self, *args, **kwargs):
        self.route('/snapshot', methods=['POST'])(self.receive_snapshot)
        super().run(*args, **kwargs)


if __name__ == '__main__':
    server = MonitorServer(__name__)
    server.run()
