from pydantic import BaseModel

from src.serializer import JSONSerializer, PydanticSerializer


class SampleModel(BaseModel):
    name: str
    count: int


async def test_json_serializer_roundtrip() -> None:
    serializer = JSONSerializer()
    payload = {"name": "alpha", "count": 1}

    serialized = await serializer.serialize(payload)
    assert isinstance(serialized, str)

    deserialized = await serializer.deserialize(serialized)
    assert deserialized == payload


async def test_pydantic_serializer_roundtrip() -> None:
    serializer = PydanticSerializer(SampleModel)
    payload = SampleModel(name="bravo", count=2)

    serialized = await serializer.serialize(payload)
    assert isinstance(serialized, str)

    deserialized = await serializer.deserialize(serialized)
    assert isinstance(deserialized, SampleModel)
    assert deserialized.model_dump() == payload.model_dump()
