import json
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from collections import Counter


class PathTuple:
    """
    Store the paths of count files.
    """
    def __init__(self) -> None:
        self.total: Path = None
        self.annual: Path = None


class Loader:
    """
    Load counts as dataframes.
    """
    def load(self, paths: PathTuple) -> None:
        """
        Load counts from JSON files and convert them to dataframes.
        """
        with paths.total.open(encoding="utf-8") as file:
            self._handle_total(json.load(file))
        with paths.annual.open(encoding="utf-8") as file:
            self._handle_annual(json.load(file))

    @property
    def total(self) -> pd.DataFrame | dict:
        """
        Get the total count for 4 years.
        """
        assert False

    @property
    def annual(self) -> dict:
        """
        Get the annual count for each year.
        """
        assert False

    def _handle_total(self, count: dict) -> None:
        """
        Handle the total count.
        """
        assert False

    def _handle_annual(self, count: dict) -> None:
        """
        Handle the annual count.
        """
        assert False


def build_dataframe(count: Counter) -> pd.DataFrame:
    """
    Create a dataframe from a count.
    """
    data = pd.DataFrame(pd.Series(dict(count)), columns=["count"])
    data.index.name = "country"
    return data.sort_values(by="count", ascending=False)


class NormalLoader(Loader):
    def __init__(self) -> None:
        super().__init__()
        self._total: pd.DataFrame = None
        self._annual: dict[int, pd.DataFrame] = {}

    @property
    def total(self) -> pd.DataFrame:
        return self._total

    @property
    def annual(self) -> dict[int, pd.DataFrame]:
        return self._annual

    def _handle_total(self, count: Counter) -> None:
        self._total = build_dataframe(count)

    def _handle_annual(self, count: dict[int, Counter]) -> None:
        for year in count.keys():
            self._annual[year] = build_dataframe(count[year])


class DiplomacyLoader(Loader):
    def __init__(self) -> None:
        super().__init__()
        self._total: dict[str, pd.DataFrame] = {}
        self._annual: dict[int, dict[str, pd.DataFrame]] = {}

    @property
    def total(self) -> dict[str, pd.DataFrame]:
        return self._total

    @property
    def annual(self) -> dict[int, dict[str, pd.DataFrame]]:
        return self._annual

    def _handle_total(self, count: dict[str, Counter]) -> None:
        for country in count.keys():
            self._total[country] = build_dataframe(count[country])

    def _handle_annual(self, count: dict[int, dict[str, Counter]]) -> None:
        for year in count.keys():
            self._annual[year] = {}
            for country in count[year].keys():
                self._annual[year][country] = build_dataframe(count[year][country])
