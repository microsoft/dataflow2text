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
