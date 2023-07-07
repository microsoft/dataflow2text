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
class ShowAsStatus(PrimitiveSchema):
    inner: str

    def __post_init__(self):
        if self.inner not in {
            "Free",
            "Tentative",
            "Busy",
            "OutOfOffice",
            "WorkingElsewhere",
            "Unknown",
            "UnexpectedValue",
        }:
            raise ValueError(f"Unknown ShowAsStatus: {self.inner}")

    @classmethod
    def Free(cls):
        return cls("Free")

    @classmethod
    def Tentative(cls):
        return cls("Tentative")

    @classmethod
    def Busy(cls):
        return cls("Busy")

    @classmethod
    def OutOfOffice(cls):
        return cls("OutOfOffice")

    @classmethod
    def WorkingElsewhere(cls):
        return cls("WorkingElsewhere")

    @classmethod
    def Unknown(cls):
        return cls("Unknown")

    @classmethod
    def UnexpectedValue(cls):
        return cls("UnexpectedValue")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "ShowAsStatus":
        schema_ = json_obj.get("schema")
        assert schema_ == "ShowAsStatus"
        underlying = json_obj.get("underlying")

        return ShowAsStatus(underlying)
