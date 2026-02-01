from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
from pydantic import BaseModel
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


PydanticT = TypeVar('PydanticT', bound=BaseModel)

class PydanticSerializer(Serializer[PydanticT]):

    def __init__(self, model: Type[PydanticT]):
        self.model = model

    async def serialize(self, value: PydanticT) -> str:
        json_val = value.model_dump(mode="json")
        return await JSONSerializer().serialize(json_val)

    async def deserialize(self, serialized_value: str) -> PydanticT:
        json_val = await JSONSerializer().deserialize(serialized_value)
        return self.model.model_validate(json_val)
