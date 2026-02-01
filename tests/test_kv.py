import pytest
from pydantic import BaseModel

from src.kv import InMemoryKKV, PersistedKKV
from src.serializer import JSONSerializer, PydanticSerializer, Serializer


class SampleModel(BaseModel):
    name: str
    count: int


@pytest.mark.parametrize(
    ("data", "serializer"),
    [
        ({"name": "alpha", "count": 1}, JSONSerializer()),
        (SampleModel(name="bravo", count=2), PydanticSerializer(SampleModel)),
    ],
)
async def test_kv_roundtrip_with_serializers(tmp_path, data, serializer: Serializer):
    kvs = [
        InMemoryKKV(),
        PersistedKKV(str(tmp_path / "kkv.json")),
    ]

    for kv in kvs:
        serialized = await serializer.serialize(data)
        await kv.set("primary", "secondary", serialized)

        cached = await kv.get("primary", "secondary")
        assert cached == serialized

        deserialized = await serializer.deserialize(cached)
        if isinstance(deserialized, BaseModel):
            assert deserialized.model_dump() == data.model_dump()
        else:
            assert deserialized == data

        await kv.delete("primary", "secondary")
        assert await kv.get("primary", "secondary") is None
