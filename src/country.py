import json
from pathlib import Path


class Location:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude: float = latitude
        self.longitude: float = longitude


class Container:
    def __init__(self, path: Path) -> None:
        """
        Store and check countries' information.
        """
        with path.open(encoding="utf-8") as file:
            countries = json.load(file)
        self._locations: dict[str, Location] = {}
        self._synonyms: dict[str, str] = {}
        for country in countries:
            if type(country["country"]) is str:
                name = country["country"]
                self._synonyms[name.upper()] = name
                self._locations[name] = Location(country["latitude"], country["longitude"])
            else:
                names = country["country"]
                main_name = names[0]
                self._locations[main_name] = Location(country["latitude"], country["longitude"])
                for i in range(0, len(names)):
                    self._synonyms[names[i].upper()] = main_name

    def all(self) -> list[str]:
        return list(self._locations.keys())

    def contain(self, name: str) -> bool:
        return name.upper() in self._synonyms

    def location(self, name: str) -> Location:
        main_name = self.main_name(name)
        return self._locations[main_name] if main_name else None

    def main_name(self, name: str) -> str:
        """
        Get the main name of a country.
        Some countries have several names of different forms, such as "USA" and "America".
        """
        name = name.upper()
        if name in self._synonyms:
            return self._synonyms[name]
        else:
            return ""
