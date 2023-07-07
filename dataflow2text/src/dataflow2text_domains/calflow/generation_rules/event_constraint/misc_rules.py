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
from dataflow2text.dataflow.schema import Interval
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.date_utils import Today
from dataflow2text_domains.calflow.functions.event_constraints import (
    EventAfterDateTime,
    EventAtTime,
    EventBeforeDateTime,
    EventBetweenEvents,
    EventDuringRange,
    EventDuringRangeDateTime,
    EventOnDate,
    EventOnDateAfterTime,
    EventOnDateBeforeTime,
    EventOnDateFromTimeToTime,
    EventOnDateTime,
    EventOnDateWithTimeRange,
)
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    EmptyStructConstraint,
)
from dataflow2text_domains.calflow.functions.time_constraints import Night
from dataflow2text_domains.calflow.helpers.date_helpers import get_today
from dataflow2text_domains.calflow.helpers.date_time_helpers import (
    get_date_time_interval_between_events,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
    get_date_from_datetime,
    get_time_from_datetime,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    # The template describes `[event]` twice to handle utterances like "with Georgia on August 5th at John's Office"
    # where the `[date]` is described in the middle.
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [date] }} "
        f"{{ {GenerationAct.PP.value} [event] }}"
    ),
)
def pp_handle_event_on_date_1(c: BaseFunction):
    match c:
        case EventOnDate(date, event):
            return {"event": event, "date": date}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template="from now until the end of the day",
)
def pp_handle_event_on_date_2(c: BaseFunction):
    match c:
        case EventOnDate(Today(), EmptyStructConstraint(_)):
            return {}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [event] }} {{ {GenerationAct.PP.value} [dateTime] }}",
)
def pp_handle_event_on_date_time(c: BaseFunction):
    match c:
        case EventOnDateTime(date_time, event):
            return {"event": event, "dateTime": date_time}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{{{ {{ {GenerationAct.PP.value} [timeRange] }} | {{ {GenerationAct.NP.value} [timeRange] }} }}}}"
    ),
)
def pp_handle_event_on_date_with_time_range(c: BaseFunction):
    match c:
        case EventOnDateWithTimeRange(event, timeRange):
            return {"event": event, "timeRange": timeRange}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [event] }} this {{ {GenerationAct.NP.value} [timeRange] }}",
)
def pp_handle_event_on_today_with_time_range(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case EventOnDateWithTimeRange(
            EventOnDate(date, event), timeRange
        ) if date.__value__ == get_today():
            return {"event": event, "timeRange": timeRange}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [event] }} tonight",
)
def pp_handle_event_on_today_with_night(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case EventOnDateWithTimeRange(
            EventOnDate(date, event), Night()
        ) if date.__value__ == get_today():
            return {"event": event}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"before {{ {GenerationAct.PP.value} [date] }} "
        f"at {{ {GenerationAct.NP.value} [time] }}"
    ),
)
def pp_handle_event_on_date_before_time_1(c):
    match c:
        case EventOnDateBeforeTime(date, event, time):
            return {"event": event, "date": date, "time": time}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [event] }} ",
)
def pp_handle_event_on_date_before_time_2(c):
    match c:
        case EventOnDateBeforeTime(_date, event, _time):
            return {"event": event}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [date] }} after {{ {GenerationAct.NP.value} [time] }}"
    ),
)
def pp_handle_event_on_date_after_time_1(c):
    match c:
        case EventOnDateAfterTime(date, event, time):
            return {"event": event, "date": date, "time": time}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"after {{ {GenerationAct.NP.value} [date] }} at {{ {GenerationAct.NP.value} [time] }}"
    ),
)
def pp_handle_event_on_date_after_time_2(c):
    match c:
        case EventOnDateAfterTime(date, event, time):
            return {"event": event, "date": date, "time": time}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [date] }} "
        f"{{ {GenerationAct.PP.value} [timeInterval] }}"
    ),
)
def pp_handle_event_on_date_from_time_to_time(c):
    match c:
        case EventOnDateFromTimeToTime(date, event, time1, time2):
            time_interval = Interval(lower=time1.__value__, upper=time2.__value__)
            return {
                "event": event,
                "date": date,
                "timeInterval": ValueCtor(time_interval),
            }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{{{ before {{ {GenerationAct.NP.value} [dateTime] }} | _ }}}}"
    ),
)
def pp_handle_event_before_date_time(c):
    match c:
        case EventBeforeDateTime(date_time, event):
            return {
                "event": event,
                "dateTime": date_time,
            }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [date] }} after {{ {GenerationAct.NP.value} [time] }}"
    ),
)
def pp_handle_event_after_date_time(c):
    match c:
        case EventAfterDateTime(event, date_time):
            return {
                "event": event,
                "date": get_date_from_datetime(date_time),
                "time": get_time_from_datetime(date_time),
            }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [event] }} at {{ {GenerationAct.NP.value} [time] }}",
)
def pp_handle_event_at_time(c):
    match c:
        case EventAtTime(event, time):
            return {
                "event": event,
                "time": time,
            }


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [dateRange] }} "
        f"{{ {GenerationAct.PP.value} [event] }}"
    ),
)
def pp_handle_event_during_range(c: BaseFunction):
    match c:
        case EventDuringRange(event, date_range):
            return {"event": event, "dateRange": date_range}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [dateTimeRange] }} "
        f"{{ {GenerationAct.PP.value} [event] }}"
    ),
)
def pp_handle_event_during_range_date_time(c: BaseFunction):
    match c:
        case EventDuringRangeDateTime(event, date_time_range):
            return {"event": event, "dateTimeRange": date_time_range}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.PP.value} [dateTimeInterval] }}"
        f"{{ {GenerationAct.PP.value} [event] }} "
    ),
)
def pp_handle_event_between_events(c: BaseFunction):
    match c:
        case EventBetweenEvents(event, event1, event2):
            interval = get_date_time_interval_between_events(
                event1.__value__, event2.__value__
            )
            if interval is None:
                return None

            return {"event": event, "dateTimeInterval": ValueCtor(interval)}
