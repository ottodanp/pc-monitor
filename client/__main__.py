import asyncio

from aiohttp import ClientSession


async def main(host: str):
    auth_code = input("Enter the auth code: ")
    nickname = input("Enter the nickname: ")
    async with ClientSession() as session:
        async with session.get(f"http://{host}/init_client?nickname={nickname}&auth_code={auth_code}") as response:
            body = await response.json()

        client_id = body["id"]
        async with session.get(f"http://{host}/get_snapshot?id={client_id}") as response:
            print(await response.text())

        async with session.get(f"http://{host}/screen_grab?id={client_id}") as response:
            body = await response.read()
            with open("screenshot.jpg", "wb") as f:
                f.write(body)


if __name__ == "__main__":
    asyncio.run(main("127.0.0.1:5000"))
