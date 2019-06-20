import logging

# noinspection PyUnresolvedReferences
def test(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    import polytropos_demo.s_3_mm_aggregate_mm_scan.conf.changes.city
    import polytropos_demo.s_3_mm_aggregate_mm_scan.conf.changes.company
    import polytropos_demo.s_3_mm_aggregate_mm_scan.conf.scans.rank
    import polytropos_demo.s_3_mm_aggregate_mm_scan.conf.aggregations.economy
    run_task('s_3_mm_aggregate_mm_scan', 'economy', 'city/expected')
