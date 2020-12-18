import json
from pathlib import Path
from typing import Any
import pandas as pd
from analysis.counter.counter import Count


class PathTuple:
    """
    Store the paths of count files.
    """
    def __init__(self) -> None:
        self.total: Path = None
        self.annual: Path = None


class Loader:
    """
    Load counts from JSON files and convert them to dataframes.
    """
    def load(self, paths: PathTuple) -> None:
        with paths.total.open(encoding="utf-8") as file:
            self._handle_total(json.load(file))
        with paths.annual.open(encoding="utf-8") as file:
            self._handle_annual(json.load(file))

    @property
    def total(self) -> Any:
        assert False

    @property
    def annual(self) -> dict:
        assert False

    def _handle_total(self, count: dict) -> None:
        assert False

    def _handle_annual(self, count: dict) -> None:
        assert False


def build_dataframe(count: Count) -> pd.DataFrame:
    """
    Create a dataframe from a count.
    """
    data = pd.DataFrame(pd.Series(count), columns=["count"])
    data.index.name = "country"
    return data.sort_values(by="count", ascending=False)
