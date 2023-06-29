from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, NullaryStructSchema
from dataflow2text_domains.calflow.schemas.place import Place


@dataclass(frozen=True)
class PlaceSearchResponse(NullaryStructSchema):
    results: List[Place]
