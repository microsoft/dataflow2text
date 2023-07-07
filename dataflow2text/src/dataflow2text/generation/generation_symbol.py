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

import json
from abc import ABC
from dataclasses import dataclass

from dataflow2text.dataflow.function import BaseFunction, hash_computation


class GenerationSymbol(ABC):
    pass


@dataclass(frozen=True)
class GenerationNonterminal(GenerationSymbol):
    """
    A nonterminal in the generation grammar.
    """

    act: str
    computation: BaseFunction

    def __hash__(self) -> int:
        return hash(f"{self.act}_{hash_computation(self.computation)}")


@dataclass(frozen=True)
class GenerationTerminal(GenerationSymbol):
    inner: str


def render_generation_symbol(
    symbol: GenerationSymbol,
    add_extra_space_for_terminals: bool = False,
) -> str:

    if isinstance(symbol, GenerationNonterminal):
        return f"{symbol.act}_{hash_computation(symbol.computation)}"

    if isinstance(symbol, GenerationTerminal):
        # The grammar in CLAMP is at character-level from what I understand. So we need to add extra space tokens.
        # However, adding such tokens in a consistent manner and avoiding multiple space repetitions is tricky.
        # To keep things simple, we add " "?
        # This possibly increases the size of the grammar, but we might still prefer it for simplicity
        inner = symbol.inner.strip()
        # Use `json.dumps` to add surrounding quotes and escape inner quotes.
        if add_extra_space_for_terminals:
            return '" "? ' + f"{json.dumps(inner)}"
        else:
            return f"{json.dumps(inner)}"

    raise TypeError(f"Cannot render {symbol}.")
