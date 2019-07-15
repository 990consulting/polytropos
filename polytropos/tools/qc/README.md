  * Create an object called FixtureComparator, and do all the business logic there
    * Construction arguments:
       * expected: Composite
       * actual: Optional[Composite]
       * schema: Schema
    * properties (All return Iterator[FixtureCase], where FixtureCase is a named tuple)
       * matches
         * What it sounds like: right type and content agrees
       * mismatches
         * Data is type-compatible, but the content does not agree
       * missing
         * Expected value is defined but no corresponding value exists in actual
       * undefined
         * Path into data does not correspond to a variable in the schema
    * On build:
       * Initialize sets for each return type
       * For each period (and for immutable)
         * Crawl the data hierarchy tree depth first, tracking path
           * If you hit a path that is unknown to schema, add to “undefined” and stop traversing
           * If you hit a list or a terminal node, do the comparison and add to “matches,” “mismatches,” or “missing”
       * Store properties as dequeues so that the traversal order is consistent 
    * CompareAllFixtures classes creates a dict of EIN -> FixtureComparator
    * Iterators for matches, mismatches, missing, undefined
  * Tests (all provide custom messages--use the “ids” property of pytest.mark.parametrize to produce helpful test names for report)
    * test_report_no_actual() --> all fail
    * test_report_matches() --> all pass
    * test_report_mismatches() --> all fail
    * test_report_missing() --> all fail
    * test_report_undefined() --> all fail
