import pytest

def test_encode_named_list_trivial():
    """No mappings, no content"""
    pytest.fail()

def test_encode_named_list_empty_content():
    """Mappings present, no content."""
    pytest.fail()

def test_encode_named_list():
    """Both mappings and content present."""
    pytest.fail()

def test_encode_unmapped_content_raises():
    """If a content named_list item contains a field without a mapping, raise."""
    pytest.fail()

def test_encode_missing_content_skips():
    """If something isn't present in a content named list item that is defined in the mappings, skip it."""
    pytest.fail()

def test_encode_null_content():
    """Content that is explicitly null is encoded."""
    pytest.fail()

def test_decode_named_list_trivial():
    """No mappings, no content"""
    pytest.fail()

def test_decode_named_list_empty_content():
    """Mappings present, no content."""
    pytest.fail()

def test_decode_named_list():
    """Both mappings and content present."""
    pytest.fail()

def test_decode_unmapped_content_raises():
    """If a content named list item contains a field without a mapping, raise."""
    pytest.fail()

def test_decode_missing_content_skips():
    """If something isn't present in a content named list item that is defined in the mappings, skip it."""
    pytest.fail()

def test_decode_null_content():
    """Content that is explicitly null is decoded."""
    pytest.fail()
