import logging
from polytropos.actions import register_all

# noinspection PyUnresolvedReferences
def test(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    import examples.s_8_filter_narrow.conf.filters.threshold
    run_task('s_8_filter_narrow', 'example_8', 'generic/expected')
