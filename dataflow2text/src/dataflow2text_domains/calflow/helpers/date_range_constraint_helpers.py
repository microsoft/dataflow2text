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

import calendar
import datetime
from datetime import timedelta

from dataflow2text.dataflow.schema import Option
from dataflow2text_domains.calflow.helpers.context_helpers import get_current_datetime
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_date_to_calflow_date,
)
from dataflow2text_domains.calflow.helpers.date_helpers import (
    next_or_same_dow,
    previous_dow,
)
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_range_constraint import (
    DateRangeConstraint,
)
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.period import Period
from dataflow2text_domains.calflow.schemas.year import Year


def next_period(period: Period) -> DateRangeConstraint:
    """Returns a constraint from today to `period` after today."""
    start_date_py = get_current_datetime().date.to_python_date()
    end_date_py = start_date_py + period.to_python_relativedelta()
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )


def full_month_of_month(month: Month, year: Option[Year]) -> DateRangeConstraint:
    if year.inner is None:
        year_value = get_current_datetime().date.year.inner
    else:
        year_value = year.inner.inner
    _, num_days = calendar.monthrange(year_value, month.inner)
    start_date_py = datetime.date(year_value, month.inner, 1)
    end_date_py = datetime.date(year_value, month.inner, num_days)

    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )


def weekend_of_date(date: Date) -> DateRangeConstraint:
    if date.dayOfWeek in (DayOfWeek.Monday(), DayOfWeek.Tuesday()):
        sunday = previous_dow(date, DayOfWeek.Sunday())
    else:
        sunday = next_or_same_dow(date, DayOfWeek.Sunday())
    saturday = previous_dow(sunday, DayOfWeek.Saturday())
    return DateRangeConstraint(start_date=saturday, end_date=sunday)


def week_of_date(date: Date) -> DateRangeConstraint:
    date_py = date.to_python_date()
    start_date_py = date_py - timedelta(days=date_py.weekday())
    end_date_py = start_date_py + timedelta(days=6)
    return DateRangeConstraint(
        start_date=convert_python_date_to_calflow_date(start_date_py),
        end_date=convert_python_date_to_calflow_date(end_date_py),
    )
