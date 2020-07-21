import os
from typing import TextIO, Optional, cast
import click
import logging

from polytropos.actions.consume.source_coverage import SourceCoverage
from polytropos.actions.translate import Translate
from polytropos.actions.translate.trace import Trace
from polytropos.ontology.schema import Schema

from polytropos.actions.consume.coverage import CoverageFile
from polytropos.ontology.context import Context
from polytropos.ontology.task import Task
from polytropos.ontology.variable import VariableId
from polytropos.tools.schema import treeview
from polytropos.tools.schema.catalog import variable_catalog
from polytropos.tools.schema.linkage import ExportLinkages
from polytropos.tools.schema.repair_sort import repair_sort_order
from polytropos.actions import register_all

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

register_all()


@click.group()
def cli() -> None:
    """Polytropos. Copyright (c) 2019 Applied Nonprofit Research."""
    pass


@cli.command()
@click.argument('data_path', type=click.Path(exists=True))
@click.argument('config_path', type=click.Path(exists=True))
@click.argument('task_name', type=str)
@click.option('--input_path', type=click.Path(exists=True))
@click.option('--output_path', type=click.Path(exists=False))
@click.option('--temp_path', type=click.Path(exists=False))
@click.option('--no_cleanup', is_flag=True)
@click.option('--chunk_size', type=click.INT)
def task(data_path: str, config_path: str, task_name: str, input_path: Optional[str], output_path: Optional[str], temp_path: Optional[str], no_cleanup: bool, chunk_size: Optional[int]) -> None:
    """Perform a Polytropos task."""
    with Context.build(config_path, data_path, input_dir=input_path, output_dir=output_path, temp_dir=temp_path, no_cleanup=no_cleanup, process_pool_chunk_size=chunk_size) as context:
        task = Task.build(context, task_name)
        task.run()


@cli.group()
def schema() -> None:
    """Commands for viewing and manipulating schemas."""
    pass


@schema.group()
def linkage() -> None:
    """Import and export translation linkages."""
    pass


@linkage.command(name="export")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('output_file', type=click.File('w'))
def linkage_export(schema_basepath: str, source_schema: str, target_schema: str, output_file: TextIO) -> None:
    """Export a translation linkage."""
    ExportLinkages.from_files(schema_basepath, source_schema, target_schema, output_file)


"""
@linkage.command(name="import")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('input_file', type=click.File('r'))
@click.option('-s', '--suffix', default="_revised", type=str)
def linkage_import(schema_basepath: str, source_schema: str, target_schema: str, input_file: TextIO, suffix: str) -> None:
    #Import a modified translation linkage and output it.
    ImportLinkages.from_files(schema_basepath, source_schema, target_schema, input_file, suffix)
"""


@schema.command()
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
@click.argument('output_file', type=click.File('w'))
def catalog(schema_basepath: str, schema_name: str, output_file: TextIO) -> None:
    """Export a CSV-formatted catalog of variables in a schema."""
    variable_catalog(schema_basepath, schema_name, output_file)


@schema.command(name="treeview")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
@click.option('--hide_ids', is_flag=True)
def schema_treeview(schema_basepath: str, schema_name: str, hide_ids: bool) -> None:
    """Output an ASCII tree representation of a schema to stdout."""
    treeview.print_from_files(schema_basepath, schema_name, hide_ids)


@schema.command(name="repair")
@click.argument('schema_path', type=click.Path(exists=True))
def schema_repair(schema_path: str) -> None:
    """Replaces the existing sort order in a schema (if any) with an arbitrary, but valid, sort order. No aspect of the
    old sort order will be preserved; the new order will be alphabetized by variable name."""
    repair_sort_order(schema_path)


@schema.command(name="validate")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
@click.option('--schema_source_name', type=str, default=None)
def schema_validate(schema_basepath: str, schema_name: str, schema_source_name: Optional[str]) -> None:
    """Validates a schema without doing any other work."""
    source: Optional[Schema] = None
    if schema_source_name is not None:
        source = Schema.load(schema_source_name, schema_basepath)
    Schema.load(schema_name, schema_basepath, source_schema=source)


@cli.command()
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
@click.argument('data_path', type=click.Path(exists=True))
@click.argument('output_prefix', type=str)
@click.option('--t-group', type=str, default=None, help="Variable ID of temporal grouping variable, if any.")
@click.option('--i-group', type=str, default=None, help="Variable ID of immutable grouping variable, if any.")
@click.option('--exclude_trivial', is_flag=True)
def coverage(schema_basepath: str, schema_name: str, data_path: str, output_prefix: str, t_group: Optional[str],
             i_group: Optional[str], exclude_trivial: bool) -> None:
    """Produce a coverage report consisting of four files: coverage and groups for each of immutable and temporal
    tracks."""
    with Context.build("", "", input_dir=data_path, schemas_dir=schema_basepath) as context:
        CoverageFile.standalone(context, schema_name, output_prefix, cast(Optional[VariableId], t_group), cast(Optional[VariableId], i_group), exclude_trivial)


@cli.command()
@click.argument('schemas_dir', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=False))
@click.option('--chunk_size', type=click.INT)
def trace(schemas_dir: str, source_schema: str, target_schema: str, input_dir: str, output_dir: str, chunk_size: Optional[int]) -> None:
    with Context.build("", "", input_dir=input_dir, output_dir=output_dir, schemas_dir=schemas_dir, process_pool_chunk_size=chunk_size) as context:
        Trace.standalone(context, source_schema, target_schema)


@cli.command()
@click.argument('schemas_dir', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=False))
def translate(schemas_dir: str, source_schema: str, target_schema: str, input_dir: str, output_dir: str) -> None:
    with Context.build("", "", input_dir=input_dir, output_dir=output_dir, schemas_dir=schemas_dir) as context:
        Translate.standalone(context, source_schema, target_schema)


@cli.command()
@click.argument('schemas_dir', type=click.Path(exists=True))
@click.argument('source_schema_name', type=str)
@click.argument('target_schema_name', type=str)
@click.argument('translate_dir', type=click.Path(exists=True))
@click.argument('trace_dir', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path(exists=False))
@click.option('--chunk_size', type=click.INT)
def source_coverage(schemas_dir: str, source_schema_name: str, target_schema_name: str, translate_dir: str, trace_dir: str, output_path: str,
                    chunk_size: Optional[int]) -> None:
    """Produce a source coverage report."""
    output_dir, output_filename = os.path.split(output_path)
    with Context.build("", "", output_dir=output_dir, schemas_dir=schemas_dir, clean_output_directory=False, process_pool_chunk_size=chunk_size) as context:
        SourceCoverage.standalone(context, translate_dir, trace_dir, source_schema_name, target_schema_name, output_filename)


if __name__ == "__main__":
    cli()
