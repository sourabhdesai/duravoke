from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
import json

T = TypeVar('T')

class Serializer(Generic[T], ABC):
    @abstractmethod
    async def serialize(self, value: T) -> str:
        pass

    @abstractmethod
    async def deserialize(self, serialized_value: str) -> T:
        pass

class JSONSerializer(Serializer[dict]):

    async def serialize(self, value: dict) -> str:
        json_val = json.dumps(value)
        return json.dumps({"value": json_val})

    async def deserialize(self, serialized_value: str) -> dict:
        json_val = json.loads(serialized_value)["value"]
        return json.loads(json_val)
