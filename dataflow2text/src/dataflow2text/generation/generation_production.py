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

from dataclasses import dataclass
from typing import List

from dataflow2text.generation.generation_symbol import (
    GenerationNonterminal,
    GenerationSymbol,
    GenerationTerminal,
    render_generation_symbol,
)


@dataclass(frozen=True)
class GenerationProduction:
    """A CFG production for the generation model.

    Each production maps a single symbol on the left-hand side (`lhs`) to a sequence of symbols on the
    right-hand side (`rhs`).
    As a context-free production, `lhs` has to be a `GenerationNonterminal`, and `rhs` is a sequence of
    `GenerationSymbol`s which can be either `GenerationTerminal` or `GenerationNonterminal`.
    """

    name: str
    lhs: GenerationNonterminal
    rhs: List[GenerationSymbol]


def render_generation_production(production: GenerationProduction) -> str:
    rhs_str = " ".join(
        [
            render_generation_symbol(symbol, add_extra_space_for_terminals=True)
            for symbol in production.rhs
            if not (
                isinstance(symbol, GenerationTerminal) and symbol.inner.strip() == ""
            )
        ]
    )
    if len(rhs_str) == 0:
        rhs_str = '""'
    ret = f"{render_generation_symbol(production.lhs)} -> {rhs_str}"
    return ret
