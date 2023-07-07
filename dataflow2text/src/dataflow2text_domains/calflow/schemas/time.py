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
from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Dict

from dataflow2text.dataflow.schema import Long, NullaryStructSchema, Number


@total_ordering
@dataclass(frozen=True)
class Time(NullaryStructSchema):
    hour: Long = Long(0)
    minute: Long = Long(0)
    second: Long = Long(0)
    nanosecond: Long = Long(0)

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Time":
        schema = json_obj.get("schema")
        assert schema == "Time"
        underlying = json_obj.get("underlying")

        hour = Number.from_typed_json(underlying.get("hour"))
        minute = Number.from_typed_json(underlying.get("minute"))
        second = Number.from_typed_json(underlying.get("second"))
        nanosecond = Number.from_typed_json(underlying.get("nanosecond"))

        return Time(
            hour=hour.to_long(),
            minute=minute.to_long(),
            second=second.to_long(),
            nanosecond=nanosecond.to_long(),
        )

    def to_python_time(self) -> datetime.time:
        return datetime.time(
            hour=int(self.hour.inner),
            minute=int(self.minute.inner),
            second=int(self.second.inner),
            microsecond=int(self.nanosecond.inner / 1000),
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Time):
            raise ValueError(f"cannot compare{self} with {other}.")

        return self.to_python_time() < other.to_python_time()
