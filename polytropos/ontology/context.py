import logging
import os
import shutil
from dataclasses import dataclass
from typing import Optional, Any, Type, List, Iterable, TypeVar, Callable

from polytropos.util.futures import run_in_process_pool, run_in_thread_pool, run_in_loop, Func

T = TypeVar('T')  # element type
R = TypeVar('R', covariant=True)  # result type

@dataclass
class Context:
    """Context"""
    conf_dir: str
    schemas_dir: str
    lookups_dir: str
    entities_input_dir: str
    entities_output_dir: str
    output_dir: str
    temp_dir: str
    no_cleanup: bool
    process_pool_chunk_size: int
    legacy_mode: bool
    steppable_mode: bool

    @classmethod
    def build(cls, conf_dir: str, data_dir: str, input_dir: Optional[str] = None, output_dir: Optional[str] = None, schemas_dir: Optional[str] = None,
              temp_dir: Optional[str] = None, no_cleanup: bool = False,
              process_pool_chunk_size: Optional[int] = None, steppable_mode: bool = False) -> "Context":

        entities_input_dir = input_dir or os.path.join(data_dir, 'entities')
        entities_output_dir = output_dir or entities_input_dir

        if output_dir:
            try:
                logging.debug("Attempting to remove old output directory, if it exists.")
                shutil.rmtree(output_dir)
                logging.debug("Old output directory removed.")
            except FileNotFoundError:
                logging.debug("No old output directory.")

            os.makedirs(output_dir)
            temp_dir = temp_dir or os.path.join(output_dir, '_tmp')
        else:
            output_dir = os.path.join(conf_dir, "..") if conf_dir else "."
            temp_dir = temp_dir or os.path.join(data_dir, '_tmp')

        os.makedirs(temp_dir, exist_ok=True)

        return cls(conf_dir=conf_dir,
                   schemas_dir=schemas_dir or os.path.join(conf_dir, 'schemas'),
                   lookups_dir=os.path.join(data_dir, 'lookups'),
                   entities_input_dir=entities_input_dir,
                   entities_output_dir=entities_output_dir,
                   output_dir=output_dir,
                   temp_dir=temp_dir,
                   no_cleanup=no_cleanup,
                   process_pool_chunk_size=process_pool_chunk_size if process_pool_chunk_size is not None else 1000,
                   legacy_mode=input_dir is None,
                   steppable_mode=steppable_mode)

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Type, exc_val: Any, exc_tb: Any) -> None:
        if not self.no_cleanup:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_in_process_pool(self, func: Callable[..., R], items: List[T], *args: Any, chunk_size: Optional[int] = None, workers_count: Optional[int] = None) -> Iterable[R]:  # func: Func[T,R] doesn't work currently (MyPy issue)
        if self.steppable_mode:
            return run_in_loop(func, items, *args, chunk_size=chunk_size)

        if chunk_size is None:
            chunk_size = self.process_pool_chunk_size

        return run_in_process_pool(func, items, *args, chunk_size=chunk_size, workers_count=workers_count)

    def run_in_thread_pool(self, func: Callable[..., R], items: List[T], *args: Any, chunk_size: Optional[int] = None, workers_count: Optional[int] = None) -> Iterable[R]:  # func: Func[T,R] doesn't work currently (MyPy issue)
        if self.steppable_mode:
            return run_in_loop(func, items, *args, chunk_size=chunk_size)

        return run_in_thread_pool(func, items, *args, chunk_size=chunk_size, workers_count=workers_count)
