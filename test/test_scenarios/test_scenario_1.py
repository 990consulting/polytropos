def test(run_task):
    import polytropos_demo.s_1_mm_only.conf.changes.vitals
    import polytropos_demo.s_1_mm_only.conf.changes.description
    import polytropos_demo.s_1_mm_only.conf.changes.color
    run_task('s_1_mm_only', 'infer_about_person', 'person/expected')
