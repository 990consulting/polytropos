import math
import os
from concurrent.futures import as_completed, Executor, ThreadPoolExecutor, Future
from concurrent.futures.process import ProcessPoolExecutor
from typing import Optional, Callable, List, Any, Iterable, Dict

from tqdm import tqdm

MAX_PROCESS_POOL_CHUNK_SIZE = 10000


def run_on_process_pool(func: Callable, items: List[Any], *args: Any, chunk_size: Optional[int] = None, workers_count: Optional[int] = None) -> Iterable[Any]:
    if len(items) == 0:
        return

    if workers_count is None:
        workers_count = os.cpu_count() or 1

    if chunk_size is None:
        chunk_size = math.ceil(len(items) / workers_count)
        if chunk_size > MAX_PROCESS_POOL_CHUNK_SIZE:
            chunk_size = MAX_PROCESS_POOL_CHUNK_SIZE

    executor = ProcessPoolExecutor(max_workers=workers_count)
    yield from run_on_pool(executor, func, items, *args, chunk_size=chunk_size)


def run_on_thread_pool(func: Callable, items: List[Any], *args: Any, chunk_size: Optional[int] = None, workers_count: Optional[int] = None) -> Iterable[Any]:
    if len(items) == 0:
        return

    executor = ThreadPoolExecutor(max_workers=workers_count)
    yield from run_on_pool(executor, func, items, *args, chunk_size=chunk_size)


def run_on_pool(executor: Executor, func: Callable, items: List[Any], *args: Any, chunk_size: Optional[int] = None) -> Iterable[Any]:
    if len(items) == 0:
        return

    if chunk_size is None:
        chunk_size = 1

    chunks: Iterable[List[Any]] = split_to_chunks(list(items), chunk_size)

    exceptions: List[BaseException] = []
    with executor:
        futures: Dict[Future, int] = {}
        for chunk in chunks:
            future = executor.submit(func, chunk, *args)
            futures[future] = len(chunk)
        with tqdm(total=len(items)) as pbar:
            for future in as_completed(futures.keys()):
                pbar.update(futures[future])
                e = future.exception()
                if e is not None:
                    exceptions.append(e)
                else:
                    yield future.result()
    if len(exceptions) > 0:
        raise exceptions[0]


# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def split_to_chunks(items: List[Any], chunk_size: int) -> Iterable[List[Any]]:
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]
