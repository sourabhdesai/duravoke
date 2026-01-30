from typing import Any
from typing import Callable, TypeVar, Coroutine
from src.kv import KeyedKeyValues
from src.serializer import Serializer
from src.duravoke_context import DuravokeContext
from src.duravokable import Duravokable

T = TypeVar('T')

class Duravoke:

    def __init__(self, kv: KeyedKeyValues, serializer: Serializer):
        self.kv = kv
        self.serializer = serializer
        self.duravoke_context = DuravokeContext()

    def duravoke(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Duravokable:
        return Duravokable(func, self.duravoke_context, self.serializer, self.kv)
