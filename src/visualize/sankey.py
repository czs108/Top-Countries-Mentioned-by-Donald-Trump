from pathlib import Path
from pyecharts import options as opts
from pyecharts.charts import Sankey as PySankey
from pyecharts.globals import ThemeType
from visualize.loader.diplomacy import DiplomacyLoader
from visualize.loader.normal import NormalLoader
from visualize.graph import Graph


class Sankey(Graph):
    def __init__(self, usa: str, normal: NormalLoader, diplomacy: DiplomacyLoader,
                 first_lvl_top: int = 10, second_lvl_top: int = 3) -> None:
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
                node = "%s ↔ %s" % (country, relation)
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
