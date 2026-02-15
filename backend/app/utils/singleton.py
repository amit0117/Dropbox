"""
Singleton metaclass using double-checked locking pattern.

Provides thread-safe singleton instantiation. Any class using this
metaclass will only ever have one instance created, regardless of
how many times it is instantiated or from how many threads.

Usage:
    class MyService(metaclass=SingletonMeta):
        def __init__(self):
            self.value = "initialized once"
"""

import threading

class SingletonMeta(type):

    _instances: dict = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
