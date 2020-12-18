from pathlib import Path
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, ThemeType
from analysis.country.container import CountryContainer
from visualize.loader.normal import NormalLoader
from visualize.graph import Graph


class FlowMap(Graph):
    def __init__(self, usa: str, countries: CountryContainer, loader: NormalLoader, top: int = 20) -> None:
        self._usa: str = usa
        self._countries: CountryContainer = countries
        self._loader: NormalLoader = loader
        self._top: int = top

    def render(self, path: Path) -> None:
        geo = Geo(init_opts=opts.InitOpts(width="1366px", height="768px", theme=ThemeType.WESTEROS,
                                          page_title="Top Countries Mentioned by Donald Trump")
                  ).add_schema(maptype="world")
        self._load_coordinates(geo)

        total = self._loader.total.drop(index=[self._usa], errors="ignore").head(self._top)
        max_count = total.iloc[0, 0]
        max_width, max_point_size = 6, 60
        for row in total.itertuples():
            country = row.Index
            width = max_width * (row.count / max_count)
            geo.add("", [(self._usa, country)], type_=ChartType.LINES, symbol_size=6, symbol="circle",
                    linestyle_opts=opts.LineStyleOpts(curve=0.2, width=width))
            point_size = max_point_size * (row.count / max_count)
            geo.add("", [(country, row.count)], type_=ChartType.EFFECT_SCATTER, symbol_size=point_size)

        geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        geo.set_global_opts(title_opts=opts.TitleOpts(
            title="Top %d Countries Mentioned by Donald Trump" % total.count()))
        geo.render(str(path))

    def _load_coordinates(self, geo: Geo) -> None:
        for country in self._countries.all():
            loc = self._countries.location(country)
            geo.add_coordinate(country, loc.longitude, loc.latitude)
