from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, NullaryStructSchema
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.time import Time


@dataclass(frozen=True)
class FindMeetingTimesResult(NullaryStructSchema):
    results: List[Constraint[Time]]
