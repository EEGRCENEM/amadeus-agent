from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from agent.types import ISOCountyCode, IATACode, Airport


class AirportService:
    def __init__(self) -> None:
        path = Path(__file__).parent.parent / "resources" / "airport-codes.csv"
        df = pd.read_csv(path, index_col=0)
        self._document = df.dropna()

    def list_airports(self) -> Iterable[Airport]:
        for _idx, row in self._document.iterrows():
            yield Airport.model_validate(dict(row))

    def count_airports(self) -> int:
        return len(self._document)

    def find_iata_code_for_airport(self, search_term: str) -> IATACode | None:
        for _idx, row in self._document[
            self._document.name.str.contains(search_term)
        ].iterrows():
            return Airport.model_validate(dict(row)).iata_code
        return None

    def find_airport_by_iata_code(self, iata_code: IATACode) -> Airport | None:
        for _idx, row in self._document[
            self._document.iata_code == iata_code
        ].iterrows():
            return Airport.model_validate(dict(row))
        return None

    def find_airports_in_country(self, iso_country: ISOCountyCode) -> Iterable[Airport]:
        for _idx, row in self._document[
            self._document.iso_country == iso_country
        ].iterrows():
            yield Airport.model_validate(dict(row))
