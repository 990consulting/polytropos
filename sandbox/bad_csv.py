"""Confirming that CSV reader doesn't care about variable line lengths"""
import csv

with open("variable_length.csv") as fh:
    reader = csv.reader(fh)
    for line in reader:
        var_id, abs_path, *sources = line
        print("Variable ID: %s. Absolute path: %s. Sources: %s." % (var_id, abs_path, ", ".join(sources)))
