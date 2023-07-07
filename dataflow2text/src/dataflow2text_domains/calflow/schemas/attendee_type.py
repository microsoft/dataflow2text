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
class AttendeeType(PrimitiveSchema):
    inner: str

    @classmethod
    def Required(cls):
        return cls("Required")

    @classmethod
    def Optional(cls):
        return cls("Optional")

    @classmethod
    def Resource(cls):
        return cls("Resource")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "AttendeeType":
        schema_ = json_obj.get("schema")
        assert schema_ == "AttendeeType"
        underlying = json_obj.get("underlying")

        if underlying == "Required":
            return AttendeeType.Required()

        if underlying == "Optional":
            return AttendeeType.Optional()

        if underlying == "Resource":
            return AttendeeType.Resource()

        raise ValueError(f"Unknown attendee type: {underlying}")
