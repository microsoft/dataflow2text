from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.event_spec import EventSpec


@dataclass(frozen=True)
class CreateCommitEvent(NullaryStructSchema):
    data: EventSpec
