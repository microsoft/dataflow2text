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

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Dynamic, Unit
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event


@function
def ConfirmAndReturnAction() -> CalflowIntension[Dynamic]:
    """Confirms an action that needs confirmation and then returns the root computation from salience."""

    # TODO: Currently holding a dummy `Unit`.
    return CalflowIntension(
        underlying=Dynamic(type_arg=Unit.dtype_ctor(), inner=Unit())
    )


@function
def ConfirmUpdateAndReturnActionIntension(
    constraint: Constraint[Event],
) -> CalflowIntension[Dynamic]:
    """Like `ConfirmAndReturnAction`, but for an update with `constraint`."""

    # TODO: Currently holding a dummy `Unit`.
    return CalflowIntension(
        underlying=Dynamic(type_arg=Unit.dtype_ctor(), inner=Unit())
    )
