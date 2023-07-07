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
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.calflow_yield import Yield
from dataflow2text_domains.calflow.functions.do import do
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct


@generation(act=DEFAULT_ACT, template=f"{{ {DEFAULT_ACT} [x] }}")
def handle_yield(c: BaseFunction):
    match c:
        case Yield(x):
            return {"x": x}


@generation(
    act=DEFAULT_ACT,
    template=f"{{{{ {{ {DEFAULT_ACT} [x] }} | _ }}}} {{ {DEFAULT_ACT} [y] }}",
)
def handle_do(c: BaseFunction):
    match c:
        case do(x, y):
            return {"x": x, "y": y}


@generation(
    act=GenerationAct.PP.value,
    template="",
)
def pp_say_null(c: BaseFunction):
    """A dummy rule so that the generation model can sometimes skip describing PP constituents."""
    return {}


@generation(
    act=GenerationAct.PP.value,
    template=f"{{{{ in | on | at | _ }}}} {{ {GenerationAct.NP.value} [c] }}",
)
def pp_base_rule(c: BaseFunction):
    """PP -> IN NP

    We also rewrite PP into a bare NP without a preposition since we sometimes treat "today/tomorrow" as PP.
    """
    return {"c": c}
