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

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_DAY_OF_WEEK
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Monday")
def np_monday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Monday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Tuesday")
def np_tuesday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Tuesday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Wednesday")
def np_wednesday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Wednesday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Thursday")
def np_thursday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Thursday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Friday")
def np_friday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Friday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Saturday")
def np_saturday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Saturday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Sunday")
def np_sunday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Sunday():
        return {}
    return None
