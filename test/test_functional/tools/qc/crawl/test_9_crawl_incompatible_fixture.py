from typing import Dict

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.tools.qc.crawl import CrawlImmutable
from polytropos.tools.qc.outcome import Outcome, InvalidPath

def test_fixture_boolean_spec_folder(simple_track: Track, empty_track: Track, entity_id: str):
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "outer": True
    }
    observation: Dict = {
        "outer": {
            "some_multiple_text": ["foo", "bar"]
        }
    }
    expected: Outcome = Outcome()
    expected.invalids.append(InvalidPath(entity_id, "/outer", "immutable", True))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual
