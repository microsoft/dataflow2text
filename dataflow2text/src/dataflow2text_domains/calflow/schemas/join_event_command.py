from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema, Option, String
from dataflow2text_domains.calflow.schemas.event_id import EventId


@dataclass(frozen=True)
class JoinEventCommand(NullaryStructSchema):
    event_id: EventId
    teamsMeetingLink: Option[String]
