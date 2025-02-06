from os import name
import asyncio


async def main():
    if name == 'nt':
        from monitor.windows import main as runner
    else:
        from monitor.linux import main as runner

    await runner()


if __name__ == '__main__':
    asyncio.run(main())
