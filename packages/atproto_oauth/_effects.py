import asyncio
import inspect
import time
import typing as t
from dataclasses import dataclass, field

T = t.TypeVar('T')


@dataclass(frozen=True)
class Call:
    """Request to call a function that does I/O. An awaitable result is awaited by the asynchronous runner."""

    func: t.Callable[..., t.Any]
    # arguments carry tokens and request bodies
    args: t.Tuple[t.Any, ...] = field(default=(), repr=False)
    kwargs: t.Dict[str, t.Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class Sleep:
    seconds: float


def call(func: t.Callable[..., t.Any], *args: t.Any, **kwargs: t.Any) -> Call:
    return Call(func, args, kwargs)


Effect = t.Union[Call, Sleep]
Flow = t.Generator[Effect, t.Any, T]


def perform(effect: Effect) -> t.Any:
    if isinstance(effect, Sleep):
        time.sleep(effect.seconds)
        return None

    return effect.func(*effect.args, **effect.kwargs)


async def perform_async(effect: Effect) -> t.Any:
    if isinstance(effect, Sleep):
        await asyncio.sleep(effect.seconds)
        return None

    result = effect.func(*effect.args, **effect.kwargs)
    if inspect.isawaitable(result):
        return await result

    return result


def run_flow(flow: Flow[T]) -> T:
    """Run a flow to completion, doing its I/O synchronously."""
    try:
        effect = next(flow)
        while True:
            try:
                result = perform(effect)
            except BaseException as e:  # noqa: BLE001
                effect = flow.throw(e)
            else:
                effect = flow.send(result)
    except StopIteration as stop:
        value: T = stop.value
        return value


async def run_flow_async(flow: Flow[T]) -> T:
    """Run a flow to completion, doing its I/O asynchronously."""
    try:
        effect = next(flow)
        while True:
            try:
                result = await perform_async(effect)
            except BaseException as e:  # noqa: BLE001
                effect = flow.throw(e)
            else:
                effect = flow.send(result)
    except StopIteration as stop:
        value: T = stop.value
        return value
