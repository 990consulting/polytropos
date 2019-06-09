from test.test_integration.scenarios.helper import run_task

def test():
    import fixtures.s_3_mm_aggregate_mm_scan.conf.changes.city
    import fixtures.s_3_mm_aggregate_mm_scan.conf.changes.company
    import fixtures.s_3_mm_aggregate_mm_scan.conf.scans.rank
    import fixtures.s_3_mm_aggregate_mm_scan.conf.aggregations.economy
    run_task('s_3_mm_aggregate_mm_scan', 'economy', 'city/expected')
