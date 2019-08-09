import pytest

from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.type_translators import FolderTranslator


def test_translate_all_children_missing(translator, document, variable):
    translator.translate.return_value = {}

    type_translator = FolderTranslator(translator, document, variable, None)
    with pytest.raises(SourceNotFoundException):
        _ = type_translator()


def test_translate_all_children_none(translator, document, variable):
    translator.translate.return_value = {
        "folder": {
            "a": None,
            "b": None
        }
    }

    type_translator = FolderTranslator(translator, document, variable, None)
    assert type_translator() == {
        "folder": {
            "a": None,
            "b": None
        }
    }


def test_translate_with_folders(translator, document, variable):
    translator.translate.return_value = {
        "folder1": {
            "a": 1,
            "folder1.1": {
                "b": "b"
            }
        },
        "folder2": {
            "c": 2.3,
        },
    }

    type_translator = FolderTranslator(translator, document, variable, None)
    assert type_translator() == {
        "folder1": {
            "a": 1,
            "folder1.1": {
                "b": "b"
            }
        },
        "folder2": {
            "c": 2.3,
        },
    }

