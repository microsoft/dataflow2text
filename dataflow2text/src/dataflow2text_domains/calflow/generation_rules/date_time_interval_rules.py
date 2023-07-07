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

import datetime

from dataflow2text.dataflow.function import BaseFunction, ValueCtor
from dataflow2text.dataflow.schema import Interval, Long
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_date_to_calflow_date,
)
from dataflow2text_domains.calflow.helpers.date_time_helpers import (
    localize_date_time_interval,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_INTERVAL_DATE_TIME,
)
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.time import Time

MIDNIGHT = Time(hour=Long(0), minute=Long(0), second=Long(0), nanosecond=Long(0))


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE_TIME,
    template=f"between {{ {GenerationAct.NP.value} [start] }} and {{ {GenerationAct.NP.value} [end] }}",
)
def pp_say_between_start_and_end(c: BaseFunction[Interval[DateTime]]):
    return {"start": ValueCtor(c.__value__.lower), "end": ValueCtor(c.__value__.upper)}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE_TIME,
    template=f"from {{ {GenerationAct.NP.value} [start] }} to {{ {GenerationAct.NP.value} [end] }}",
)
def pp_say_from_start_to_end(c: BaseFunction[Interval[DateTime]]):
    return {"start": ValueCtor(c.__value__.lower), "end": ValueCtor(c.__value__.upper)}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE_TIME,
    template=f"{{ {GenerationAct.PP.value} [dateInterval] }}",
)
def pp_say_date_interval(c: BaseFunction[Interval[DateTime]]):
    interval_local = localize_date_time_interval(c.__value__)
    start_date: Date = interval_local.lower.date
    end_date: Date = interval_local.upper.date
    if interval_local.upper.time == MIDNIGHT:
        end_date_py = end_date.to_python_date() - datetime.timedelta(days=1)
        end_date = convert_python_date_to_calflow_date(end_date_py)
    else:
        end_date = interval_local.upper.date
    date_interval: Interval[Date] = Interval(lower=start_date, upper=end_date)
    return {"dateInterval": ValueCtor(date_interval)}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE_TIME,
    template=f"{{ {GenerationAct.PP.value} [date] }} {{ {GenerationAct.PP.value} [timeInterval] }}",
)
def pp_say_date_and_time_interval(c: BaseFunction[Interval[DateTime]]):
    interval_local = localize_date_time_interval(c.__value__)
    if interval_local.lower.date == interval_local.upper.date:
        time_interval = Interval(
            lower=interval_local.lower.time, upper=interval_local.upper.time
        )
        return {
            "date": ValueCtor(interval_local.lower.date),
            "timeInterval": ValueCtor(time_interval),
        }
    return None


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_INTERVAL_DATE_TIME,
    template=f"before {{ {GenerationAct.NP.value} [end] }}",
)
def pp_say_before_end(c: BaseFunction[Interval[DateTime]]):
    return {"end": ValueCtor(c.__value__.upper)}
