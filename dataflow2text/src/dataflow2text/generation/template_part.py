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

from abc import ABC
from dataclasses import dataclass

import astor

from dataflow2text.generation.name_transformer import NameTransformer, parse_expression


class TemplatePart(ABC):
    """The base class of generation template symbols."""


@dataclass(frozen=True)
class TemplateTerminal(TemplatePart):
    """A terminal symbol in a generation template.

    It only contains a raw string.
    """

    inner: str

    def __str__(self) -> str:
        return self.inner


@dataclass(frozen=True)
class TemplateNonterminal(TemplatePart):
    """A nonterminal symbol in a generation template.

    It needs to be recursively expanded to produce a string.
    """

    # The name of the act corresponding to this nonterminal.
    act: str
    # The expression of the computation corresponding to the value that needs to be described by this nonterminal.
    # We do not directly store a Computation because the template can contain placeholder variables, and the `expand`
    # method would rewrite them into computations.
    expression: str

    def __str__(self) -> str:
        return f"{{{self.act} [{self.expression}]}}"

    def expand(self, transformer: NameTransformer) -> "TemplateNonterminal":
        new_node = transformer.visit(parse_expression(self.expression))
        new_expression = astor.to_source(new_node).strip()
        return TemplateNonterminal(self.act, new_expression)
