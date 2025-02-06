from json import dumps
from typing import List


class ActiveProcess:
    _name: str
    _description: str
    _command: str
    _pid: int
    _creation_date: str
    _priority: int
    _thread_count: int

    def __init__(self, name: str, description: str, command: str, pid: int, creation_date: str, priority: int,
                 thread_count: int):
        self._name = name
        self._description = description
        self._command = command
        self._pid = pid
        self._creation_date = creation_date
        self._priority = priority
        self._thread_count = thread_count

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def command(self) -> str:
        return self._command

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def creation_date(self) -> str:
        return self._creation_date

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def thread_count(self) -> int:
        return self._thread_count

    def __str__(self) -> str:
        return dumps({
            'name': self.name,
            'description': self.description,
            'command': self.command,
            'pid': self.pid,
            'creation_date': self.creation_date,
            'priority': self.priority,
            'thread_count': self.thread_count
        })

    def __repr__(self) -> str:
        return self.__str__()


class MemoryUsage:
    _bytes: int
    _percent: float

    def __init__(self, bytes_used: int, percent: float):
        self._bytes = bytes_used
        self._percent = percent

    @property
    def bytes(self) -> int:
        return self._bytes

    @property
    def percent(self) -> float:
        return self._percent


class ResourceUsage:
    _cpu: float
    _memory: MemoryUsage

    def __init__(self, cpu_usage: float, memory_usage: MemoryUsage):
        self._cpu = cpu_usage
        self._memory = memory_usage

    @property
    def cpu(self) -> float:
        return self._cpu

    @property
    def memory(self) -> MemoryUsage:
        return self._memory


class Snapshot:
    _active_processes: List[ActiveProcess]
    _resource_usage: ResourceUsage

    def __init__(self, active_processes: List[ActiveProcess], resource_usage: ResourceUsage):
        self._active_processes = active_processes
        self._resource_usage = resource_usage

    @property
    def active_processes(self) -> List[ActiveProcess]:
        return self._active_processes

    @property
    def resource_usage(self) -> ResourceUsage:
        return self._resource_usage
