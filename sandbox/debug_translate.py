import logging

from polytropos.ontology.task import Task

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
conf_path = "/dmz/github/anr-polytropos-config/"
data_path = "/dmz/output/polytropos_tmp/"
task = "origin_to_logical"
task = Task.build(conf_path, data_path, task)
task.run()