from collections.abc import Sequence
from analysis.counter.counter import Count, Counter
from analysis.country.container import CountryContainer


class NormalCounter(Counter):
    """
    Count the number of times each country has been mentioned.
    """
    def __init__(self, countries: CountryContainer) -> None:
        super().__init__()
        self._countries: CountryContainer = countries
        self._total: Count = {}
        self._annual: dict[int, Count] = {}

    def handle(self, year: int, nouns: Sequence[str]) -> None:
        for word in nouns:
            if self._countries.contain(word):
                self.add_record(year, word)

    def add_record(self, year: int, country: str, count: int = 1) -> None:
        country = self._countries.main_name(country)
        self._init_dict(year, country)
        self._total[country] += count
        self._annual[year][country] += count

    @property
    def total(self) -> Count:
        return self._total

    @property
    def annual(self) -> dict[int, Count]:
        return self._annual

    def _init_dict(self, year: int, country: str) -> None:
        if country not in self._total:
            self._total[country] = 0
        if year not in self._annual:
            self._annual[year] = {}
        if country not in self._annual[year]:
            self._annual[year][country] = 0
