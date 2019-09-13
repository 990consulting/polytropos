"""This is a regression test for a bug in which lists that had two sources, only one of which existed in the data,
returned empty."""
from collections import OrderedDict
from typing import Tuple, Dict, Any

import pytest

from polytropos.actions.translate import Translator
from polytropos.ontology.track import Track

@pytest.fixture()
def source() -> Tuple[Dict, Dict]:
    doc: Dict = {
        "e_file": {
            "Return": {
                "ReturnData": {
                    "IRS990": {
                        "Form990PartVIISectionAGrp": [
                            {
                                "AverageHoursPerWeekRt": "1.00",
                                "IndividualTrusteeOrDirectorInd": "X",
                                "OtherCompensationAmt": "0",
                                "PersonNm": "JOHN DOE",
                                "ReportableCompFromOrgAmt": "0",
                                "ReportableCompFromRltdOrgAmt": "0",
                                "TitleTxt": "BOARD MEMBER"
                            },
                            {
                                "AverageHoursPerWeekRt": "40.00",
                                "OtherCompensationAmt": "50000",
                                "PersonNm": "JANE SMITH",
                                "ReportableCompFromOrgAmt": "100000",
                                "ReportableCompFromRltdOrgAmt": "10000",
                                "TitleTxt": "DIRECTOR OF ENGINEERING"
                            }
                        ]
                    }
                }
            }
        }
    }

    spec: Dict = {
        "origin_temporal_000263": {
            "data_type": "Folder",
            "name": "e_file",
            "sort_order": 0
        },
        "origin_temporal_000264": {
            "data_type": "Folder",
            "name": "Return",
            "parent": "origin_temporal_000263",
            "sort_order": 0
        },
        "origin_temporal_000265": {
            "data_type": "Folder",
            "name": "ReturnData",
            "parent": "origin_temporal_000264",
            "sort_order": 0
        },
        "origin_temporal_000266": {
            "data_type": "Folder",
            "name": "IRS990",
            "parent": "origin_temporal_000265",
            "sort_order": 0
        },
        "origin_temporal_000413": {
            "data_type": "List",
            "name": "Form990PartVIISectionA",
            "parent": "origin_temporal_000266",
            "sort_order": 0
        },
        "origin_temporal_000414": {
            "data_type": "Text",
            "name": "AverageHoursPerWeek",
            "parent": "origin_temporal_000413",
            "sort_order": 0
        },
        "origin_temporal_000415": {
            "data_type": "Text",
            "name": "NamePerson",
            "parent": "origin_temporal_000413",
            "sort_order": 1
        },
        "origin_temporal_000416": {
            "data_type": "Unary",
            "name": "Officer",
            "parent": "origin_temporal_000413",
            "sort_order": 2
        },
        "origin_temporal_000417": {
            "data_type": "Currency",
            "name": "OtherCompensation",
            "parent": "origin_temporal_000413",
            "sort_order": 3
        },
        "origin_temporal_000418": {
            "data_type": "Currency",
            "name": "ReportableCompFromOrganization",
            "parent": "origin_temporal_000413",
            "sort_order": 4
        },
        "origin_temporal_000419": {
            "data_type": "Currency",
            "name": "ReportableCompFromRelatedOrgs",
            "parent": "origin_temporal_000413",
            "sort_order": 5
        },
        "origin_temporal_000420": {
            "data_type": "Text",
            "name": "Title",
            "parent": "origin_temporal_000413",
            "sort_order": 6
        },
        "origin_temporal_001067": {
            "data_type": "Text",
            "name": "AverageHoursPerWeekRelated",
            "parent": "origin_temporal_000413",
            "sort_order": 7
        },
        "origin_temporal_001230": {
            "data_type": "List",
            "name": "Form990PartVIISectionAGrp",
            "parent": "origin_temporal_000266",
            "sort_order": 1
        },
        "origin_temporal_001231": {
            "data_type": "Text",
            "name": "AverageHoursPerWeekRt",
            "parent": "origin_temporal_001230",
            "sort_order": 0
        },
        "origin_temporal_001232": {
            "data_type": "Unary",
            "name": "OfficerInd",
            "parent": "origin_temporal_001230",
            "sort_order": 1
        },
        "origin_temporal_001233": {
            "data_type": "Currency",
            "name": "OtherCompensationAmt",
            "parent": "origin_temporal_001230",
            "sort_order": 2
        },
        "origin_temporal_001234": {
            "data_type": "Text",
            "name": "PersonNm",
            "parent": "origin_temporal_001230",
            "sort_order": 3
        },
        "origin_temporal_001235": {
            "data_type": "Currency",
            "name": "ReportableCompFromOrgAmt",
            "parent": "origin_temporal_001230",
            "sort_order": 4
        },
        "origin_temporal_001236": {
            "data_type": "Currency",
            "name": "ReportableCompFromRltdOrgAmt",
            "parent": "origin_temporal_001230",
            "sort_order": 5
        },
        "origin_temporal_001237": {
            "data_type": "Text",
            "name": "TitleTxt",
            "parent": "origin_temporal_001230",
            "sort_order": 6
        },
        "origin_temporal_001238": {
            "data_type": "Unary",
            "name": "IndividualTrusteeOrDirectorInd",
            "parent": "origin_temporal_001230",
            "sort_order": 7
        },
        "origin_temporal_001643": {
            "data_type": "Unary",
            "name": "IndividualTrusteeOrDirector",
            "parent": "origin_temporal_000413",
            "sort_order": 8
        },
        "origin_temporal_001921": {
            "data_type": "Unary",
            "name": "HighestCompensatedEmployee",
            "parent": "origin_temporal_000413",
            "sort_order": 9
        },
        "origin_temporal_002215": {
            "data_type": "Unary",
            "name": "HighestCompensatedEmployeeInd",
            "parent": "origin_temporal_001230",
            "sort_order": 8
        },
        "origin_temporal_002524": {
            "data_type": "Unary",
            "name": "KeyEmployeeInd",
            "parent": "origin_temporal_001230",
            "sort_order": 9
        },
        "origin_temporal_002593": {
            "data_type": "Unary",
            "name": "KeyEmployee",
            "parent": "origin_temporal_000413",
            "sort_order": 10
        },
        "origin_temporal_002594": {
            "data_type": "Unary",
            "name": "Former",
            "parent": "origin_temporal_000413",
            "sort_order": 11
        },
        "origin_temporal_002978": {
            "data_type": "Text",
            "name": "AverageHoursPerWeekRltdOrgRt",
            "parent": "origin_temporal_001230",
            "sort_order": 10
        },
        "origin_temporal_002979": {
            "data_type": "Unary",
            "name": "FormerOfcrDirectorTrusteeInd",
            "parent": "origin_temporal_001230",
            "sort_order": 11
        },
        "origin_temporal_003467": {
            "data_type": "Folder",
            "name": "NameBusiness",
            "parent": "origin_temporal_000413",
            "sort_order": 12
        },
        "origin_temporal_003468": {
            "data_type": "Text",
            "name": "BusinessNameLine1",
            "parent": "origin_temporal_003467",
            "sort_order": 0
        },
        "origin_temporal_003645": {
            "data_type": "Unary",
            "name": "InstitutionalTrustee",
            "parent": "origin_temporal_000413",
            "sort_order": 13
        },
        "origin_temporal_003651": {
            "data_type": "Unary",
            "name": "InstitutionalTrusteeInd",
            "parent": "origin_temporal_001230",
            "sort_order": 12
        },
        "origin_temporal_006519": {
            "data_type": "Folder",
            "name": "BusinessName",
            "parent": "origin_temporal_001230",
            "sort_order": 13
        },
        "origin_temporal_006520": {
            "data_type": "Text",
            "name": "BusinessNameLine1Txt",
            "parent": "origin_temporal_006519",
            "sort_order": 0
        },
        "origin_temporal_006659": {
            "data_type": "Text",
            "name": "BusinessNameLine2Txt",
            "parent": "origin_temporal_006519",
            "sort_order": 1
        }
    }

    return spec, doc

