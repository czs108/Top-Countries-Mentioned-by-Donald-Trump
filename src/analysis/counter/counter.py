from pathlib import Path
from collections.abc import Sequence
import nltk
import spacy


Count = dict[str, int]


class Counter:
    def handle(self, year: int, nouns: Sequence[str]) -> None:
        """
        Handle nouns in a sentence related to a specific year.
        """
        assert False

    @property
    def total(self) -> dict:
        """
        Get the total count for 4 years.
        """
        assert False

    @property
    def annual(self) -> dict[int, dict]:
        """
        Get the annual count for each year.
        """
        assert False


class Director:
    """
    Read annual files, extract nouns and send them to counters.
    """
    _SENTENCE_CLUSTER: int = 3

    def __init__(self, in_dir: Path, counters: Sequence[Counter]) -> None:
        self._in_dir: Path = in_dir
        self._counters: Sequence[Counter] = counters
        self._nlp = spacy.load("en_core_web_sm")

    def handle(self) -> None:
        if len(self._counters) == 0:
            return
        for path in self._in_dir.glob("20??.txt"):
            if not path.is_file():
                continue
            with path.open(encoding="utf-8") as file:
                sentences = nltk.sent_tokenize(file.read())
                for i in range(0, len(sentences), self._SENTENCE_CLUSTER):
                    # Several sentences are made a group.
                    sentence_num = min(self._SENTENCE_CLUSTER, len(sentences) - i)
                    cluster = "".join([sentences[j] for j in range(i, i + sentence_num)])
                    for counter in self._counters:
                        nouns = self._nlp(cluster).noun_chunks
                        counter.handle(int(path.stem), [i.text for i in nouns])
