import inspect
from typing import Callable, Coroutine, Any, TypeVar
from duravoke.duravoke_context import DuravokeContext
from duravoke.utils.methods import positional_arguments
from duravoke.kv import KeyedKeyValues
from duravoke.serializer import Serializer

T = TypeVar('T')

class Duravokable:

    def __init__(
        self,
        callable: Callable[..., Coroutine[Any, Any, T]], 
        duravoke_context: DuravokeContext,
        serializer: Serializer,
        kv: KeyedKeyValues,
    ):
        self.callable = callable
        self.duravoke_context = duravoke_context
        self.serializer = serializer
        self.kv = kv

    def __name__(self) -> str:
        return f"Duravokable({self.callable.__name__})"

    async def call_with_context(self, serializer: Serializer, kv: KeyedKeyValues, *args, **kwargs) -> T:
        duravoke_context = self.duravoke_context

        positional_args = positional_arguments(self.callable)
        func_kwargs = {arg: val for arg, val in zip(positional_args, args)}
        func_kwargs.update(kwargs)

        context_key = duravoke_context.parent_invocation_key.get("duravoker_root")
        invocation_key_suffix = duravoke_context.get_invocation_key_suffix(func_kwargs)
        invocation_key_stack = duravoke_context.get_invocation_stack()
        call_counters = duravoke_context.get_call_counters()
        invocation_key = duravoke_context.get_invocation_key(
            f"{self.callable.__module__}.{self.callable.__name__}",
            invocation_key_suffix,
            invocation_key_stack,
            call_counters,
        )
        stack_token, current_path_key = duravoke_context.push_invocation_key(
            invocation_key_stack, invocation_key
        )

        try:
            cached_result = await kv.get(context_key, invocation_key)
            if cached_result:
                return await serializer.deserialize(cached_result)

            # Set context for nested calls, then restore after execution
            token = duravoke_context.parent_invocation_key.set(invocation_key)
            try:
                result = self.callable(*args, **kwargs)
                # support both sync and async functions
                if inspect.isawaitable(result):
                    result = await result
                serialized_result = await serializer.serialize(result)
                # Save to the original context, not the one we just set
                await kv.set(context_key, invocation_key, serialized_result)
                return result
            finally:
                # Reset context to previous value
                duravoke_context.parent_invocation_key.reset(token)
        finally:
            # Always restore the previous stack (works for any depth).
            duravoke_context.invocation_key_stack.reset(stack_token)
            # Clear counters for this invocation's path to avoid leakage.
            duravoke_context.cleanup_call_counters(current_path_key)

    async def __call__(self, *args, **kwargs) -> T:
        return await self.call_with_context(self.serializer, self.kv, *args, **kwargs)
