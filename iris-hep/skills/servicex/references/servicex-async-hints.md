# ServiceX Async Hints

Load this only when async execution is explicitly requested.

## Async `deliver_async` with timeout

Use `asyncio.wait_for(...)` to bound runtime and keep `ignore_local_cache=True`
behavior explicit.

```python
import asyncio
import inspect
from typing import Any

from servicex import ServiceXSpec

try:
    from servicex import deliver_async as sx_deliver_async
except ImportError:
    sx_deliver_async = None


async def run_deliver_async(spec: ServiceXSpec, timeout_seconds: int = 600) -> Any:
    if sx_deliver_async is None:
        raise RuntimeError("deliver_async is not available in this servicex version")

    async def _invoke() -> Any:
        result = sx_deliver_async(
            spec,
            ignore_local_cache=True,
        )

        # Version compatibility: some releases return an awaitable directly,
        # others return an object exposing .wait().
        if inspect.isawaitable(result):
            return await result

        wait_method = getattr(result, "wait", None)
        if callable(wait_method):
            waited = wait_method()
            if inspect.isawaitable(waited):
                return await waited
            return waited

        return result

    return await asyncio.wait_for(_invoke(), timeout=timeout_seconds)
```

## Version compatibility guidance

- Some `servicex` versions expose only `deliver` and not top-level
  `deliver_async`.
- When async APIs are unavailable, use sync `deliver` fallback (and for Linux
  timeout behavior, use the sync timeout recipe in `servicex-hints.md`).
