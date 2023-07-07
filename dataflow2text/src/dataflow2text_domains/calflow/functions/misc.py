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
from dataflow2text.dataflow.schema import List, Long, TSchema, Unit
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.path import Path


@function
def AgentStillHere() -> Unit:
    return Unit()


@function
def CancelScreen() -> Unit:
    return Unit()


@function
def DoNotConfirm() -> Unit:
    return Unit()


@function
def UserPauseResponse() -> Unit:
    return Unit()


@function
def numberToIndexPath(number: Long) -> Path:
    return Path(f"[{number}]")


# pylint: disable=redefined-builtin
@function
def minBy(list: List[TSchema], path: Path) -> TSchema:
    raise NotImplementedError()


@function
def roomRequest() -> Constraint[LocationKeyphrase]:
    """Returns a constraint that requests a conference room.

    For now the predicate always returns true.
    """

    def predicate(x: LocationKeyphrase) -> bool:
        return True

    return Constraint(type_arg=LocationKeyphrase.dtype_ctor(), underlying=predicate)


@function
def RepeatAgent() -> Unit:
    raise NotImplementedError()
