from test.test_integration.scenarios.helper import run_task


def test():
    import fixtures.s_1_mm_only.conf.changes.vitals
    import fixtures.s_1_mm_only.conf.changes.description
    import fixtures.s_1_mm_only.conf.changes.color
    run_task('s_1_mm_only', 'infer_about_person', 'person/expected')
