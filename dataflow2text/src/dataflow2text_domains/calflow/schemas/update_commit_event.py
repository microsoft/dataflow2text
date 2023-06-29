from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.event_id import EventId


@dataclass(frozen=True)
class UpdateCommitEvent(NullaryStructSchema):
    id: EventId
