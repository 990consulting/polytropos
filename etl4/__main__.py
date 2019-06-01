import argparse

from etl4.__cli import CLI
import sys
import os
import logging

cli: CLI = CLI()
args: argparse.Namespace = cli.parse_args()

# If the user requested license information, display it and exit, regardless of other args
if args.license:
    path: str = os.path.dirname(os.path.abspath(__file__))
    license_fn = "%s/../license.txt" % path
    with open(license_fn) as fh:
        print(fh.read())
    sys.exit(0)

# Set user's preferred log level and begin logging
log_level_key = args.log_level
log_levels = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "none": logging.NOTSET
}
log_level = log_levels[log_level_key]
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=log_level)

# Verify data path exists
data_path: str = args.data
if not (os.path.exists(data_path) and os.path.isdir(data_path)):
    if data_path == cli.default_data_path:
        cli.error('The default data directory, ./data, does not exist at this location.')
    else:
        cli.error('Invalid data path "%s".' % data_path)

# Verify configuration path exists
conf_path: str = args.conf
if not (os.path.exists(conf_path) and os.path.isdir(conf_path)):
    if conf_path == cli.default_conf_path:
        cli.error('The default configuration directory, ./conf, does not exist at this location.')
    else:
        cli.error('Invalid configuration path "%s".' % conf_path)

# Verify task is defined
task_yaml: str = args.task
task_yaml_path = "%s/tasks/%s.yaml" % (conf_path, task_yaml)
if not os.path.exists(task_yaml_path) or os.path.isdir(task_yaml_path):
    cli.error('No task "%s" YAML found in task directory (%s/tasks).' % (task_yaml, conf_path))

# All parameters having been verified, load and run the task

