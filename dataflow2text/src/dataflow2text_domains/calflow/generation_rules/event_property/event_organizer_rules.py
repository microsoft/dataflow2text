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

from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_RECIPIENT
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_RECIPIENT,
    # A more precise rule should choose between "is" and "are" based on the organizer.
    # We leave such decision to the model instead of hard-coded in the generation rules.
    template=(
        f"{{ {GenerationAct.NP.value} [organizer] }} "
        "{{ is | are }} the organizer of "
        f"{{ {GenerationAct.NP.value} [event] }}."
    ),
)
def say_event_organizer(c: BaseFunction[Recipient]):
    match c:
        case GetAttr(
            StructAttribute("organizer", _),
            event,
        ) as organizer:
            return {
                "event": event,
                "organizer": organizer,
            }
