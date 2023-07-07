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

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.attendees_utils import (
    AttendeeListHasRecipientConstraint,
)
from dataflow2text_domains.calflow.functions.constraint_utils import andConstraint
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_LIST_ATTENDEE,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_LIST_ATTENDEE,
    template=(
        f"{{ {GenerationAct.NP.value} [c1] }} "
        "{{ , | _ }} "
        "{{ and | _ }} "
        f"{{ {GenerationAct.NP.value} [c2] }}"
    ),
)
def np_handle_and_constraint(c: BaseFunction):
    match c:
        case andConstraint(c1, c2):
            return {"c1": c1, "c2": c2}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_LIST_ATTENDEE,
    template=f"{{ {GenerationAct.NP.value} [constraint] }}",
)
def np_handle_attendee_list_has_recipient_constraint(c: BaseFunction):
    match c:
        case AttendeeListHasRecipientConstraint(constraint):
            return {"constraint": constraint}
