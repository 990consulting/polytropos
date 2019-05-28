import os


BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../../../'
))


TASKS_DIR = os.path.join(BASE_DIR, 'fixtures/conf/tasks')
DATA_DIR = os.path.join(BASE_DIR, 'fixtures/data')
CHANGES_DIR = os.path.join(BASE_DIR, 'fixtures/conf/changes')
