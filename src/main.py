import json
import logging
from pathlib import Path

from clean.tuple import PathTuple as CleanerPathTuple
from clean.standard import Standard
from clean.segment import Segment

from analysis.country.container import CountryContainer
from analysis.counter.normal import NormalCounter
from analysis.counter.diplomacy import DiplomacyCounter
from analysis.counter.counter import Director, Counter

from visualize.loader.loader import PathTuple as LoaderPathTuple
from visualize.loader.normal import NormalLoader
from visualize.loader.diplomacy import DiplomacyLoader
from visualize.barchart import BarChart
from visualize.sankey import Sankey
from visualize.flowmap import FlowMap


JSON_INDENT = 4

data_dir = Path("..", "data")

countries = CountryContainer(Path("analysis", "country", "data.json"))


def clean() -> None:
    paths = CleanerPathTuple()
    paths.trump_tweet = data_dir.joinpath("origin", "donald_trump_tweet.csv")
    paths.president_speech = data_dir.joinpath("origin", "presidential_speech.csv")
    paths.state_of_union_address = data_dir.joinpath("origin", "state_of_the_union_address.csv")

    data = Standard(paths, data_dir.joinpath("clean")).handle()
    Segment(data_dir.joinpath("segment")).handle_dataframe(data)


def analyze() -> None:
    def write_json(counter: Counter, out_dir: Path) -> None:
        if not out_dir.exists():
            out_dir.mkdir(parents=True)
        with out_dir.joinpath("total_count.json").open("w", encoding="utf-8") as file:
            file.write(json.dumps(counter.total, indent=JSON_INDENT))
        with out_dir.joinpath("annual_count.json").open("w", encoding="utf-8") as file:
            file.write(json.dumps(counter.annual, indent=JSON_INDENT))

    normal = NormalCounter(countries)
    diplomacy = DiplomacyCounter(countries, normal)
    Director(data_dir.joinpath("segment"), [diplomacy]).handle()

    write_json(normal, data_dir.joinpath("count", "normal"))
    write_json(diplomacy, data_dir.joinpath("count", "diplomacy"))


def visualize() -> None:
    paths = LoaderPathTuple()
    paths.total = data_dir.joinpath("count", "normal", "total_count.json")
    paths.annual = data_dir.joinpath("count", "normal", "annual_count.json")
    normal = NormalLoader()
    normal.load(paths)

    paths = LoaderPathTuple()
    paths.total = data_dir.joinpath("count", "diplomacy", "total_count.json")
    paths.annual = data_dir.joinpath("count", "diplomacy", "annual_count.json")
    diplomacy = DiplomacyLoader()
    diplomacy.load(paths)

    usa = countries.main_name("United States")

    def barchart() -> None:
        chart = BarChart(usa, normal)
        chart.render(data_dir.joinpath("visualize", "bar-chart.html"))

    def sankey() -> None:
        chart = Sankey(usa, normal, diplomacy)
        chart.render(data_dir.joinpath("visualize", "sankey-diagram.html"))

    def flowmap() -> None:
        chart = FlowMap(usa, countries, normal)
        chart.render(data_dir.joinpath("visualize", "flow-map.html"))

    barchart()
    sankey()
    flowmap()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    try:
        clean()
        print("[*] The clean has finished.")

        analyze()
        print("[*] The analysis has finished.")

        visualize()
        print("[*] The visualize has finished.")

    except BaseException as err:
        logger.exception(err)
