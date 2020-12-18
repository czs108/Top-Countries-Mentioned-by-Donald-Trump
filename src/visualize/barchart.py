from pathlib import Path
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType
from visualize.loader.normal import NormalLoader
from visualize.graph import Graph


class BarChart(Graph):
    def __init__(self, usa: str, loader: NormalLoader, top: int = 10) -> None:
        self._usa: str = usa
        self._loader: NormalLoader = loader
        self._top: int = top

    def render(self, path: Path) -> None:
        super().render(path)
        total = self._loader.total.drop(index=[self._usa], errors="ignore").head(self._top)
        countries = total.index.tolist()

        bar = Bar(init_opts=opts.InitOpts(width="1366px", height="768px", theme=ThemeType.WESTEROS,
                                          page_title="Top Countries Mentioned by Donald Trump"))
        bar.add_xaxis(countries)
        for year in self._loader.annual.keys():
            annual = self._loader.annual[year]
            values = []
            for country in countries:
                if country in annual.index:
                    values.append(int(annual.loc[country, "count"]))
                else:
                    values.append(0)
            bar.add_yaxis(str(year), values, label_opts=opts.LabelOpts(font_weight="bold"), stack="total")
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title="Top %d Countries Mentioned by Donald Trump" % len(countries)))
        bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        bar.render(str(path))
