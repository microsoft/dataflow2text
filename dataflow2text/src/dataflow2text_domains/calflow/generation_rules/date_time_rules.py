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

from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.date_time_helpers import astimezone
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_DATE_TIME
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.time import Time


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE_TIME,
    template=f"{{ {GenerationAct.NP.value} [date] }} at {{ {GenerationAct.NP.value} [time] }}",
)
def np_say_date_at_time(c: BaseFunction[DateTime]):
    current = get_current_datetime()
    local = astimezone(c.__value__, current.timeZone)
    return {"date": ValueCtor(local.date), "time": ValueCtor(local.time)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE_TIME,
    template=f"{{ {GenerationAct.NP.value} [date] }}",
)
def np_say_date(c: BaseFunction[DateTime]):
    current = get_current_datetime()
    local = astimezone(c.__value__, current.timeZone)
    return {"date": ValueCtor(local.date)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE_TIME,
    template=f"{{ {GenerationAct.NP.value} [time] }}",
)
def np_say_time(c: BaseFunction[DateTime]):
    current = get_current_datetime()
    local = astimezone(c.__value__, current.timeZone)
    return {"time": ValueCtor(local.time)}


@generation(act=GenerationAct.VB.value, typ=DTYPE_DATE_TIME, template="starts")
def vb_say_starts(c: BaseFunction[DateTime]):
    if c.__value__ >= get_current_datetime():
        return {}
    return None


@generation(act=GenerationAct.VB.value, typ=DTYPE_DATE_TIME, template="started")
def vb_say_started(c: BaseFunction[DateTime]):
    if c.__value__ < get_current_datetime():
        return {}
    return None


@generation(act=GenerationAct.VB.value, typ=DTYPE_DATE_TIME, template="ends")
def vb_say_ends(c: BaseFunction[DateTime]):
    if c.__value__ >= get_current_datetime():
        return {}
    return None


@generation(act=GenerationAct.VB.value, typ=DTYPE_DATE_TIME, template="ended")
def vb_say_ended(c: BaseFunction[DateTime]):
    if c.__value__ < get_current_datetime():
        return {}
    return None


def get_reference_datetime():
    """Returns the reference datetime for determining the copula tense.

    The agent utterance still uses "is" if the value being described falls in the same hour with the current timestamp,
    even if it is before the current timestamp.
    """
    current_datetime = get_current_datetime()
    return DateTime(
        date=current_datetime.date,
        time=Time(hour=current_datetime.time.hour),
        timeZone=current_datetime.timeZone,
    )


@generation(
    act=GenerationAct.Copula.value, typ=DTYPE_DATE_TIME, template="{{ is | 's }}"
)
def cop_say_is(c: BaseFunction):
    reference_datetime = get_reference_datetime()
    if c.__value__ >= reference_datetime:
        return {}

    return None


@generation(act=GenerationAct.Copula.value, typ=DTYPE_DATE_TIME, template="was")
def cop_say_was(c: BaseFunction):
    reference_datetime = get_reference_datetime()
    if c.__value__ < reference_datetime:
        return {}

    return None
