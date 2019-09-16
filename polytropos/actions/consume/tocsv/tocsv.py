import csv
import os
from collections import deque
from typing import Iterable, Tuple, Any, Optional, List, Dict, TextIO, Callable, Iterator, Type, Deque, TYPE_CHECKING


from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.descriptors.colnames import DescriptorBlockToColumnNames
from polytropos.actions.filter import Filter
from polytropos.ontology.schema import Schema

from polytropos.ontology.context import Context

from polytropos.actions.consume import Consume
from polytropos.actions.consume.tocsv.blocks import Block, BlockProduct
from polytropos.actions.consume.tocsv.descriptors import fromraw
from polytropos.ontology.composite import Composite

if TYPE_CHECKING:
    from polytropos.actions.step import Step

def _get_all_blocks(schema: Schema, columns: List[Dict]) -> List[Block]:
    as_block_value: AsBlockValue = AsBlockValue(schema)
    get_all_blocks: Callable = fromraw.GetAllBlocks(as_block_value)
    return get_all_blocks(columns)

def _get_all_column_names(schema: Schema, columns: List[Dict]) -> List[str]:
    spec_to_names: DescriptorBlockToColumnNames = DescriptorBlockToColumnNames(schema)
    get_all_column_names: Callable = fromraw.GetAllColumnNames(spec_to_names)
    return get_all_column_names(columns)

def _open_file(context: Context, filename: str) -> TextIO:
    fh: TextIO = open(os.path.join(context.output_dir, filename), 'w')
    return fh

class ExportToCSV(Consume):
    def __init__(self, context: Context, schema: Schema, filename: str, columns: List,
                 filters: Optional[List]=None):
        super(ExportToCSV, self).__init__(context, schema)
        self.blocks: List[Block] = _get_all_blocks(schema, columns)
        self.column_names: List[str] = _get_all_column_names(schema, columns)
        self.fh: TextIO = _open_file(context, filename)
        self.writer: Any = csv.writer(self.fh)
        self.filters: List[Filter] = self._make_filters(filters)

    def _make_filters(self, filter_specs: Optional[List]) -> List[Filter]:
        if filter_specs is None:
            return []

        ret: List = []
        for filter_spec in filter_specs:  # type: Dict
            assert len(filter_spec) == 1
            for class_name, kwargs in filter_spec.items():  # type: str, Dict
                try:
                    the_filter: Step = Filter.build(context=self.context, schema=self.schema, name=class_name,
                                                    **kwargs)
                except Exception as e:
                    print("breakpoint")
                    raise e
                ret.append(the_filter)
        return ret

    def before(self) -> None:
        self.writer.writerow(self.column_names)

    def extract(self, composite: Composite) -> Iterator[List[Optional[Any]]]:
        for f in self.filters:
            if not f.passes(composite):
                return
            f.narrow(composite)

        render: BlockProduct = BlockProduct(composite, self.blocks)
        yield from render()

    def consume(self, extracts: Iterable[Tuple[str, Iterator[List[Optional[Any]]]]]) -> None:
        for composite_id, rows in extracts:
            self.writer.writerows(rows)

    def after(self) -> None:
        self.fh.close()

