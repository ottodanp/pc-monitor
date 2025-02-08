import asyncio
from os import name
from typing import Tuple

from aiohttp import ClientSession

from util import generate_auth_code, LoopPolicy


async def initialize_monitored_client(session: ClientSession, host: str, nickname: str) -> Tuple[str, str]:
    auth_code = generate_auth_code()

    async with session.get(f'http://{host}/init?auth_code={auth_code}&nickname={nickname}') as response:
        data = await response.json()
        return data['id'], auth_code


async def main():
    if name == 'nt':
        from monitor.windows import main as runner
    else:
        from monitor.linux import main as runner

    nickname = input("Enter the nickname: ")
    process_queue = asyncio.Queue()
    async with ClientSession() as session:
        client_id, auth_code = await initialize_monitored_client(session, "127.0.0.1:5000", nickname)

    print("Enter the following auth code on the client to begin monitoring")
    print("Auth Code: ", auth_code)
    await runner(process_queue, "127.0.0.1:5000", client_id)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(LoopPolicy())
    asyncio.run(main())
