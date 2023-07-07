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

from dataflow2text.dataflow.schema import Long, NullaryStructSchema


@total_ordering
@dataclass(frozen=True)
class Duration(NullaryStructSchema):
    seconds: Long = Long(0)
    nanoseconds: Long = Long(0)

    def to_python_duration(self) -> datetime.timedelta:
        return datetime.timedelta(
            seconds=self.seconds.inner,
            # This loss of precision may introduce bugs, but we assume this does not matter in practice.
            microseconds=int(self.nanoseconds.inner / 1000),
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Duration):
            raise ValueError(f"cannot compare{self} with {other}.")

        return self.to_python_duration() < other.to_python_duration()
