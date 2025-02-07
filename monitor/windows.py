import asyncio
import os
from base64 import b64encode
from json import dumps
from typing import List

import psutil
import wmi
from PIL import ImageGrab
from aiohttp import ClientSession, FormData

from structures import ActiveProcess, ResourceUsage, MemoryUsage, Snapshot
from util import make_directory, get_latest_image_hash


def get_avg_cpu_usage() -> float:
    load1, load5, load15 = psutil.getloadavg()
    return (load15 / os.cpu_count()) * 100


def get_memory_usage() -> MemoryUsage:
    bytes_used = psutil.virtual_memory()[3]
    percent_used = psutil.virtual_memory()[2]

    return MemoryUsage(bytes_used, percent_used)


def get_active_processes(f: wmi.WMI) -> List[ActiveProcess]:
    return [
        ActiveProcess(
            process.Name,
            process.Description,
            process.CommandLine,
            process.ProcessId,
            process.CreationDate,
            process.Priority,
            process.ThreadCount
        ) for process in f.Win32_Process()
    ]


async def monitor_thread(f: wmi.WMI, q: asyncio.Queue[Snapshot], delay: int):
    while True:
        await q.put(
            Snapshot(
                get_active_processes(f),
                ResourceUsage(
                    get_avg_cpu_usage(),
                    get_memory_usage(),
                )
            )
        )

        get_screen_grab()
        await asyncio.sleep(delay)


def get_screen_grab():
    make_directory("image_grabs")
    snapshot = ImageGrab.grab()
    save_path = "image_grabs\\snapshot.jpg"
    snapshot.save(save_path)


async def screen_grab_thread(delay: int):
    while True:
        get_screen_grab()
        await asyncio.sleep(delay)


async def display_thread(q: asyncio.Queue[Snapshot], session: ClientSession, host: str, screen_grab_path: str, client_id: str):
    image_hash = ""

    while True:
        snapshot = await q.get()
        payload = snapshot.as_payload()
        new_hash = get_latest_image_hash(screen_grab_path)
        form_data = FormData()

        if new_hash != image_hash:
            f = open(screen_grab_path, "rb")
            form_data.add_field("file", f, filename=screen_grab_path, content_type="image/jpeg")

            image_hash = new_hash

        form_data.add_field("json", dumps(payload))

        async with session.post(
                f'http://{host}/snapshot?id={client_id}',
                data=form_data
        ) as response:
            print(await response.text())

        await asyncio.sleep(1)


async def main(process_queue: asyncio.Queue[Snapshot], host: str, client_id: str):
    f = wmi.WMI()
    print("Monitoring processes...")

    loop = asyncio.get_event_loop()

    async with ClientSession() as session:
        await asyncio.gather(
            monitor_thread(f, process_queue, 1),
            display_thread(process_queue, session, host, "image_grabs\\snapshot.jpg", client_id),
            screen_grab_thread(10)
        )

    loop.run_forever()
