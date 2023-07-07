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

from typing import List

from nltk.tree import Tree

from dataflow2text.generation.generation_production import GenerationProduction
from dataflow2text.generation.generation_symbol import (
    GenerationNonterminal,
    GenerationTerminal,
)

_ALLOWED_TREE_LABEL_TYPES = (
    str,
    GenerationNonterminal,
    GenerationTerminal,
    GenerationProduction,
)


class GenerationTree(Tree):
    def __init__(self, label, children: List["GenerationTree"]):
        assert isinstance(label, _ALLOWED_TREE_LABEL_TYPES)
        if isinstance(
            label,
            (GenerationNonterminal, GenerationTerminal),
        ):
            # The children must be empty.
            assert not children

        super().__init__(label, children)

    def _set_node(self, value):
        # Needed to since IntelliJ treat this as abstractmethod.
        pass

    def _get_node(self):
        # Needed to since IntelliJ treat this as abstractmethod.
        pass

    def productions(self) -> List[GenerationProduction]:
        label = self.label()
        if isinstance(label, GenerationTerminal):
            return []

        if not isinstance(label, GenerationProduction):
            raise TypeError(
                f"Productions can only be generated from trees with `GenerationProduction` labels, got {label}."
            )

        prods = [label]
        for child in self:
            if not isinstance(child, GenerationTree):
                raise TypeError(
                    f"Productions can only be generated from trees with `GenerationTree` children, got {child}."
                )
            prods += child.productions()
        return prods

    def terminals(self) -> List[GenerationTerminal]:
        label = self.label()
        if isinstance(label, GenerationTerminal):
            return [label]
        terminals = []
        for child in self:
            terminals.extend(child.terminals())
        return terminals

    def get_string(self) -> str:
        return build_string(self.terminals())


def build_string(terminals: List[GenerationTerminal]) -> str:
    output_str = ""
    for terminal in terminals:
        o = terminal.inner
        if len(o) > 0 and (o[0].isspace() or o[0] in (".", "?", ",", ":", "'")):
            # If there is consecutive whitespace at the boundaries of terminals/nonterminals,
            # or whitespace followed by punctuation, discard extra whitespace.
            # This ensures that nonterminals that produce empty strings
            # don't cause additional undesired whitespace, e.g. in templates like "hello {NP [x]} world".
            output_str = output_str.rstrip()
        output_str += o
    return output_str.strip()
