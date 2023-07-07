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
class ResponseStatusType(PrimitiveSchema):
    """

    Note `Null` and `NotResponded` are equivalent.
    TODO: There is only one use of `NotResponded` in CalFlow, and we should change that to `Null` and then
    change this schema.
    """

    inner: str

    def __post_init__(self):
        if self.inner not in {
            "Null",
            "Organizer",
            "TentativelyAccepted",
            "Accepted",
            "Declined",
            "NotResponded",
        }:
            raise ValueError(f"Unknown ResponseStatusType: {self.inner}")

    @classmethod
    def Null(cls):
        return cls("Null")

    @classmethod
    def Organizer(cls):
        return cls("Organizer")

    @classmethod
    def TentativelyAccepted(cls):
        return cls("TentativelyAccepted")

    @classmethod
    def Accepted(cls):
        return cls("Accepted")

    @classmethod
    def Declined(cls):
        return cls("Declined")

    @classmethod
    def NotResponded(cls):
        return cls("NotResponded")

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "ResponseStatusType":
        schema = json_obj.get("schema")
        assert schema == "ResponseStatusType"
        underlying = json_obj.get("underlying")
        assert underlying is not None

        if underlying == "None":
            return ResponseStatusType.Null()

        return ResponseStatusType(underlying)
