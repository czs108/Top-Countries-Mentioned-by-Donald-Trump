from typing import TYPE_CHECKING
from pathlib import Path
import os

import pandas as pd

from presidential_term import BEGIN_YEAR, END_YEAR

if TYPE_CHECKING:
    from typing import TextIO


class PathTuple:
    """
    Store the paths of datasets.
    """
    def __init__(self) -> None:
        self.trump_tweet: Path = None
        self.president_speech: Path = None
        self.state_of_union_address: Path = None


class DataFrameTuple:
    """
    Store the dataframes of datasets.
    """
    def __init__(self) -> None:
        self.trump_tweet: pd.DataFrame = None
        self.president_speech: pd.DataFrame = None
        self.state_of_union_address: pd.DataFrame = None


def sort_date(data: pd.DataFrame) -> None:
    """
    Sort a dataframe by its time index.
    """
    data["date"] = pd.to_datetime(data["date"])
    data.set_index("date", inplace=True)
    data.sort_index(inplace=True)


class Standard:
    """
    Unify the form of datasets, only remaining the "date" and "content" columns.
    """
    def __init__(self, in_paths: PathTuple, out_dir: Path) -> None:
        """
        The constructor.

        -- PARAMETERS --
        in_paths: The paths of original datasets.
        out_dir: A directory used to store standard datasets.
        """
        self._in_paths: PathTuple = in_paths
        self._out_dir: Path = out_dir
        self._data: DataFrameTuple = DataFrameTuple()

    def handle(self) -> DataFrameTuple:
        """
        Handle each dataset.
        """
        if not self._out_dir.exists():
            self._out_dir.mkdir(parents=True)

        self._handle_trump_tweet()
        self._handle_president_speech()
        self._handle_state_of_union_address()
        return self._data

    def _handle_trump_tweet(self) -> None:
        data = pd.read_csv(self._in_paths.trump_tweet)
        res = data.loc[:, ["date", "content"]]
        res["date"] = res["date"].str[:10]

        res = self._remove_irrelevance(res)
        self._data.trump_tweet = res
        self._write_csv_file(res, self._out_dir, Path(self._in_paths.trump_tweet).name)

    def _handle_president_speech(self) -> None:
        data = pd.read_csv(self._in_paths.president_speech)
        res = data.loc[data["President"] == "Donald Trump", ["Date", "Transcript"]]
        res.rename(columns={"Date": "date", "Transcript": "content"}, inplace=True)

        res = self._remove_irrelevance(res)
        self._data.president_speech = res
        self._write_csv_file(res, self._out_dir, Path(self._in_paths.president_speech).name)

    def _handle_state_of_union_address(self) -> None:
        data = pd.read_csv(self._in_paths.state_of_union_address)
        res = data.loc[data["President"] == "Donald Trump", ["Year", "Text"]]
        res.rename(columns={"Year": "date", "Text": "content"}, inplace=True)
        res["date"] = pd.to_datetime(res["date"], format="%Y").dt.strftime("%Y-01-01")

        res = self._remove_irrelevance(res)
        self._data.state_of_union_address = res
        self._write_csv_file(res, self._out_dir, Path(self._in_paths.state_of_union_address).name)

    @staticmethod
    def _remove_irrelevance(data: pd.DataFrame) -> pd.DataFrame:
        """
        Delete the contents that don't belong to Donald Trump's first presidential term.
        """
        sort_date(data)
        return data[f"{BEGIN_YEAR}":f"{END_YEAR}"]

    @staticmethod
    def _write_csv_file(data: pd.DataFrame, dir: Path, name: str) -> None:
        """
        Write a dataframe to a CSV file.

        -- PARAMETERS --
        data: A dataframe.
        dir: A directory to store the file.
        name: The name of the file.
        """
        data.to_csv(dir.joinpath(name), index=True)


class Segment:
    """
    Separate datasets into different annual files.
    """
    def __init__(self, out_dir: Path) -> None:
        """
        The constructor.

        -- PARAMETERS --
        out_dir: An output directory used to store annual files.
        """
        self._data: DataFrameTuple = None
        self._annual_files: dict[int, TextIO] = {}
        self._out_dir: Path = out_dir
        if not self._out_dir.exists():
            self._out_dir.mkdir(parents=True)

    def handle_csv(self, paths: PathTuple) -> None:
        """
        Handle data from CSV files.
        """
        data = DataFrameTuple()
        data.trump_tweet = pd.read_csv(paths.trump_tweet)
        sort_date(data.trump_tweet)
        data.president_speech = pd.read_csv(paths.president_speech)
        sort_date(data.president_speech)
        data.state_of_union_address = pd.read_csv(paths.state_of_union_address)
        sort_date(data.state_of_union_address)
        self.handle_dataframe(data)

    def handle_dataframe(self, data: DataFrameTuple) -> None:
        """
        Handle data from dataframes.
        """
        self._data = data
        self._handle_trump_tweet()
        self._handle_president_speech()
        self._handle_state_of_union_address()
        self._close_files()

    def _handle_trump_tweet(self) -> None:
        self._separate(self._data.trump_tweet)

    def _handle_president_speech(self) -> None:
        self._separate(self._data.president_speech)

    def _handle_state_of_union_address(self) -> None:
        self._separate(self._data.state_of_union_address)

    def _separate(self, data: pd.DataFrame) -> None:
        """
        Separate a dataframe into different annual files.
        """
        for row in data.itertuples():
            try:
                self._get_file(row.Index.year).write(row.content + os.linesep)
            except BaseException as err:
                print(err)

    def _get_file(self, year: int) -> TextIO:
        """
        Get the annual file corresponding to a specific year.
        """
        if year not in self._annual_files:
            self._annual_files[year] = self._out_dir.joinpath(f"{year}.txt").open("w", encoding="utf-8")
        return self._annual_files[year]

    def _close_files(self) -> None:
        """
        Close all files.
        """
        for file in self._annual_files.values():
            file.close()
        self._annual_files.clear()
