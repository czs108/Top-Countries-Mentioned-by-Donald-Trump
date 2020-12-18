from pathlib import Path
from typing import TextIO
import pandas as pd
from clean.tuple import DataFrameTuple, PathTuple
from clean.standard import sort_date


class Segment:
    """
    Separate contents into different files by year.
    """
    def __init__(self, out_dir: Path) -> None:
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
        for row in data.itertuples():
            try:
                self._get_file(row.Index.year).write(row.content + "\n")
            except BaseException as err:
                print(err)

    def _get_file(self, year: int) -> TextIO:
        if year not in self._annual_files:
            self._annual_files[year] = self._out_dir.joinpath("%d.txt" % year).open("w", encoding="utf-8")
        return self._annual_files[year]

    def _close_files(self) -> None:
        for file in self._annual_files.values():
            file.close()
        self._annual_files.clear()
