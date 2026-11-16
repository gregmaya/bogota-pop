"""Which sources have their own ingest module.

A source listed here is converted by its own module (layer, filter, arrival
figures). Any other source uses the plain ``convert.to_geoparquet``.
"""

from bogota_pop.ingest import convert, dane_mgn, uaecd
from bogota_pop.ingest.core import Converter

CONVERTERS: dict[str, Converter] = {
    dane_mgn.SOURCE_ID: dane_mgn.convert,
    dane_mgn.CLASE_SOURCE_ID: dane_mgn.convert_clase,
    **uaecd.CONVERTERS,
}


def converter_for(source_id: str) -> Converter:
    """Return the convert function for a source (its own, or the plain default)."""
    return CONVERTERS.get(source_id, convert.to_geoparquet)
