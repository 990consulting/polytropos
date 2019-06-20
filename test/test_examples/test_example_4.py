import logging

# noinspection PyUnresolvedReferences
def test(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    import examples.s_4_filter_mm_scan.conf.changes.bmi
    import examples.s_4_filter_mm_scan.conf.changes.weight
    import examples.s_4_filter_mm_scan.conf.filters.gender
    import examples.s_4_filter_mm_scan.conf.scans.rank
    run_task('s_4_filter_mm_scan', 'bmi_rank', 'person/expected')
