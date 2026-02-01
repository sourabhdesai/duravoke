from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator
from collections import defaultdict
import json
from contextlib import asynccontextmanager

class KeyedKeyValues(ABC):

    @abstractmethod
    async def get(self, primary_key: str, secondary_key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def set(self, primary_key: str, secondary_key: str, value: str) -> None:
        pass

    @abstractmethod
    async def delete(self, primary_key: str, secondary_key: str) -> None:
        pass

class InMemoryKKV(KeyedKeyValues):

    def __init__(self, store: dict[str, dict[str, dict[str, str]]] = None):
        self.store = defaultdict(dict)
        self.store.update(store or {})

    async def get(self, primary_key: str, secondary_key: str) -> Optional[str]:
        return self.store.get(primary_key, {}).get(secondary_key, None)

    async def set(self, primary_key: str, secondary_key: str, value: str) -> None:
        self.store[primary_key][secondary_key] = value

    async def delete(self, primary_key: str, secondary_key: str) -> None:
        del self.store[primary_key][secondary_key]


class PersistedKKV(KeyedKeyValues):
    def __init__(self, path: str):
        self.path = path

    async def load(self) -> dict:
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    async def save(self, store: dict) -> None:
        with open(self.path, "w") as f:
            json.dump(store, f, indent=4)

    @asynccontextmanager
    async def store_context(self) -> AsyncGenerator[InMemoryKKV, None]:
        kkv = InMemoryKKV(await self.load())
        try:
            yield kkv
        finally:
            await self.save(kkv.store)

    async def get(self, primary_key: str, secondary_key: str) -> Optional[str]:
        async with self.store_context() as kkv:
            return await kkv.get(primary_key, secondary_key)

    async def set(self, primary_key: str, secondary_key: str, value: str) -> None:
        async with self.store_context() as kkv:
            await kkv.set(primary_key, secondary_key, value)

    async def delete(self, primary_key: str, secondary_key: str) -> None:
        async with self.store_context() as kkv:
            await kkv.delete(primary_key, secondary_key)
