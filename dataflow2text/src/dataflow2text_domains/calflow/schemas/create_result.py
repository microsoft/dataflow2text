from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.event import Event


@dataclass(frozen=True)
class CreateResult(NullaryStructSchema):
    result: Event
