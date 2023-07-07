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
from dataflow2text.dataflow.schema import Boolean, Option, String, TSchema
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_candidate_with_and_without_conflicts import (
    EventCandidatesWithAndWithoutConflicts,
)


@function
def IsBusy(eventCandidates: EventCandidatesWithAndWithoutConflicts) -> Boolean:
    """Returns true if the object passed in includes no Event candidates without conflicts."""
    raise NotImplementedError()


@function
def IsFree(eventCandidates: EventCandidatesWithAndWithoutConflicts) -> Boolean:
    raise NotImplementedError()


@function
def item(t: TSchema) -> Event:
    # In the CalFlow 2.0 data, the lispress program explicitly uses a type arg for `item` (e.g., `item[Dynamic](...)`).
    # However, unlike `roleConstraint` etc., this method does not need to be defined as a generic class in Python.
    # Therefore, we drop the type arg when converting the lispress program to python program.
    raise UnableToImplementError()


@function
def hasTeamsLink() -> Constraint[Option[String]]:
    raise NotImplementedError()
