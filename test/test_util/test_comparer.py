from polytropos.util.compare import compare


def test_equality():
    nested_data = {
        'asdgdsa': [1, 3, 4, {}],
        'adgnw': {'asldfn': 'asldlgkn', 'asndf': 1.0, 'askdf': '1'},
        'gane': 'lakdng',
        'asdlklvkn': 1,
        'aksdvf': 1.0,
        'asgn': {'alsdkvkn': {'akvn': [], 'alsd': 2.2}}
    }
    assert compare(nested_data, nested_data)


def test_similar():
    data1 = {'': {'': [{'': 1.0}]}}
    data2 = {'': {'': [{'': 1.0000000000001}]}}
    assert compare(data1, data2)


def test_not_similar():
    data1 = {'': {'': [{'': 1.0}]}}
    data2 = {'': {'': [{'': 1.00000001}]}}
    assert not compare(data1, data2)


def test_int_float():
    data1 = {'': {'': [{'': 1}]}}
    data2 = {'': {'': [{'': 1.0000000000001}]}}
    assert compare(data1, data2)
