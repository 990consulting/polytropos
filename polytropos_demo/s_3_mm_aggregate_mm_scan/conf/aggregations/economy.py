from dataclasses import dataclass
from typing import Iterator, Tuple, Dict, Iterable, Any, Optional

from polytropos.ontology.composite import Composite

from polytropos.ontology.variable.__variable import Decimal, Text

from polytropos.actions.aggregate import Aggregate
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.variable import Integer


@dataclass
class EconomicOverview(Aggregate):
    n_employee_var: str = VariableValidator(data_type=Integer, temporal=1)
    revenue_var: str = VariableValidator(data_type=Decimal, temporal=1)
    source_zip_var: str = VariableValidator(data_type=Text, temporal=-1)
    source_city_var: str = VariableValidator(data_type=Text, temporal=-1)
    source_state_var: str = VariableValidator(data_type=Text, temporal=-1)

    # Output schema variables
    n_company_var: str = VariableValidator(data_type=Integer, temporal=1)
    mean_employee_var: str = VariableValidator(data_type=Decimal, temporal=1)
    annual_prod_var: str = VariableValidator(data_type=Decimal, temporal=1)
    target_zip_var: str = VariableValidator(data_type=Text, temporal=-1)
    target_city_var: str = VariableValidator(data_type=Text, temporal=-1)
    target_state_var: str = VariableValidator(data_type=Text, temporal=-1)

    def __post_init__(self):
        # Internal variable used for reduce/analyze step
        self.city_data: Dict[str, Dict] = {}

    def extract(self, composite: Dict) -> Optional[Any]:
        """In this case, the source document is very small and the analysis uses every variable in it, so we just return
        the composite. In real-world cases, only a few variables are likely to be used."""
        return composite

    def analyze(self, extracts: Iterable[Tuple[str, Composite]]) -> None:
        for company_id, company in extracts:
            zip_code = company.get_immutable(self.source_zip_var)
            city = company.get_immutable(self.source_city_var)
            state = company.get_immutable(self.source_state_var)

            # Create a transient composite for the city. It will be processed into its final form in emit().
            if zip_code not in self.city_data:
                self.city_data[zip_code] = {'immutable': {
                    "zip": zip_code,
                    "city": city,
                    "state": state
                }}

            for period in company.periods:
                if period not in self.city_data[zip_code]:
                    self.city_data[zip_code][period] = {
                        "n_companies": 0,
                        "tot_employees": 0,
                        "tot_revenue": 0.0
                    }

                p_dict = self.city_data[zip_code][period]
                p_dict["n_companies"] += 1
                p_dict["tot_employees"] += company.get_observation(self.n_employee_var, period)
                p_dict["tot_revenue"] += company.get_observation(self.revenue_var, period)

    def emit(self) -> Iterator[Tuple[str, Composite]]:
        for zip_code, transient in self.city_data.items():
            city: Composite = Composite(self.target_schema, {})

            transient_periods = set(transient.keys()) - {"immutable"}
            for period in sorted(transient_periods):
                n_companies = transient[period]["n_companies"]
                tot_employees = transient[period]["tot_employees"]
                tot_revenue = transient[period]["tot_revenue"]

                mean_employees = tot_employees / n_companies
                productivity = tot_revenue / tot_employees

                city.put_observation(period, self.n_company_var, n_companies)
                city.put_observation(period, self.annual_prod_var, productivity)
                city.put_observation(period, self.mean_employee_var, mean_employees)

            city.put_immutable(self.target_zip_var, transient["immutable"]["zip"])
            city.put_immutable(self.target_city_var, transient["immutable"]["city"])
            city.put_immutable(self.target_state_var, transient["immutable"]["state"])
            
            yield zip_code, city
