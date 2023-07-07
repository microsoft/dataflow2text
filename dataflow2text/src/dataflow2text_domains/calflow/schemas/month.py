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

from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class Month(PrimitiveSchema):
    # Use 1-based values to be consistent with python datetime.
    inner: int

    def __post_init__(self):
        assert 1 <= self.inner <= 12

    @classmethod
    def January(cls):
        return cls(1)

    @classmethod
    def February(cls):
        return cls(2)

    @classmethod
    def March(cls):
        return cls(3)

    @classmethod
    def April(cls):
        return cls(4)

    @classmethod
    def May(cls):
        return cls(5)

    @classmethod
    def June(cls):
        return cls(6)

    @classmethod
    def July(cls):
        return cls(7)

    @classmethod
    def August(cls):
        return cls(8)

    @classmethod
    def September(cls):
        return cls(9)

    @classmethod
    def October(cls):
        return cls(10)

    @classmethod
    def November(cls):
        return cls(11)

    @classmethod
    def December(cls):
        return cls(12)

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Month":
        schema = json_obj.get("schema")
        assert schema == "Month"
        underlying = json_obj.get("underlying")

        return Month(_ALL_MONTHS.index(underlying) + 1)


_ALL_MONTHS = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]
