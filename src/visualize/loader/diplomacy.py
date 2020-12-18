import pandas as pd
from visualize.loader.loader import Loader, build_dataframe
from analysis.counter.counter import Count


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

    def _handle_total(self, count: dict[str, Count]) -> None:
        for country in count.keys():
            self._total[country] = build_dataframe(count[country])

    def _handle_annual(self, count: dict[int, dict[str, Count]]) -> None:
        for year in count.keys():
            self._annual[year] = {}
            for country in count[year].keys():
                self._annual[year][country] = build_dataframe(count[year][country])
