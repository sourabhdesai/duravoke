import random

from src.duravoke import Duravoke
from src.duravokable import Duravokable
from src.duravoke_context import DuravokeContext
from src.kv import InMemoryKKV
from src.serializer import JSONSerializer


async def test_simple_flow() -> None:
    kv = InMemoryKKV()
    duravoke = Duravoke(kv, JSONSerializer())

    @duravoke.duravoke
    async def flaky_task() -> str:
        if random.random() < 0.2:
            raise RuntimeError("flaky_task failed")
        return f"{random.randint(1, 100)}"

    @duravoke.duravoke
    async def serial(results: list[str]) -> list[str]:
        for _ in range(len(results), 10):
            result = await flaky_task()
            results.append(result)
        return results

    results: list[str] = []
    previous_results: list[str] = []
    num_attempts = 0
    while len(results) < 10 and num_attempts < 100:
        num_attempts += 1
        try:
            results = await serial(results)
        except RuntimeError:
            pass
        assert results[: len(previous_results)] == previous_results
        previous_results = results.copy()
    assert len(results) == 10
    assert num_attempts >= 1, "num_attempts should be at least 1"


async def test_complex_flow() -> None:
    kv = InMemoryKKV()
    duravoke = Duravoke(kv, JSONSerializer())

    @duravoke.duravoke
    async def dura_shuffle(items: list[str]) -> list[str]:
        random.shuffle(items)
        return items

    @duravoke.duravoke
    async def task_alpha() -> str:
        if random.random() < 0.1:
            raise RuntimeError("task_alpha failed")
        return f"alpha:{random.randint(1, 100)}"

    @duravoke.duravoke
    async def task_bravo() -> str:
        if random.random() < 0.1:
            raise RuntimeError("task_bravo failed")
        return f"bravo:{random.randint(1, 100)}"

    @duravoke.duravoke
    async def task_charlie() -> str:
        if random.random() < 0.1:
            raise RuntimeError("task_charlie failed")
        return f"charlie:{random.randint(1, 100)}"

    @duravoke.duravoke
    async def task_delta() -> str:
        if random.random() < 0.1:
            raise RuntimeError("task_delta failed")
        return f"delta:{random.randint(1, 100)}"

    @duravoke.duravoke
    async def complex_flow(results: list[str]) -> list[str]:
        tasks = [task_alpha, task_bravo, task_charlie, task_delta]
        task_names = [task.__name__ for task in tasks]
        task_names_to_tasks = {task_name: task for task_name, task in zip(task_names, tasks)}
        rng = random.Random(0)

        planned_order: list[str] = []
        for _ in range(3):
            round_names = task_names[:]
            rng.shuffle(round_names)
            planned_order.extend(round_names)

        for task_name in planned_order[len(results) :]:
            result = await task_names_to_tasks[task_name]()
            results.append(result)
        return results

    results = []
    previous_results = []
    num_attempts = 0
    while len(results) < 12 and num_attempts < 100:
        num_attempts += 1
        try:
            results = await complex_flow(results)
        except RuntimeError:
            pass
        assert results[: len(previous_results)] == previous_results
        previous_results = results.copy()
    assert len(results) == 12
    assert num_attempts >= 1, "num_attempts should be at least 1"


async def test_randomized_order_changes_break_cache() -> None:
    """
    This test checks that when the order of tasks is randomized, the cache is broken.
    This is because the cache is keyed by the order of tasks, so if the order is randomized,
    the cache will be broken.
    """
    kv = InMemoryKKV()
    duravoke = Duravoke(kv, JSONSerializer())
    counters: dict[str, int] = {"alpha": 0, "bravo": 0, "charlie": 0, "delta": 0}

    @duravoke.duravoke
    async def task_alpha() -> str:
        counters["alpha"] += 1
        return f"alpha:{counters['alpha']}"

    @duravoke.duravoke
    async def task_bravo() -> str:
        counters["bravo"] += 1
        return f"bravo:{counters['bravo']}"

    @duravoke.duravoke
    async def task_charlie() -> str:
        counters["charlie"] += 1
        return f"charlie:{counters['charlie']}"

    @duravoke.duravoke
    async def task_delta() -> str:
        counters["delta"] += 1
        return f"delta:{counters['delta']}"

    task_map = {
        "alpha": task_alpha,
        "bravo": task_bravo,
        "charlie": task_charlie,
        "delta": task_delta,
    }

    @duravoke.duravoke
    async def complex_flow(order: list[str]) -> list[str]:
        results: list[str] = []
        for name in order:
            results.append(await task_map[name]())
        return results

    order_one = ["alpha", "bravo", "charlie", "delta", "alpha", "bravo"]
    order_two = ["delta", "charlie", "bravo", "alpha", "delta", "charlie"]

    results_one = await complex_flow(order_one)
    results_two = await complex_flow(order_two)

    assert results_one != results_two
    assert counters == {"alpha": 3, "bravo": 3, "charlie": 3, "delta": 3}


async def test_duravokable_sync_callable_cached() -> None:
    kv = InMemoryKKV()
    serializer = JSONSerializer()
    context = DuravokeContext()
    call_count = {"count": 0}

    def sync_task() -> str:
        call_count["count"] += 1
        return f"sync:{call_count['count']}"

    duravokable = Duravokable(sync_task, context, serializer, kv)

    first = await duravokable()
    second = await duravokable()

    assert first == "sync:1"
    assert second == "sync:1"
    assert call_count["count"] == 1
