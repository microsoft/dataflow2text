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

from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.time import Time


class TimeRangeConstraint(Constraint[Time]):
    def __init__(self, start_time: Time, end_time: Time):
        self.start_time = start_time
        self.end_time = end_time

        def predicate(dt: Time) -> bool:
            return start_time <= dt <= end_time

        super().__init__(type_arg=Time.dtype_ctor(), underlying=predicate)

    @classmethod
    def dtype_ctor(cls, *type_args: TypeName) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(Time.dtype_ctor())

    @property
    def dtype(self) -> TypeName:
        # Hack to deal with subtyping.
        return Constraint.dtype_ctor(Time.dtype_ctor())
