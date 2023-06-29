from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Option, String
from dataflow2text_domains.calflow.schemas.event import EventId
from dataflow2text_domains.calflow.schemas.join_event_command import JoinEventCommand


@function
def joinEventCommand(event_id: EventId) -> JoinEventCommand:
    """Crates a JoinEventCommand command for an event ID."""
    return JoinEventCommand(
        event_id=event_id,
        teamsMeetingLink=Option(type_arg=String.dtype_ctor(), inner=None),
    )


@function
def joinEventCommandWithLink(
    event_id: EventId, teamsMeetingLink: String
) -> JoinEventCommand:
    """Crates a JoinEventCommand command for an event ID with a teams meeting link."""
    return JoinEventCommand(
        event_id=event_id, teamsMeetingLink=Option.from_value(teamsMeetingLink)
    )
