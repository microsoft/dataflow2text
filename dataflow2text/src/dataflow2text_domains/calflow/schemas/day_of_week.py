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

from dataflow2text.dataflow.schema import PrimitiveSchema


@dataclass(frozen=True)
class DayOfWeek(PrimitiveSchema):
    # Use 0-based values to be consistent with python datetime.
    inner: int

    def __post_init__(self):
        assert isinstance(self.inner, int)
        assert 0 <= self.inner < 7

    @classmethod
    def Monday(cls):
        return cls(0)

    @classmethod
    def Tuesday(cls):
        return cls(1)

    @classmethod
    def Wednesday(cls):
        return cls(2)

    @classmethod
    def Thursday(cls):
        return cls(3)

    @classmethod
    def Friday(cls):
        return cls(4)

    @classmethod
    def Saturday(cls):
        return cls(5)

    @classmethod
    def Sunday(cls):
        return cls(6)
