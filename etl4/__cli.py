import argparse


class CLI:
    description = """
    Polytropos (https://polytropos.io) --- Functional data enrichment for Python.
    ------------------------------------------------------------------------------
    Copyright (c) 2019 Applied Nonprofit Research, LLC. For license information, 
    use --license.
    """.strip()

    epilog = """
        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as
        published by the Free Software Foundation, either version 3 of the
        License, or (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Affero General Public License for more details.
        
        For full documentation, visit https://polytropos.io.
    """.strip()

    default_data_path = "./data"
    default_conf_path = "./conf"

    def __init__(self):
        self.cli = argparse.ArgumentParser(
            prog="polytropos",
            description=self.description,
            epilog=self.epilog
        )

        self.cli.add_argument(
            "--data",
            help="Location where data should be read and written. Defaults to ./data.",
            default=self.default_data_path
        )

        self.cli.add_argument(
            "--conf",
            help="Location where configuration files are located. Defaults to ./conf.",
            default=self.default_conf_path
        )

        self.cli.add_argument(
            "--task",
            help="Name of the task to be performed. The task is defined in a .yaml file of the same name, located in"
                 " the tasks/ directory of the configuration."
        )

        self.cli.add_argument(
            "--license",
            action="store_true",
            help="Displays license information for Polytropos."
        )

        self.cli.add_argument(
            "--log_level",
            choices=["critical", "error", "warning", "info", "debug", "none"],
            help='The level of logging detail to be reported while running Polytropos. Defaults to "info".',
            default="info"
        )

    def parse_args(self) -> argparse.Namespace:
        args = self.cli.parse_args()

        if not (args.task or args.license):
            self.cli.error("Either --task or --license argument required.")
        return args

    def error(self, msg):
        self.cli.error(msg)