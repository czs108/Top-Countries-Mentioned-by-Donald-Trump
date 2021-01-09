from pathlib import Path
from typing import TYPE_CHECKING

import nltk
import spacy

from country import Container

if TYPE_CHECKING:
    from collections.abc import Sequence


Count = dict[str, int]


class Counter:
    def handle(self, year: int, nouns: Sequence[str]) -> None:
        """
        Handle nouns in a sentence related to a specific year.
        """
        assert False

    @property
    def total(self) -> dict:
        """
        Get the total count for 4 years.
        """
        assert False

    @property
    def annual(self) -> dict[int, dict]:
        """
        Get the annual count for each year.
        """
        assert False


class Director:
    """
    Read annual files, extract nouns and send them to counters.
    """
    _SENTENCE_CLUSTER: int = 3

    def __init__(self, in_dir: Path, counters: Sequence[Counter]) -> None:
        self._in_dir: Path = in_dir
        self._counters: Sequence[Counter] = counters
        self._nlp = spacy.load("en_core_web_sm")

    def handle(self) -> None:
        if len(self._counters) == 0:
            return
        for path in self._in_dir.glob("20??.txt"):
            if not path.is_file():
                continue
            with path.open(encoding="utf-8") as file:
                sentences = nltk.sent_tokenize(file.read())
                for i in range(0, len(sentences), self._SENTENCE_CLUSTER):
                    # Several sentences are made a group.
                    sentence_num = min(self._SENTENCE_CLUSTER, len(sentences) - i)
                    cluster = "".join([sentences[j] for j in range(i, i + sentence_num)])
                    for counter in self._counters:
                        nouns = self._nlp(cluster).noun_chunks
                        counter.handle(int(path.stem), [i.text for i in nouns])


class NormalCounter(Counter):
    """
    Count the number of times each country has been mentioned.
    """
    def __init__(self, countries: Container) -> None:
        super().__init__()
        self._countries: Container = countries
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


class DiplomacyCounter(Counter):
    """
    Count the number of times each diplomatic relation has been mentioned.
    """
    def __init__(self, countries: Container, normal: NormalCounter) -> None:
        super().__init__()
        self._countries: Container = countries
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
