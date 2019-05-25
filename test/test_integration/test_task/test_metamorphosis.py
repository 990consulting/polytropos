import json
import os
from etl4.ontology.task import Task


def test_infer_about_person():
    task = Task.build('infer_about_person')
    task.run()
    path = 'fixtures/data/person/'
    for filename in os.listdir(os.path.join(path, 'actual')):
        with open(os.path.join(path, 'actual', filename), 'r') as f:
            with open(os.path.join(path, 'expected', filename), 'r') as g:
                assert json.load(f) == json.load(g)
