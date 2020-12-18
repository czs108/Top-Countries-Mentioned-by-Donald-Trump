from pathlib import Path
import pandas as pd


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
