from typing import Optional, Dict

from polytropos.ontology.schema import Schema

from polytropos.ontology.composite import Composite
from polytropos.tools.qc.crawl import CrawlPeriod, CrawlImmutable
from polytropos.tools.qc.outcome import Outcome

class FixtureComparator:
    def __init__(self, schema: Schema, entity_id: str, fixture: Composite, actual: Optional[Composite]):
        self.entity_id: str = entity_id
        self.no_actual: bool = actual is None

        self.outcomes: Outcome = Outcome()

        if actual is not None:
            self._crawl(schema, fixture, actual)

    def _crawl(self, schema: Schema, fixture: Composite, actual: Composite) -> None:
        for period in fixture.periods:
            f_period: Dict = fixture.content[period]
            a_period: Optional[Dict] = actual.content.get(period)
            crawl_period: CrawlPeriod = CrawlPeriod(schema, f_period, a_period, self.outcomes, period)
            crawl_period()

        if "immutable" in fixture.content:
            f_immutable: Dict = fixture.content["immutable"]
            a_immutable: Optional[Dict] = actual.content.get("immutable")
            crawl_immutable: CrawlImmutable = CrawlImmutable(schema, f_immutable, a_immutable, self.outcomes)
            crawl_immutable()
