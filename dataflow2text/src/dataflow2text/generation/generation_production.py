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
