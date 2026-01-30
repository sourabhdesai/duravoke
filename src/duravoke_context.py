import hashlib
from typing import Any
from contextvars import ContextVar
import json

class DuravokeContext:

    def __init__(self):
        self.parent_invocation_key: ContextVar[str] = ContextVar("parent_invocation_key")
        self.invocation_key_stack: ContextVar[list[str]] = ContextVar(
            "invocation_key_stack"
        )
        self.call_counters: ContextVar[dict[str, int]] = ContextVar(
            "call_counters"
        )

    def get_invocation_key_suffix(self, func_kwargs: dict[str, Any]) -> str:
        return self.hash_str(json.dumps(func_kwargs, sort_keys=True))

    def get_invocation_stack(self) -> list[str]:
        invocation_key_stack = self.invocation_key_stack.get(None)
        if invocation_key_stack is None:
            invocation_key_stack = []
            self.invocation_key_stack.set(invocation_key_stack)
        return invocation_key_stack

    def get_call_counters(self) -> dict[str, int]:
        call_counters = self.call_counters.get(None)
        if call_counters is None:
            call_counters = {}
            self.call_counters.set(call_counters)
        return call_counters

    def get_invocation_key(
        self,
        func_name: str,
        invocation_key_suffix: str,
        invocation_key_stack: list[str],
        call_counters: dict[str, int],
    ) -> str:
        if invocation_key_stack:
            stack_path = "|".join(invocation_key_stack)
            parent_path_key = self.hash_str(stack_path)
            call_index = call_counters.get(parent_path_key, 0)
            call_counters[parent_path_key] = call_index + 1
            return f"{func_name}:{parent_path_key}:{call_index}:{invocation_key_suffix}"
        return f"{func_name}:{invocation_key_suffix}"

    def push_invocation_key(self, invocation_key_stack: list[str], invocation_key: str):
        new_stack = invocation_key_stack + [invocation_key]
        stack_token = self.invocation_key_stack.set(new_stack)
        current_path_key = self.hash_str("|".join(new_stack))
        return stack_token, current_path_key

    def cleanup_call_counters(self, current_path_key: str) -> None:
        call_counters = self.call_counters.get(None)
        if call_counters is not None:
            call_counters.pop(current_path_key, None)

    def hash_str(self, string: str) -> str:
        # Use deterministic hash (SHA-256) for consistent hashing across runs
        # The hash is deterministic: same input always produces same output
        hash_obj = hashlib.sha256(string.encode('utf-8'))
        # Convert hex digest to integer string for consistent representation
        return str(int(hash_obj.hexdigest(), 16))
