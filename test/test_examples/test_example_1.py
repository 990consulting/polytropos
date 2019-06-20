import logging

# noinspection PyUnresolvedReferences
def test(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    import examples.s_1_mm_only.conf.changes.vitals
    import examples.s_1_mm_only.conf.changes.description
    import examples.s_1_mm_only.conf.changes.color
    run_task('s_1_mm_only', 'infer_about_person', 'person/expected')
