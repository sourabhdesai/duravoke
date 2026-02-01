from duravoke import JSONSerializer

async def test_json_serializer_roundtrip() -> None:
    serializer = JSONSerializer()
    payload = {"name": "alpha", "count": 1}

    serialized = await serializer.serialize(payload)
    assert isinstance(serialized, str)

    deserialized = await serializer.deserialize(serialized)
    assert deserialized == payload
