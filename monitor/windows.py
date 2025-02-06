import asyncio
import os
from typing import List

import psutil
import wmi

from structures import ActiveProcess, ResourceUsage, MemoryUsage, Snapshot


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

        await asyncio.sleep(delay)


async def display_thread(q: asyncio.Queue[Snapshot]):
    while True:
        snapshot = await q.get()
        print(snapshot.active_processes)
        print(snapshot.resource_usage.cpu)
        print(snapshot.resource_usage.memory.percent, snapshot.resource_usage.memory.bytes)
        print("\n\n")


async def main():
    process_queue = asyncio.Queue()
    f = wmi.WMI()
    print("Monitoring processes...")

    await asyncio.gather(
        monitor_thread(f, process_queue, 1),
        display_thread(process_queue)
    )


if __name__ == '__main__':
    asyncio.run(main())
