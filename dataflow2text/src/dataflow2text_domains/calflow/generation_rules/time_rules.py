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
    DTYPE_TIME,
    stringify_time,
)
from dataflow2text_domains.calflow.schemas.time import Time


@generation(act=DEFAULT_ACT, typ=DTYPE_TIME, template=f"{{ {DEFAULT_ACT} [dateTime] }}")
def say_it_start_at_time(c: BaseFunction[Time]):
    match c:
        case GetAttr(StructAttribute("time", _), date_time):
            return {"dateTime": date_time}


@generation(act=GenerationAct.NP.value, typ=DTYPE_TIME, template="[timeStr]")
def say_stringify_time_with_ampm(c: BaseFunction[Time]):
    return {"timeStr": stringify_time(c, True)}


@generation(act=GenerationAct.NP.value, typ=DTYPE_TIME, template="[timeStr]")
def say_stringify_time_without_ampm(c: BaseFunction[Time]):
    return {"timeStr": stringify_time(c, False)}
