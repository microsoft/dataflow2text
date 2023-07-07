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
from dataflow2text_domains.calflow.functions.constraint_utils import negate
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        "{{ event | events }} {{ matching | named | _ }} "
        f"{{ {GenerationAct.NP.value} [constraint] }}"
    ),
)
def np_handle_event_subject_constraint(c: BaseFunction):
    match c:
        case EventExt.subject_constraint(constraint):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        "{{ event | events }} not {{ matching | named | _ }} "
        f"{{ {GenerationAct.NP.value} [constraint] }}"
    ),
)
def np_handle_event_subject_constraint_with_negate(c):
    match c:
        case EventExt.subject_constraint(negate(constraint)):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{{{ matching | named | _ }}}} {{ {GenerationAct.NP.value} [constraint] }}",
)
def pp_handle_event_subject_constraint(c: BaseFunction):
    match c:
        case EventExt.subject_constraint(constraint):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"not {{{{ matching | named | _ }}}} {{ {GenerationAct.NP.value} [constraint] }}",
)
def pp_handle_event_subject_constraint_with_negate(c: BaseFunction):
    match c:
        case EventExt.subject_constraint(negate(constraint)):
            return {"constraint": constraint}
