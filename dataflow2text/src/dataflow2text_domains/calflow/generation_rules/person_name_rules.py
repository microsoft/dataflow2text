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

from dataflow2text.dataflow.function import BaseFunction, StringCtor
from dataflow2text.generation.constants import TOSTRING_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_PERSON_NAME,
    get_first_name_from_name,
    get_name_from_person_name,
)
from dataflow2text_domains.calflow.schemas.person_name import PersonName


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_PERSON_NAME,
    template=f"{{ {TOSTRING_ACT} [name] }}",
)
def np_say_full_name(c: BaseFunction[PersonName]):
    return {"name": get_name_from_person_name(c)}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_PERSON_NAME,
    template=f"{{ {TOSTRING_ACT} [firstName] }}",
)
def np_say_first_name(c: BaseFunction[PersonName]):
    return {"firstName": get_first_name_from_name(get_name_from_person_name(c))}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_PERSON_NAME,
    template=f"{{ {TOSTRING_ACT} [firstName] }}",
)
def np_say_first_name_lowercased(c: BaseFunction[PersonName]):
    return {
        "firstName": get_first_name_from_name(
            get_name_from_person_name(c), lowercase=True
        )
    }


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_PERSON_NAME,
    template=f"{{ {TOSTRING_ACT} [name] }}",
)
def np_say_full_name_stripped(c: BaseFunction[PersonName]):
    """Like `np_say_full_name`, but the name tokens are normalized so that only the first character is capitalized
    and remaining characters are lower-cased.
    """
    name_tokens = c.__value__.name.inner.split(" ")
    processed_name = " ".join([token.capitalize() for token in name_tokens])
    return {"name": StringCtor(processed_name)}
