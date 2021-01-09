from pathlib import Path

from pyecharts import options as opts
from pyecharts.charts import Bar, Geo, Sankey as PySankey
from pyecharts.globals import ThemeType, ChartType

from country import Container
from visualize.loader import NormalLoader, DiplomacyLoader


class Graph:
    def render(self, path: Path) -> None:
        if not path.parent.exists():
            path.parent.mkdir(parents=True)


class BarChart(Graph):
    def __init__(self, usa: str, loader: NormalLoader, top: int = 10) -> None:
        assert top > 0
        super().__init__()
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
            title_opts=opts.TitleOpts(title=f"Top {len(countries)} Countries Mentioned by Donald Trump"))
        bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        bar.render(str(path))


class FlowMap(Graph):
    def __init__(self, usa: str, countries: Container, loader: NormalLoader, top: int = 20) -> None:
        assert top > 0
        super().__init__()
        self._usa: str = usa
        self._countries: Container = countries
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
            title=f"Top {total.count()['count']} Countries Mentioned by Donald Trump"))
        geo.render(str(path))

    def _load_coordinates(self, geo: Geo) -> None:
        for country in self._countries.all():
            loc = self._countries.location(country)
            geo.add_coordinate(country, loc.longitude, loc.latitude)


class Sankey(Graph):
    def __init__(self, usa: str, normal: NormalLoader, diplomacy: DiplomacyLoader,
                 first_lvl_top: int = 10, second_lvl_top: int = 3) -> None:
        assert first_lvl_top > 0 and second_lvl_top > 0
        super().__init__()
        self._usa: str = usa
        self._normal: NormalLoader = normal
        self._diplomacy: DiplomacyLoader = diplomacy
        self._first_lvl_top: int = first_lvl_top
        self._second_lvl_top: int = second_lvl_top

    def render(self, path: Path) -> None:
        super().render(path)
        links = []
        nodes = [{"name": self._usa}]
        total = self._normal.total.drop(index=[self._usa], errors="ignore").head(self._first_lvl_top)
        for row in total.itertuples():
            country = row.Index
            nodes.append({"name": country})
            links.append({"source": self._usa,
                          "target": country, "value": row.count})

            relations = self._diplomacy.total[country].head(self._second_lvl_top)
            for subrow in relations.itertuples():
                relation = subrow.Index
                node = f"{country} ↔ {relation}"
                nodes.append({"name": node})
                links.append({"source": country, "target": node, "value": subrow.count})

        sankey = PySankey(init_opts=opts.InitOpts(width="1366px", height="768px", theme=ThemeType.MACARONS,
                                                  page_title="Top Diplomatic Relations Mentioned by Donald Trump"))
        sankey.add("", nodes, links, node_gap=20,
                   linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"),
                   label_opts=opts.LabelOpts(position="right"), levels=[
                    opts.SankeyLevelsOpts(
                        depth=2,
                        itemstyle_opts=opts.ItemStyleOpts(color="source")
                    )])
        sankey.set_global_opts(title_opts=opts.TitleOpts(
            title_textstyle_opts=opts.TextStyleOpts(font_weight="bold"),
            title="Top Diplomatic Relations Mentioned by Donald Trump"))
        sankey.render(str(path))
