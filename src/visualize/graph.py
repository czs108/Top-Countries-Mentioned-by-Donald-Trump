from pathlib import Path


class Graph:
    def render(self, path: Path):
        if not path.parent.exists():
            path.parent.mkdir(parents=True)