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

"""Grammar rules for describing Constraint[Date]."""
from dataflow2text.dataflow.function import BaseFunction, GetAttr, ValueCtor
from dataflow2text.dataflow.schema import Interval, StructAttribute
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.date_range_constraints import (
    FullMonthofLastMonth,
    FullMonthofMonth,
    FullMonthofPreviousMonth,
    LastWeekNew,
    NextWeekend,
    NextWeekList,
    ThisWeek,
    ThisWeekend,
)
from dataflow2text_domains.calflow.functions.date_utils import Today
from dataflow2text_domains.calflow.functions.month_utils import NextMonth
from dataflow2text_domains.calflow.helpers.date_helpers import (
    last_date_of_month_in_year,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_DATE,
)
from dataflow2text_domains.calflow.schemas.date_range_constraint import (
    DateRangeConstraint,
)


@generation(
    act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="last month"
)
def pp_say_last_month(c):
    match c:
        case FullMonthofLastMonth():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_DATE,
    template=f"last {{ {GenerationAct.NP.value} [month] }}",
)
def pp_say_last_month_value_1(c):
    match c:
        case FullMonthofPreviousMonth(month):
            return {"month": month}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_DATE,
    template=f"last {{ {GenerationAct.NP.value} [month] }}",
)
def pp_say_last_month_value_2(c):
    match c:
        # pylint: disable=used-before-assignment
        case FullMonthofMonth(month, maybe_year) if (
            maybe_year.__value__.inner is not None
            and Today().__value__
            > last_date_of_month_in_year(month.__value__, maybe_year.__value__.inner)
        ):
            return {"month": month}


@generation(
    act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="this month"
)
def pp_say_this_month(c):
    match c:
        case FullMonthofMonth(GetAttr(StructAttribute("month", _), Today())):
            return {}


@generation(
    act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="next month"
)
def pp_say_next_month(c):
    match c:
        case FullMonthofMonth(NextMonth()):
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_DATE,
    template=f"in {{ {GenerationAct.NP.value} [month] }}",
)
def pp_in_month_value(c):
    match c:
        case FullMonthofMonth(month):
            return {"month": month}


@generation(act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="last week")
def pp_say_last_week(c):
    match c:
        case LastWeekNew():
            return {}


@generation(act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="next week")
def pp_say_next_week(c):
    match c:
        case NextWeekList():
            return {}


@generation(
    act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="next weekend"
)
def pp_say_next_weekend(c):
    match c:
        case NextWeekend():
            return {}


@generation(act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="this week")
def pp_say_this_week(c):
    match c:
        case ThisWeek():
            return {}


@generation(
    act=GenerationAct.PP.value, typ=DTYPE_CONSTRAINT_DATE, template="this weekend"
)
def pp_say_this_weekend(c):
    match c:
        case ThisWeekend():
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_DATE,
    template=f"{{ {GenerationAct.PP.value} [dateInterval] }}",
)
def pp_handle_date_range_constraint(c: BaseFunction[DateRangeConstraint]):
    if isinstance(c.__value__, DateRangeConstraint):
        date_interval = Interval(
            lower=c.__value__.start_date, upper=c.__value__.end_date
        )
        return {"dateInterval": ValueCtor(date_interval)}
    return None
