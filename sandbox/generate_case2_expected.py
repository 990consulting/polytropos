from typing import Dict, Tuple, List

import numpy
import scipy.stats
import json

from polytropos.util import nesteddicts

basepath = "/dmz/github/polytroposa/fixtures/2_mm_scan/data/entities"

people: Dict[str, Dict] = {}

def assign_bmi_by_year(person: Dict) -> None:
    height = nesteddicts.get(person, ["immutable", "height"])
    years = set(person.keys()) - {"immutable"}
    h_squared = height ** 2
    for year in years:
        weight = nesteddicts.get(person, [year, "weight"])
        bmi = weight / h_squared * 703
        nesteddicts.put(person, [year, "bmi"], bmi)

def assign_regression_stats(person: Dict) -> None:
    years = set(person.keys()) - {"immutable"}
    years_ordered = sorted([int(year) for year in years])
    weights = [nesteddicts.get(person, [str(year), "weight"]) for year in years_ordered]
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(years_ordered, weights)
    nesteddicts.put(person, ["immutable", "weight_change", "slope"], slope)
    nesteddicts.put(person, ["immutable", "weight_change", "p_value"], p_value)

def assign_mean_bmi(person: Dict) -> None:
    years = set(person.keys()) - {"immutable"}
    bmis = [nesteddicts.get(person, [year, "bmi"]) for year in years]
    mean_bmi = numpy.average(bmis)
    nesteddicts.put(person, ["immutable", "mean_bmi"], mean_bmi)

# Equivalent of Evolve step
for i in range(1, 10):
    fn = "person_%i.json" % i
    input_fn = "%s/origin/%s" % (basepath, fn)
    output_fn = "%s/expected/%s" % (basepath, fn)
    with open(input_fn) as input_fh:
        person = json.load(input_fh)
        assign_bmi_by_year(person)
        assign_regression_stats(person)
        assign_mean_bmi(person)
        people[fn] = person

# Equivalent of scan step
mean_bmi_dict: Dict[str, Dict[str, float]] = {}
genders = ["male", "female", "overall"]
for gender in genders:
    mean_bmi_dict[gender] = {}

for fn, person in people.items():
    gender: str = "female"
    if person["immutable"]["male"]:
        gender = "male"
    mean_bmi = person["immutable"]["mean_bmi"]
    mean_bmi_dict[gender][fn] = mean_bmi
    mean_bmi_dict["overall"][fn] = mean_bmi

ranked: Dict[str, List[str]] = {}
for gender in genders:
    people_ranked = list(sorted(mean_bmi_dict[gender].keys(), key=lambda k: -1 * mean_bmi_dict[gender][k]))
    ranked[gender] = people_ranked

for gender in ["male", "female"]:
    for k, person in enumerate(ranked[gender]):
        nesteddicts.put(people[person], ["immutable", "bmi_rank_within_gender"], k + 1)

for k, person in enumerate(ranked["overall"]):
    nesteddicts.put(people[person], ["immutable", "bmi_rank_overall"], k + 1)

for fn, person in people.items():
    with open("%s/expected/%s" % (basepath, fn), "w") as output_fh:
        json.dump(person, output_fh, indent=2)
