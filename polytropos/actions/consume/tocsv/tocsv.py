import csv
import os
from typing import Iterable, Tuple, Any, Optional, List, Dict, TextIO, Callable, Iterator

from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.descriptors.colnames import DescriptorBlockToColumnNames
from polytropos.ontology.schema import Schema

from polytropos.ontology.paths import PathLocator

from polytropos.actions.consume import Consume
from polytropos.actions.consume.tocsv.blocks import Block, BlockProduct
from polytropos.actions.consume.tocsv.descriptors import fromraw
from polytropos.ontology.composite import Composite

def _get_all_blocks(schema: Schema, columns: List[Dict]) -> List[Block]:
    as_block_value: AsBlockValue = AsBlockValue(schema)
    get_all_blocks: Callable = fromraw.GetAllBlocks(as_block_value)
    return get_all_blocks(columns)

def _get_all_column_names(schema: Schema, columns: List[Dict]) -> List[str]:
    spec_to_names: DescriptorBlockToColumnNames = DescriptorBlockToColumnNames(schema)
    get_all_column_names: Callable = fromraw.GetAllColumnNames(spec_to_names)
    return get_all_column_names(columns)

def _open_file(path_locator: Optional[PathLocator], filename: str) -> TextIO:
    assert path_locator is not None
    fh: TextIO = open(os.path.join(path_locator.conf, '../', filename), 'w')
    return fh

class ExportToCSV(Consume):
    def __init__(self, path_locator: Optional[PathLocator], schema: Schema, filename: str, columns: List):
        super(ExportToCSV, self).__init__(path_locator, schema)
        self.blocks: List[Block] = _get_all_blocks(schema, columns)
        self.column_names: List[str] = _get_all_column_names(schema, columns)
        self.fh: TextIO = _open_file(path_locator, filename)
        self.writer: Any = csv.writer(self.fh)

    def before(self) -> None:
        self.writer.writerow(self.column_names)

    def extract(self, composite: Composite) -> Iterator[List[Optional[Any]]]:
        render: BlockProduct = BlockProduct(composite, self.blocks)
        yield from render()

    def consume(self, extracts: Iterable[Tuple[str, Iterator[List[Optional[Any]]]]]) -> None:
        for composite_id, rows in extracts:
            self.writer.writerows(rows)

    def after(self) -> None:
        self.fh.close()

