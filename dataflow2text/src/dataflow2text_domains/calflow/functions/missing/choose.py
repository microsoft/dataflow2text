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
from dataflow2text.dataflow.schema import Long, TSchema
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.update_event_response import (
    UpdateEventResponse,
)


@function
def ChoosePersonFromConstraint(
    constraint: Constraint[Recipient], intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()


@function
def ChooseCreateEventFromConstraint(
    constraint: Constraint[Event], intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()


@function
def ChooseUpdateEvent(
    index: Long, intension: CalflowIntension[UpdateEventResponse]
) -> CalflowIntension[UpdateEventResponse]:
    raise NotImplementedError()


@function
def ChooseUpdateEventFromConstraint(
    constraint: Constraint[Event], intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()


@function
def ChooseUpdateEventFromConstraintWrapper(constraint: Constraint[Event]) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseUpdateEventWrapper(index: Long) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseCreateEventFromConstraintWrapper(constraint: Constraint[Event]) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChoosePersonFromConstraintWrapper(constraint: Constraint[Recipient]) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseCreateEventWrapper(index: Long) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseCreateEvent(
    index: Long, intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()