@pytest.fixture()
def target() -> Tuple[Dict, OrderedDict]:
    doc: OrderedDict = OrderedDict([
        ('Tax return', OrderedDict([
            ('IRS 990', OrderedDict([
                ('Part VII', OrderedDict([
                    ('Section A Chart', [
                        OrderedDict([
                            ('Column F', '0'),
                            ('Column E', '0'),
                            ('Column D', '0'),
                            ('Column B, sub-row 1', '1.00'),
                            ('Column C', OrderedDict([('Sub-column 1', 'X')])),
                            ('Column A, First element, Person name', 'JOHN DOE'),
                            ('Column A, Second element', 'BOARD MEMBER')
                        ]), OrderedDict([
                            ('Column F', '50000'),
                            ('Column E', '10000'),
                            ('Column D', '100000'),
                            ('Column B, sub-row 1', '40.00'),
                            ('Column A, First element, Person name', 'JANE SMITH'),
                            ('Column A, Second element', 'DIRECTOR OF ENGINEERING')
                        ])
                    ])
                ]))
            ]))
        ]))
    ])

    spec: Dict = {
        "logical_temporal_000001": {
            "data_type": "Folder",
            "name": "Tax return",
            "sort_order": 0
        },
        "logical_temporal_000007": {
            "data_type": "Folder",
            "name": "IRS 990",
            "parent": "logical_temporal_000001",
            "sort_order": 0
        },
        "logical_temporal_000070": {
            "data_type": "Folder",
            "name": "Part VII",
            "parent": "logical_temporal_000007",
            "sort_order": 0
        },
        "logical_temporal_000222": {
            "data_type": "List",
            "name": "Section A Chart",
            "parent": "logical_temporal_000070",
            "sort_order": 0,
            "sources": [
                "origin_temporal_000413",
                "origin_temporal_001230"
            ]
        },
        "logical_temporal_000587": {
            "data_type": "Currency",
            "name": "Column F",
            "parent": "logical_temporal_000222",
            "sort_order": 0,
            "sources": [
                "origin_temporal_000417",
                "origin_temporal_001233"
            ]
        },
        "logical_temporal_000588": {
            "data_type": "Currency",
            "name": "Column E",
            "parent": "logical_temporal_000222",
            "sort_order": 1,
            "sources": [
                "origin_temporal_000419",
                "origin_temporal_001236"
            ]
        },
        "logical_temporal_000589": {
            "data_type": "Currency",
            "name": "Column D",
            "parent": "logical_temporal_000222",
            "sort_order": 2,
            "sources": [
                "origin_temporal_000418",
                "origin_temporal_001235"
            ]
        },
        "logical_temporal_000590": {
            "data_type": "Text",
            "name": "Column B, sub-row 1",
            "parent": "logical_temporal_000222",
            "sort_order": 3,
            "sources": [
                "origin_temporal_000414",
                "origin_temporal_001231"
            ]
        },
        "logical_temporal_000591": {
            "data_type": "Text",
            "name": "Column B, sub-row 2",
            "parent": "logical_temporal_000222",
            "sort_order": 4,
            "sources": [
                "origin_temporal_001067",
                "origin_temporal_002978"
            ]
        },
        "logical_temporal_000592": {
            "data_type": "Folder",
            "name": "Column C",
            "parent": "logical_temporal_000222",
            "sort_order": 5,
        },
        "logical_temporal_000593": {
            "data_type": "Text",
            "name": "Column A, First element, Person name",
            "parent": "logical_temporal_000222",
            "sort_order": 6,
            "sources": [
                "origin_temporal_000415",
                "origin_temporal_001234"
            ]
        },
        "logical_temporal_000594": {
            "data_type": "Text",
            "name": "Column A, Second element",
            "parent": "logical_temporal_000222",
            "sort_order": 7,
            "sources": [
                "origin_temporal_000420",
                "origin_temporal_001237"
            ]
        },
        "logical_temporal_000595": {
            "data_type": "Text",
            "name": "Column A, First element, Business Name 2",
            "parent": "logical_temporal_000222",
            "sort_order": 8,
            "sources": [
                "origin_temporal_006659"
            ]
        },
        "logical_temporal_000596": {
            "data_type": "Text",
            "name": "Column A, First element, Business Name 1",
            "parent": "logical_temporal_000222",
            "sort_order": 9,
            "sources": [
                "origin_temporal_006520",
                "origin_temporal_003468"
            ]
        },
        "logical_temporal_000733": {
            "data_type": "Unary",
            "name": "Sub-column 1",
            "parent": "logical_temporal_000592",
            "sort_order": 0,
            "sources": [
                "origin_temporal_001643",
                "origin_temporal_001238"
            ]
        },
        "logical_temporal_000734": {
            "data_type": "Unary",
            "name": "Sub-column 6",
            "parent": "logical_temporal_000592",
            "sort_order": 1,
            "sources": [
                "origin_temporal_002979",
                "origin_temporal_002594"
            ]
        },
        "logical_temporal_000735": {
            "data_type": "Unary",
            "name": "Sub-column 3",
            "parent": "logical_temporal_000592",
            "sort_order": 2,
            "sources": [
                "origin_temporal_000416",
                "origin_temporal_001232"
            ]
        },
        "logical_temporal_000736": {
            "data_type": "Unary",
            "name": "Sub-column 2",
            "parent": "logical_temporal_000592",
            "sort_order": 3,
            "sources": [
                "origin_temporal_003645",
                "origin_temporal_003651"
            ]
        },
        "logical_temporal_000737": {
            "data_type": "Unary",
            "name": "Sub-column 4",
            "parent": "logical_temporal_000592",
            "sort_order": 4,
            "sources": [
                "origin_temporal_002593",
                "origin_temporal_002524"
            ]
        },
        "logical_temporal_000738": {
            "data_type": "Unary",
            "name": "Sub-column 5",
            "parent": "logical_temporal_000592",
            "sort_order": 5,
            "sources": [
                "origin_temporal_001921",
                "origin_temporal_002215"
            ]
        }
    }
    return spec, doc

def test_two_list_sources_one_exists(source, target):
    source_spec, source_doc = source
    target_spec, expected = target
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected
