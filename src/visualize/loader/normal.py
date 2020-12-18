import pandas as pd
from visualize.loader.loader import Loader, build_dataframe
from analysis.counter.counter import Count


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

    def _handle_total(self, count: Count) -> None:
        self._total = build_dataframe(count)

    def _handle_annual(self, count: dict[int, Count]) -> None:
        for year in count.keys():
            self._annual[year] = build_dataframe(count[year])
