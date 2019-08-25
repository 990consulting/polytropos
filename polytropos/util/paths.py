import functools
import logging
import os
from pathlib import Path
from typing import Iterator, Iterable
import textwrap

def find_all_composites(basepath: str) -> Iterator[str]:
    logging.info("Crawling %s for composites." % basepath)
    i: int = 0
    for filepath in Path(basepath).glob('**/*.json'):
        yield filepath.name.split(".")[0]
        i += 1
        if i % 1000 == 0:
            logging.info("Found {:,} composites in {}.".format(i, basepath))
    logging.info("Crawl complete. Found {:,} EINs in {}.".format(i, basepath))

@functools.lru_cache(maxsize=4194304)
def relpath_for(composite_id: str) -> str:
    chunks: Iterable[str] = textwrap.wrap(composite_id, 3)[:-1]
    return os.path.join(*chunks)
