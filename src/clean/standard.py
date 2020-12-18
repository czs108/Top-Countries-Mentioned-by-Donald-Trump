from pathlib import Path
import pandas as pd
from clean.tuple import PathTuple, DataFrameTuple
from presidential_term import BEGIN_YEAR, END_YEAR


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
    def __init__(self, paths: PathTuple, out_dir: Path) -> None:
        self._paths: PathTuple = paths
        self._out_dir: Path = out_dir
        self._data: DataFrameTuple = DataFrameTuple()

    def handle(self) -> DataFrameTuple:
        if not self._out_dir.exists():
            self._out_dir.mkdir(parents=True)

        self._handle_trump_tweet()
        self._handle_president_speech()
        self._handle_state_of_union_address()
        return self._data

    def _handle_trump_tweet(self) -> None:
        data = pd.read_csv(self._paths.trump_tweet)
        res = data.loc[:, ["date", "content"]]
        res["date"] = res["date"].str[:10]

        res = self._remove_irrelevance(res)
        self._data.trump_tweet = res
        self._write_csv_file(res, self._out_dir, Path(self._paths.trump_tweet).name)

    def _handle_president_speech(self) -> None:
        data = pd.read_csv(self._paths.president_speech)
        res = data.loc[data["President"] == "Donald Trump", ["Date", "Transcript"]]
        res.rename(columns={"Date": "date", "Transcript": "content"}, inplace=True)

        res = self._remove_irrelevance(res)
        self._data.president_speech = res
        self._write_csv_file(res, self._out_dir, Path(self._paths.president_speech).name)

    def _handle_state_of_union_address(self) -> None:
        data = pd.read_csv(self._paths.state_of_union_address)
        res = data.loc[data["President"] == "Donald Trump", ["Year", "Text"]]
        res.rename(columns={"Year": "date", "Text": "content"}, inplace=True)
        res["date"] = pd.to_datetime(res["date"], format="%Y").dt.strftime("%Y-01-01")

        res = self._remove_irrelevance(res)
        self._data.state_of_union_address = res
        self._write_csv_file(res, self._out_dir, Path(self._paths.state_of_union_address).name)

    @staticmethod
    def _remove_irrelevance(data: pd.DataFrame) -> pd.DataFrame:
        """
        Delete the contents that don't belong to Donald Trump's first presidential term.
        """
        sort_date(data)
        return data["%d" % BEGIN_YEAR:"%d" % END_YEAR]

    @staticmethod
    def _write_csv_file(data: pd.DataFrame, out_dir: Path, name: str) -> None:
        """
        Write a dataframe to a CSV file.
        """
        data.to_csv(out_dir.joinpath(name), index=True)
