import pytest

from duravoke import InMemoryKKV, PersistedKKV, JSONSerializer, Serializer


@pytest.mark.parametrize(
    ("data", "serializer"),
    [
        ({"name": "alpha", "count": 1}, JSONSerializer()),
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
        assert deserialized == data

        await kv.delete("primary", "secondary")
        assert await kv.get("primary", "secondary") is None
