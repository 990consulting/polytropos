import os
from typing import List, Tuple, Iterable, cast, Dict, Callable
import json

import pytest

from polytropos.actions.consume.sourcecoverage.crawl import Crawl
from polytropos.actions.consume.sourcecoverage.result import SourceCoverageResult
from polytropos.ontology.schema import Schema

def test_primitive_in_root_two_periods(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {"target_t_root_text_1": "lorem"},
        "201112": {"target_t_root_text_1": "ipsum"}
    }
    trace: Dict = {
        "201012": {"target_t_root_text_1": "source_t_root_text_1_1"},
        "201112": {"target_t_root_text_1": "source_t_root_text_1_1"}
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_root_text_1_1", "target_t_root_text_1", 2)
    ]
    do_crawl_test(translation, trace, expected)

def test_primitive_in_root_two_periods_one_none(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {"target_t_root_text_1": None},
        "201112": {"target_t_root_text_1": "ipsum"}
    }
    trace: Dict = {
        "201012": {"target_t_root_text_1": "source_t_root_text_1_1"},
        "201112": {"target_t_root_text_1": "source_t_root_text_1_1"}
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_root_text_1_1", "target_t_root_text_1", 1)
    ]
    do_crawl_test(translation, trace, expected)

@pytest.mark.parametrize("data_type, trivial, nontrivial", [
    ("Text", "", "foo"),
    ("Integer", 0, 1),
    ("Currency", 0, 1),
    ("Decimal", 0.0, 1.0),
    ("Integer", 0, -1),
    ("Currency", 0, -1),
    ("Decimal", 0.0, -1.0)
])
def test_primitive_in_root_two_periods_one_trivial(do_crawl_test, data_type, trivial, nontrivial) -> None:
    source: str = "source_t_root_{}_1_1".format(data_type.lower())
    target: str = "target_t_root_{}_1".format(data_type.lower())

    translation: Dict = {
        "201012": {target: trivial},
        "201112": {target: nontrivial}
    }
    trace: Dict = {
        "201012": {target: source},
        "201112": {target: source}
    }
    expected: List[Tuple[str, str, int]] = [
        (source, target, 1)
    ]
    do_crawl_test(translation, trace, expected, data_type=data_type)

def test_primitive_in_folder_two_periods(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {
            "target_t_folder": {
                "target_text_1": "lorem"
            }
        },
        "201112": {
            "target_t_folder": {
                "target_text_1": "ipsum"
            }
        }
    }
    trace: Dict = {
        "201012": {
            "target_t_folder": {
                "target_text_1": "source_t_folder_text_1_1"
            }
        },
        "201112": {
            "target_t_folder": {
                "target_text_1": "source_t_folder_text_1_1"
            }
        }
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_folder_text_1_1", "target_t_folder_text_1", 2)
    ]
    do_crawl_test(translation, trace, expected)

def test_primitive_in_list_two_periods(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_text_1": "lorem"
                    }
                ]
            }
        },
        "201112": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_text_1": "ipsum"
                    }
                ]
            }
        }
    }
    trace: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_text_1": "source_t_list_text_1_1"
                    }
                ]
            }
        },
        "201112": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_text_1": "source_t_list_text_1_1"
                    }
                ]
            }
        }
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_list_text_1_1", "target_t_list_text_1", 2)
    ]
    do_crawl_test(translation, trace, expected)

def test_primitive_in_list_two_values_one_period(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_text_1": "lorem"
                    },
                    {
                        "target_text_1": "ipsum"
                    }
                ]
            }
        }
    }
    trace: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_text_1": "source_t_list_text_1_1"
                    },
                    {
                        "target_text_1": "source_t_list_text_1_1"
                    }
                ]
            }
        }
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_list_text_1_1", "target_t_list_text_1", 2)
    ]
    do_crawl_test(translation, trace, expected)

def test_primitive_in_keyed_list_two_values_one_period_one_list_item(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "red": {
                                "target_text_1": "lorem"
                            },
                            "blue": {
                                "target_text_1": "ipsum"
                            }
                        }
                    }
                ]
            }
        }
    }
    trace: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "red": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            },
                            "blue": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            }
                        }
                    }
                ]
            }
        }
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_keyed_list_text_1_1", "target_t_keyed_list_text_1", 2)
    ]
    do_crawl_test(translation, trace, expected)

def test_primitive_in_keyed_list_four_values_one_period_two_list_items(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "red": {
                                "target_text_1": "lorem"
                            },
                            "blue": {
                                "target_text_1": "ipsum"
                            }
                        }
                    },
                    {
                        "target_keyed_list": {
                            "green": {
                                "target_text_1": "lorem"
                            },
                            "purple": {
                                "target_text_1": "ipsum"
                            }
                        }
                    }
                ]
            }
        }
    }
    trace: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "red": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            },
                            "blue": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            }
                        }
                    },
                    {
                        "target_keyed_list": {
                            "green": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            },
                            "purple": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            }
                        }
                    }
                ]
            }
        }
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_keyed_list_text_1_1", "target_t_keyed_list_text_1", 4)
    ]
    do_crawl_test(translation, trace, expected)

def test_primitive_in_keyed_list_four_values_two_periods_one_list_item(do_crawl_test) -> None:
    translation: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "red": {
                                "target_text_1": "lorem"
                            },
                            "blue": {
                                "target_text_1": "ipsum"
                            }
                        }
                    }
                ]
            }
        },
        "201112": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "green": {
                                "target_text_1": "lorem"
                            },
                            "purple": {
                                "target_text_1": "ipsum"
                            }
                        }
                    }
                ]
            }
        }
    }

    trace: Dict = {
        "201012": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "red": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            },
                            "blue": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            }
                        }
                    }
                ]
            }
        },
        "201112": {
            "target_t_folder": {
                "target_list": [
                    {
                        "target_keyed_list": {
                            "green": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            },
                            "purple": {
                                "target_text_1": "source_t_keyed_list_text_1_1"
                            }
                        }
                    }
                ]
            }
        }
    }
    expected: List[Tuple[str, str, int]] = [
        ("source_t_keyed_list_text_1_1", "target_t_keyed_list_text_1", 4)
    ]

    do_crawl_test(translation, trace, expected)