from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.errors.calflow_runtime_error import (
    EmptyListError,
    ListIndexTooLargeError,
)
from dataflow2text_domains.calflow.helpers.event_helpers import get_events
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.query_event_response import (
    QueryEventResponse,
)


@function
def FindEventWrapperWithDefaults(constraint: Constraint[Event]) -> QueryEventResponse:
    events = get_events(constraint)
    return QueryEventResponse(results=events)


@function
def FindLastEvent(constraint: Constraint[Event]) -> Event:
    events = get_events(constraint)
    if len(events) == 0:
        raise EmptyListError()

    last = max(events.inner, key=lambda ev: ev.end)
    return last


@function
def FindNumNextEvent(constraint: Constraint[Event], number: Long) -> Event:
    events = get_events(constraint)
    if len(events) < number.inner:
        raise ListIndexTooLargeError(index=number.inner)
    return events[number.inner - 1]
