import csv
from collections import defaultdict
from polytropos.ontology.variable import Primitive, List, NamedList


class Reporter:
    def __init__(self):
        self.primitive_match = defaultdict(int)
        self.primitive_mismatch = defaultdict(int)
        self.primitive_failures = []
        self.document_name = None

    def set_document_name(self, name):
        self.document_name = name

    def report_primitive(self, var_id, variable, value):
        if self.document_name in variable.simple_expected_values:
            expected = variable.simple_expected_values[self.document_name]
            if expected == value:
                self.primitive_match[var_id] += 1
            else:
                self.primitive_mismatch[var_id] += 1
                self.primitive_failures.append(
                    (var_id, self.document_name, value, expected)
                )

    def report_list(self, var_id, variable, value):
        pass

    def report_named_list(self, var_id, variable, value):
        pass

    def report(self, var_id, variable, value):
        if isinstance(variable, Primitive):
            return self.report_primitive(var_id, variable, value)
        elif isinstance(variable, List):
            return self.report_list(var_id, variable, value)
        elif isinstance(variable, NamedList):
            return self.report_list(var_id, variable, value)
        else:
            # folders don't have expected values
            return

    def save(self, prefix):
        all_vars = (
            set(self.primitive_match.keys()) |
            set(self.primitive_mismatch.keys())
        )
        with open(prefix + '_primitive_report.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['var_id', 'hits', 'misses'])
            for var_id in all_vars:
                writer.writerow([
                    var_id,
                    self.primitive_match.get(var_id, 0),
                    self.primitive_mismatch.get(var_id, 0),
                ])
        with open(prefix + '_primitive_failures.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['var_id', 'instance', 'value', 'expected'])
            for failure in self.primitive_failures:
                writer.writerow(failure)
