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

from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_DURATION,
    get_start_from_event,
)
from dataflow2text_domains.calflow.schemas.event import Event


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_DURATION,
    template=(
        "{{ The | the }} {{ event | _ }} "
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"for {{ {GenerationAct.NP.value} [duration] }}."
    ),
)
def say_event_duration_1(c: BaseFunction[Event]):
    match c:
        case GetAttr(
            StructAttribute("duration", _),
            event,
        ) as duration:
            return {
                "event": event,
                "start": get_start_from_event(event),
                "duration": duration,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_DURATION,
    template=(
        "It "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"for {{ {GenerationAct.NP.value} [duration] }}."
    ),
)
def say_event_duration_2(c: BaseFunction[Event]):
    match c:
        case GetAttr(
            StructAttribute("duration", _),
            event,
        ) as duration:
            return {
                "event": event,
                "start": get_start_from_event(event),
                "duration": duration,
            }
