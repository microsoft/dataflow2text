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
from dataflow2text_domains.calflow.helpers.date_helpers import (
    get_today,
    get_tomorrow,
    get_yesterday,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_DATE,
    get_day_from_date,
    get_dow_from_date,
    get_month_from_date,
    get_year_from_date,
)
from dataflow2text_domains.calflow.schemas.date import Date


@generation(act=DEFAULT_ACT, typ=DTYPE_DATE, template=f"{{ {DEFAULT_ACT} [dateTime] }}")
def say_date(c: BaseFunction[Date]):
    match c:
        case GetAttr(StructAttribute("date", _), date_time):
            return {"dateTime": date_time}


@generation(act=GenerationAct.NP.value, typ=DTYPE_DATE, template="today")
def np_handle_today(c: BaseFunction[Date]):
    if c.__value__ == get_today():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DATE, template="yesterday")
def np_handle_yesterday(c: BaseFunction[Date]):
    if c.__value__ == get_yesterday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DATE, template="tomorrow")
def np_handle_tomorrow(c: BaseFunction[Date]):
    if c.__value__ == get_tomorrow():
        return {}
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE,
    template=f"{{ {GenerationAct.NP.value} [month] }} {{ {GenerationAct.Ordinal.value} [dayInner] }}",
)
def np_say_month_day(c: BaseFunction[Date]):
    return {
        "month": get_month_from_date(c),
        "dayInner": LongCtor(get_day_from_date(c).__value__.inner),
    }


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE,
    template=f"{{ {GenerationAct.NP.value} [month] }} [dayInner], [yearInner]",
)
def np_say_month_day_year(c: BaseFunction[Date]):
    return {
        "month": get_month_from_date(c),
        "dayInner": LongCtor(get_day_from_date(c).__value__.inner),
        "yearInner": LongCtor(get_year_from_date(c).__value__.inner),
    }


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE,
    template=f"{{ {GenerationAct.NP.value} [dow] }} the {{ {GenerationAct.Ordinal.value} [dayInner] }}",
)
def np_say_dow_and_day(c: BaseFunction[Date]):
    if c.__value__.month == get_today().month:
        return {
            "dow": get_dow_from_date(c),
            "dayInner": LongCtor(get_day_from_date(c).__value__.inner),
        }
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_DATE,
    template=f"{{ {GenerationAct.NP.value} [dow] }}",
)
def np_say_dow(c: BaseFunction[Date]):
    return {
        "dow": get_dow_from_date(c),
        "dayInner": LongCtor(get_day_from_date(c).__value__.inner),
    }
