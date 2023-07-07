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

from dataflow2text.dataflow.function import BaseFunction, StringCtor
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.event_utils import EventAttendance
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_ATTENDANCE_RESPONSE,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_ATTENDANCE_RESPONSE,
    template=(
        f"I will {{ {GenerationAct.VB.value} [response] }} {{ {GenerationAct.NP.value} [event] }} "
        'and send a response to the organizer with the following comment: "[comment]". '
        "Is that ok?"
    ),
)
def handle_event_attendance_with_comment(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case EventAttendance(
            event,
            response,
            comment,
            _,
        ) if comment.__value__.inner != "":
            return {
                "event": event,
                "comment": StringCtor(comment.__value__.inner),
                "response": response,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_ATTENDANCE_RESPONSE,
    template=(
        f"I will {{ {GenerationAct.VB.value} [response] }} {{ {GenerationAct.NP.value} [event] }}. "
        "Is that ok?"
    ),
)
def handle_event_attendance_without_comment(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case EventAttendance(
            event,
            response,
            comment,
            _,
        ) if comment.__value__.inner == "":
            return {
                "event": event,
                "comment": StringCtor(comment.__value__.inner),
                "response": response,
            }
