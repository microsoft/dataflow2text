from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, NullaryStructSchema
from dataflow2text_domains.calflow.schemas.event import Event


@dataclass(frozen=True)
class QueryResult(NullaryStructSchema):
    results: List[Event]
