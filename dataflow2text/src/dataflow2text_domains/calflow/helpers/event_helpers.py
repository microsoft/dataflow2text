import typing

import dataflow2text_domains.calflow.config
from dataflow2text.dataflow.schema import List
from dataflow2text_domains.calflow.errors.preamble_errors import InvalidPreambleError
from dataflow2text_domains.calflow.helpers.context_helpers import get_preamble
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.create_event_response import (
    CreateEventResponse,
)
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_id import EventId


def get_events(constraint: Constraint[Event]) -> List[Event]:
    preamble = get_preamble(dataflow2text_domains.calflow.config.current_dialogue_id)
    results: typing.List[Event] = []
    for _, response_obj in preamble.items():
        if response_obj.get("schema") != "CreateEventResponse":
            continue

        try:
            response = CreateEventResponse.from_typed_json(response_obj)
        except AssertionError as e:
            raise InvalidPreambleError(
                dataflow2text_domains.calflow.config.current_dialogue_id
            ) from e

        event = response.item
        if constraint.allows(event):
            results.append(event)

    results = sorted(results, key=lambda x: x.start)
    return List(type_arg=Event.dtype_ctor(), inner=results)


def get_event(event_id: EventId) -> typing.Optional[Event]:
    preamble = get_preamble(dataflow2text_domains.calflow.config.current_dialogue_id)
    for _, response_obj in preamble.items():
        if response_obj.get("schema") != "CreateEventResponse":
            continue

        try:
            response = CreateEventResponse.from_typed_json(response_obj)
        except AssertionError as e:
            raise InvalidPreambleError(
                dataflow2text_domains.calflow.config.current_dialogue_id
            ) from e

        event = response.item
        if event.id == event_id:
            return event

    return None
