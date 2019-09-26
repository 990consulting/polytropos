import csv
import json
import os
from typing import Iterable, Tuple, Any, Optional, List, Dict, TextIO, Callable, Iterator, TYPE_CHECKING


from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.descriptors.colnames import DescriptorBlockToColumnNames
from polytropos.actions.filter import Filter
from polytropos.ontology.schema import Schema

from polytropos.ontology.context import Context

from polytropos.actions.consume import Consume
from polytropos.actions.consume.tocsv.blocks import Block, BlockProduct
from polytropos.actions.consume.tocsv.descriptors import fromraw
from polytropos.ontology.composite import Composite
from polytropos.util.paths import relpath_for

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


class ExportToCSV(Consume):
    def __init__(self, context: Context, schema: Schema, filename: str, columns: List,
                 filters: Optional[List]=None):
        super(ExportToCSV, self).__init__(context, schema)
        self.blocks: List[Block] = _get_all_blocks(schema, columns)
        self.column_names: List[str] = _get_all_column_names(schema, columns)
        self.fh: TextIO = open(os.path.join(context.output_dir, filename), 'w')
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

    def extract(self, composite: Composite) -> Any:
        raise NotImplementedError

    def consume(self, extracts: Iterable[List[Any]]) -> None:
        for rows in extracts:
            self.writer.writerows(rows)

    def after(self) -> None:
        self.fh.close()

    def process_composites(self, composite_ids: Iterable[str], origin_dir: str) -> Iterable[Any]:
        extract = ExportToCSVExtract(self.schema, origin_dir, self.context.temp_dir, self.filters, self.blocks)
        return self.context.run_in_process_pool(extract.extract, list(composite_ids))


class ExportToCSVExtract:
    def __init__(self, schema: Schema, origin_dir: str, temp_dir: str, filters: List[Filter], blocks: List[Block]):
        self.schema = schema
        self.origin_dir = origin_dir
        self.temp_dir = temp_dir
        self.filters = filters
        self.blocks = blocks

    def extract(self, composite_ids: List[str]) -> List[List[Any]]:
        result: List[List[Any]] = []

        for composite_id in composite_ids:
            relpath: str = relpath_for(composite_id)
            with open(os.path.join(self.origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.schema, content, composite_id=composite_id)
            result.extend(self._process_composite(composite))

        return result

    def _process_composite(self, composite: Composite) -> Iterator[List[Any]]:
        for f in self.filters:
            if not f.passes(composite):
                return
            f.narrow(composite)

        render: BlockProduct = BlockProduct(composite, self.blocks)
        yield from render()
