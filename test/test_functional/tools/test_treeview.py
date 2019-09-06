import pytest

from polytropos.tools.schema import treeview
from textwrap import dedent

def test_source_schema(source_schema):
    expected: str = dedent("""
    temporal
     ╠═ 0 first_temporal_folder (Folder | source_t_folder_1)
     ║  ╠═ 0 some_text (Text | source_t_folder_text_1)
     ║  ╚═ 1 a_list (List | source_t_list_1)
     ║     ╠═ 0 some_text (Text | source_t_list_text_1)
     ║     ╚═ 1 a_keyed_list (KeyedList | source_t_keyed_list_1)
     ║        ╚═ 0 some_text (Text | source_t_keyed_list_text_1)
     ╚═ 0 second_temporal_folder (Folder | source_t_folder_2)
        ╠═ 0 some_text (Text | source_t_folder_text_2)
        ╚═ 1 a_list (List | source_t_list_2)
           ╠═ 0 some_text (Text | source_t_list_text_2)
           ╚═ 1 a_keyed_list (KeyedList | source_t_keyed_list_2)
              ╚═ 0 some_text (Text | source_t_keyed_list_text_2)

    immutable
     ╠═ 0 first_immutable_folder (Folder | source_i_folder_1)
     ║  ╠═ 0 some_text (Text | source_i_folder_text_1)
     ║  ╚═ 1 a_list (List | source_i_list_1)
     ║     ╠═ 0 some_text (Text | source_i_list_text_1)
     ║     ╚═ 1 a_keyed_list (KeyedList | source_i_keyed_list_1)
     ║        ╚═ 0 some_text (Text | source_i_keyed_list_text_1)
     ╚═ 0 second_immutable_folder (Folder | source_i_folder_2)
        ╠═ 0 some_text (Text | source_i_folder_text_2)
        ╚═ 1 a_list (List | source_i_list_2)
           ╠═ 0 some_text (Text | source_i_list_text_2)
           ╚═ 1 a_keyed_list (KeyedList | source_i_keyed_list_2)
              ╚═ 0 some_text (Text | source_i_keyed_list_text_2)
    """).strip()
    actual: str = treeview.as_ascii(source_schema)
    assert actual == expected

def test_target_schema(target_schema):
    expected: str = dedent("""
    temporal
     ╚═ 0 temporal_folder (Folder | target_t_folder)
        ╠═ 0 some_text (Text | target_t_folder_text)
        ╚═ 1 a_list (List | target_t_list)
           ╠═ 0 some_text (Text | target_t_list_text)
           ╚═ 1 a_keyed_list (KeyedList | target_t_keyed_list)
              ╚═ 0 some_text (Text | target_t_keyed_list_text)

    immutable
     ╚═ 0 immutable_folder (Folder | target_i_folder)
        ╠═ 0 some_text (Text | target_i_folder_text)
        ╚═ 1 a_list (List | target_i_list)
           ╠═ 0 some_text (Text | target_i_list_text)
           ╚═ 1 a_keyed_list (KeyedList | target_i_keyed_list)
              ╚═ 0 some_text (Text | target_i_keyed_list_text)
    """).strip()
    actual: str = treeview.as_ascii(target_schema)
    assert actual == expected