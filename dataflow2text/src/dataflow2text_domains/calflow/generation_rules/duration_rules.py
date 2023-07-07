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

from dataflow2text.dataflow.function import BaseFunction, LongCtor
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_DURATION
from dataflow2text_domains.calflow.schemas.duration import Duration


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DURATION,
    template="{{ an | one | 1 }} hour",
)
def np_say_one_hour(c: BaseFunction[Duration]):
    if c.__value__.nanoseconds.inner != 0:
        return None

    if c.__value__.seconds.inner != 3600:
        return None

    return {}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DURATION,
    template="[num] hours",
)
def np_say_hours(c: BaseFunction[Duration]):
    if c.__value__.nanoseconds.inner != 0:
        return None

    num_hours = int(c.__value__.seconds.inner / 3600)
    if num_hours * 3600 != c.__value__.seconds.inner:
        return None

    if num_hours <= 1:
        return None

    return {"num": LongCtor(num_hours)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DURATION,
    template="a half hour",
)
def np_say_a_half_hour(c: BaseFunction[Duration]):
    if c.__value__.nanoseconds.inner != 0:
        return None

    if c.__value__.seconds.inner != 1800:
        return None

    return {}
