import math
import os
from concurrent.futures import as_completed, Executor, ThreadPoolExecutor, Future
from concurrent.futures.process import ProcessPoolExecutor
from typing import Optional, List, Any, Iterable, Dict, TypeVar
from typing_extensions import Protocol

from tqdm import tqdm

MAX_PROCESS_POOL_CHUNK_SIZE = 10000

T = TypeVar('T')  # element type
R = TypeVar('R', covariant=True)  # result type


class Func(Protocol[T, R]):
    def __call__(self, __chunk: List[T], *args: Any) -> R: ...


def run_in_process_pool(func: Func[T, R], items: List[T], *args: Any, chunk_size: Optional[int] = None, workers_count: Optional[int] = None) -> Iterable[R]:
    if workers_count is not None and workers_count <= 0:
        raise ValueError("workers_count must be greater than 0")

    if len(items) == 0:
        return

    if workers_count is None:
        workers_count = os.cpu_count() or 1

    if chunk_size is None:
        chunk_size = math.ceil(len(items) / workers_count)
        if chunk_size > MAX_PROCESS_POOL_CHUNK_SIZE:
            chunk_size = MAX_PROCESS_POOL_CHUNK_SIZE

    executor = ProcessPoolExecutor(max_workers=workers_count)
    yield from _run_in_pool(executor, func, items, *args, chunk_size=chunk_size)


def run_in_thread_pool(func: Func[T, R], items: List[T], *args: Any, chunk_size: Optional[int] = None, workers_count: Optional[int] = None) -> Iterable[R]:
    if workers_count is not None and workers_count <= 0:
        raise ValueError("workers_count must be greater than 0")

    if len(items) == 0:
        return

    executor = ThreadPoolExecutor(max_workers=workers_count)
    yield from _run_in_pool(executor, func, items, *args, chunk_size=chunk_size)


def _run_in_pool(executor: Executor, func: Func[T, R], items: List[T], *args: Any, chunk_size: Optional[int] = None) -> Iterable[R]:
    if chunk_size is None:
        chunk_size = 1

    chunks: Iterable[List[T]] = _split_to_chunks(items, chunk_size)

    exceptions: List[BaseException] = []
    with executor:
        futures: Dict[Future, int] = {}
        for chunk in chunks:
            future = executor.submit(func, chunk, *args)
            futures[future] = len(chunk)
        with tqdm(total=len(items)) as pbar:
            for future in as_completed(set(futures.keys())):
                pbar.update(futures[future])
                del futures[future]
                e = future.exception()
                if e is not None:
                    exceptions.append(e)
                else:
                    yield future.result()
    if len(exceptions) > 0:
        raise exceptions[0]


def run_in_loop(func: Func[T, R], items: List[T], *args: Any, chunk_size: Optional[int] = None) -> Iterable[R]:
    if len(items) == 0:
        return

    if chunk_size is None:
        chunk_size = 1

    chunks: Iterable[List[T]] = _split_to_chunks(items, chunk_size)
    with tqdm(total=len(items)) as pbar:
        for chunk in chunks:
            result = func(chunk, *args)
            pbar.update(len(chunk))
            yield result


# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def _split_to_chunks(items: List[T], chunk_size: int) -> Iterable[List[T]]:
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]
