import functools
import logging
import os
from typing import Iterator, Iterable
import textwrap

def _use_scandir(basepath: str, outer: bool = False) -> Iterator[str]:
    if outer is True:
        logging.info("Crawling %s for composites." % basepath)
    i: int = 0
    for obj in os.scandir(path=basepath):  # type: os.DirEntry
        if obj.is_dir():
            for child_obj in _use_scandir(obj.path):
                yield child_obj
                i += 1
                if outer is True and i % 1000 == 0:
                    logging.info("Found {:,} composites in {}.".format(i, basepath))
        elif obj.is_file():
            fn: str = str(obj.name)
            if fn.endswith(".json"):
                yield fn[:-5]
                i += 1
                if outer is True and i % 1000 == 0:
                    logging.info("Found {:,} composites in {}.".format(i, basepath))
    if outer is True:
        logging.info("Crawl complete. Found {:,} EINs in {}.".format(i, basepath))

def find_all_composites(basepath: str) -> Iterator[str]:
    yield from _use_scandir(basepath, outer=True)

@functools.lru_cache(maxsize=4194304)
def relpath_for(composite_id: str) -> str:
    try:
        chunks: Iterable[str] = textwrap.wrap(composite_id, 3)[:-1]
        return os.path.join(*chunks)
    except Exception as e:
        print("breakpoint")
        raise e
