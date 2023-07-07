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
from dataclasses import dataclass, field
from functools import total_ordering
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.year import Year


@total_ordering
@dataclass
class Date(NullaryStructSchema):
    year: Year
    month: Month
    day: Day
    dayOfWeek: DayOfWeek = field(init=False, repr=False)

    def __post_init__(self):
        self.dayOfWeek = DayOfWeek(self.to_python_date().weekday())

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Date":
        schema = json_obj.get("schema")
        assert schema == "Date"
        underlying = json_obj.get("underlying")

        return Date(
            year=Year.from_typed_json(underlying.get("year")),
            month=Month.from_typed_json(underlying.get("month")),
            day=Day.from_typed_json(underlying.get("day")),
        )

    def to_python_date(self) -> datetime.date:
        return datetime.date(
            year=int(self.year.inner),
            month=self.month.inner,
            day=int(self.day.inner),
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Date):
            raise ValueError(f"Cannot compare {self} with {other}.")

        return self.to_python_date() < other.to_python_date()
