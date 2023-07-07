# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
