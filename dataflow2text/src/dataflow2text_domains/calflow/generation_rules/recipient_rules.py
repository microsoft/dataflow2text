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
from dataflow2text_domains.calflow.functions.person_utils import (
    CurrentUser,
    FindManager,
    toRecipient,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_RECIPIENT,
    get_person_name_from_recipient,
)
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_RECIPIENT,
    template="{{ you | You }}",
)
def np_say_you(c: BaseFunction[Recipient]):
    if c.__value__.emailAddress.inner == CurrentUser().__value__.emailAddress:
        return {}
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_RECIPIENT,
    template=f"{{ {GenerationAct.NP.value} [name] }}",
)
def np_say_recipient_name(c: BaseFunction[Recipient]):
    return {"name": get_person_name_from_recipient(c)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_RECIPIENT,
    template="your manager",
)
def say_your_manager(c: BaseFunction[Recipient]):
    match c:
        case FindManager(toRecipient(CurrentUser())):
            return {}
