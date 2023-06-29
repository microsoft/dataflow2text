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
