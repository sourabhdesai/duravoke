from typing import Any
from typing import Callable, TypeVar, Coroutine
from duravoke.kv import KeyedKeyValues
from duravoke.serializer import Serializer
from duravoke.duravoke_context import DuravokeContext
from duravoke.duravokable import Duravokable

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
