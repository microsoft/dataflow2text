import copy
from itertools import takewhile
from typing import List, Optional, Tuple

from dataflow2text.generation.generation_production import GenerationProduction
from dataflow2text.generation.generation_symbol import (
    GenerationNonterminal,
    GenerationTerminal,
)
from dataflow2text.generation.generation_tree import GenerationTree, build_string


class GenerationTreeBuilder:
    """A builder that incrementally builds the underlying tree by applying productions.

    Attributes:
        _tree:
          The underlying tree being constructed by the builder.
        _frontier:
          A list of the locations within `_tree` of all subtrees that have not yet been expanded (i.e., those with a
          `GenerationUnexpandedNonterminalTreeLabel`) and all leaves that have not been completed (i.e., those with a
          `GenerationTerminalTreeLabel` but coming after an unexpanded nonterminal.).
           This list is sorted in left-to-right order of location within the tree.
        _completed_terminals:
          The list of `GenerationTerminal`s that have already been completed.
    """

    def __init__(self, start_symbol: GenerationNonterminal):
        root = GenerationTree(label=start_symbol, children=[])
        self._tree: GenerationTree = GenerationTree(
            label=start_symbol.act, children=[root]
        )
        self._frontier: List[Tuple[int, ...]] = [(0,)]
        self._completed_terminals: List[GenerationTerminal] = []

    @property
    def tree(self) -> GenerationTree:
        return self._tree

    def copy(self) -> "GenerationTreeBuilder":
        """Returns a copy of the builder.

        This is faster than `copy.deepcopy` and is sufficient for the bookkeeping in `SimpleGenerationParser`.
        """
        new_builder = copy.copy(self)
        # pylint: disable=protected-access
        new_builder._tree = self._tree.copy(deep=True)
        new_builder._frontier = self._frontier[:]
        new_builder._completed_terminals = self._completed_terminals[:]
        return new_builder

    def next_nonterminal(self) -> Optional[GenerationNonterminal]:
        if len(self._frontier) > 0:
            label = self._tree[self._frontier[0]].label()
            if not isinstance(label, GenerationNonterminal):
                raise ValueError(f"Expected a GenerationNonterminal, found {label}")
            return label
        return None

    def extend(self, production: GenerationProduction) -> None:
        nt = self.next_nonterminal()
        if nt is None:
            raise ValueError()

        assert isinstance(nt, GenerationNonterminal)
        if nt != production.lhs:
            raise ValueError()

        new_completed_terminals: List[GenerationTerminal] = list(
            takewhile(lambda x: isinstance(x, GenerationTerminal), production.rhs)  # type: ignore
        )

        pos = self._frontier.pop(0)
        offset = len(new_completed_terminals)
        new_frontier: List[Tuple[int, ...]] = [
            pos + (offset + idx,) for idx in range(len(production.rhs) - offset)
        ]
        self._frontier = new_frontier + self._frontier

        self._completed_terminals += new_completed_terminals

        subtree = _production_to_tree(production)
        # The `pos` would not be the root, otherwise we should just set `self._tree` to `subtree`.
        self._tree[pos] = subtree

        # process remaining completed terminals
        while len(self._frontier) > 0:
            next_pos = self._frontier[0]
            next_node_label = self._tree[next_pos].label()
            if not isinstance(next_node_label, GenerationTerminal):
                break
            self._frontier.pop(0)
            self._completed_terminals.append(next_node_label)

    def get_output_string(self) -> str:
        """Returns the output string produced by this builder so far.

        This function collapses consecutive whitespace between nonterminals, and also strips leading/trailing whitespace
        from the final string.
        """
        return build_string(self._completed_terminals)

    def get_suffix_string(self) -> str:
        """Returns the suffix string produced by this builder."""
        suffix_terminals: List[GenerationTerminal] = list(
            takewhile(lambda x: isinstance(x, GenerationTerminal), reversed(self._tree.leaves()))  # type: ignore
        )[::-1]
        return build_string(suffix_terminals)


def _production_to_tree(production: GenerationProduction) -> GenerationTree:
    return GenerationTree(
        label=production,
        children=[GenerationTree(label=elt, children=[]) for elt in production.rhs],
    )
