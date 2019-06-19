import logging

# noinspection PyUnresolvedReferences
def test(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    import polytropos_demo.s_2_mm_scan.conf.changes.bmi
    import polytropos_demo.s_2_mm_scan.conf.changes.weight
    import polytropos_demo.s_2_mm_scan.conf.scans.rank
    run_task('s_2_mm_scan', 'bmi_rank', 'person/expected')
