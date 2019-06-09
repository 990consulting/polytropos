from test.test_integration.scenarios.helper import run_task

def test():
    import fixtures.s_2_mm_scan.conf.changes.bmi
    import fixtures.s_2_mm_scan.conf.changes.weight
    import fixtures.s_2_mm_scan.conf.scans.rank
    run_task('s_2_mm_scan', 'bmi_rank', 'person/expected')
