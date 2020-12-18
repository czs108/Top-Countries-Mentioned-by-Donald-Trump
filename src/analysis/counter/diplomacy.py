from collections.abc import Sequence
from analysis.counter.counter import Count, Counter
from analysis.country.container import CountryContainer
from analysis.counter.normal import NormalCounter


class DiplomacyCounter(Counter):
    """
    Count the number of times each diplomatic relation has been mentioned.
    """
    def __init__(self, countries: CountryContainer, normal: NormalCounter) -> None:
        super().__init__()
        self._countries: CountryContainer = countries
        self._normal: NormalCounter = normal
        self._total: dict[str, Count] = {}
        self._annual: dict[int, dict[str, Count]] = {}

    def handle(self, year: int, nouns: Sequence[str]) -> None:
        countries: Count = {}
        for word in nouns:
            if self._countries.contain(word):
                name = self._countries.main_name(word)
                if name not in countries:
                    countries[name] = 0
                countries[name] += 1
                self._normal.add_record(year, name)
        self._add_records(year, countries)

    @property
    def total(self) -> dict[str, Count]:
        return self._total

    @property
    def annual(self) -> dict[int, dict[str, Count]]:
        return self._annual

    def _add_records(self, year: int, countries: Count) -> None:
        for country in countries:
            for relation in countries:
                if relation == country:
                    continue
                self._init_dict(year, country, relation)
                self._total[country][relation] += 1
                self._annual[year][country][relation] += 1

    def _init_dict(self, year: int, country: str, relation: str) -> None:
        if country not in self._total:
            self._total[country] = {}
        if year not in self._annual:
            self._annual[year] = {}
        if country not in self._annual[year]:
            self._annual[year][country] = {}

        if relation not in self._total[country]:
            self._total[country][relation] = 0
        if relation not in self._annual[year][country]:
            self._annual[year][country][relation] = 0
