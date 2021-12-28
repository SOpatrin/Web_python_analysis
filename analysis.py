from typing import List, Dict

import pandas as pd


class Analysis:
    countries: List[str]

    def __init__(self, data):
        data.fillna(0, inplace=True)
        self.countries = list(set(data['location']))
        self.data = data

    def get_countries(self) -> List[str]:
        return self.countries

    def get_quantile(self, country='Russia') -> int:
        data_per_country = self.data.groupby(['location'], as_index=False).sum()
        # calculate test per million people for each country
        data_per_country['tests_per_million'] = (
            data_per_country['total_tests'] / data_per_country['population'] * 1000000
        )
        data_per_country.fillna(0, inplace=True)

        tests_per_million = data_per_country.sort_values('tests_per_million', ascending=False)[
            ['location', 'tests_per_million']]

        country_tests = float(tests_per_million.loc[tests_per_million['location'] == country]['tests_per_million'])

        quantiles = tests_per_million.quantile([.25, .5, .75, 1])

        quantiles_map = {
            0.25: 1,
            0.5: 2,
            0.75: 3,
            1: 4
        }

        return quantiles_map[float(quantiles.loc[quantiles['tests_per_million'] <= country_tests].iloc[-1].name)]

    def get_countries_by_delta(self, country: str, delta: float) -> List[Dict[str, float]]:
        data_per_country = self.data.groupby(['location'], as_index=False).sum()
        data_per_country['cases_per_deaths_per_million'] = (
            data_per_country['new_cases_per_million'] / data_per_country['new_deaths_per_million']
        )

        country_cases = data_per_country.loc[data_per_country['location'] == country]['cases_per_deaths_per_million']
        data_per_country['delta'] = abs(data_per_country['cases_per_deaths_per_million'] - float(country_cases))
        countries_delta = (
            data_per_country
            .loc[data_per_country['delta'] < delta]
            .loc[data_per_country['location'] != country][['location', 'delta']]
            .values
            .tolist()
        )

        return list(map(lambda cd: {'location': cd[0], 'delta': cd[1]}, countries_delta))
