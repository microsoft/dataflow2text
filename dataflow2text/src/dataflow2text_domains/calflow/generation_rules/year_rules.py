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

from dataflow2text.dataflow.function import BaseFunction, GetAttr, LongCtor
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_YEAR
from dataflow2text_domains.calflow.schemas.year import Year


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_YEAR,
    template=f"The {{ {GenerationAct.NP.value} [event] }} {{ {GenerationAct.VB.value} [end] }} in [year].",
)
def say_event_end_in_year(c: BaseFunction[Year]):
    match c:
        case GetAttr(
            StructAttribute("year", _),
            GetAttr(
                StructAttribute("date", _),
                GetAttr(StructAttribute("end", _), event) as end,
            ),
        ) as year:
            return {"year": LongCtor(year.__value__.inner), "end": end, "event": event}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_YEAR,
    template=f"The {{ {GenerationAct.NP.value} [event] }} {{ {GenerationAct.VB.value} [start] }} in [year].",
)
def say_event_start_in_year(c: BaseFunction[Year]):
    match c:
        case GetAttr(
            StructAttribute("year", _),
            GetAttr(
                StructAttribute("date", _),
                GetAttr(StructAttribute("start", _), event) as start,
            ),
        ) as year:
            return {
                "year": LongCtor(year.__value__.inner),
                "start": start,
                "event": event,
            }
