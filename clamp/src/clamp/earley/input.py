# TODO: Implement a position in a language model trie whose edges are labeled
# with word pieces (so, really a radix tree; we can cache the outgoing edges
# from each node rather than repeatedly querying the language model).
#
# Scanning a terminal might traverse multiple edges because the terminal
# consists of several word pieces, or part of an edge, because a terminal
# matches only part of a word piece (in which case the returned position will be
# partway along an edge, which we can represent as the destination position of
# that edge paired with a residual substring that we still have to read to
# arrive at that destination position).  Both can happen at once, e.g., a
# terminal might complete an existing partial edge and then traverse 2 more
# edges and then go partway along the next edge, like staggered bricks in a
# wall.
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Sized,
    SupportsBytes,
    Tuple,
    TypeVar,
    cast,
)

import numpy as np

from clamp.util.keydefaultdict import KeyDefaultDict

# This is a type variable, since the terminal symbols of the CFG could
# be anything that matches against input prefixes (e.g., regexps or integerized tokens).
# Make sure that the Terminal type is disjoint from Nonterm, since any Nonterm
# on a rule RHS will be treated as a Nonterm.
Terminal = TypeVar("Terminal")

# We would like P to be a subtype of Position[Terminal], but generic bounds aren't allowed.
P = TypeVar("P", bound="Position")


class Position(ABC, Sized, Generic[Terminal]):
    """
    An abstract representation of a position in an input string, lattice, or trie.
    Concrete implementations of Position might also provide access to the prefix read so far
    and the weight of that prefix.
    """

    @abstractmethod
    def scan(self: P, terminal: Terminal) -> Iterable["P"]:
        """
        Return all the new positions we can get to from here by scanning terminal.

        TODO: The type on this is not precise enough.  We really want (P, Terminal) -> Iterable[P],
        and we should be able to write self: P to do this, but we can't declare P to be bounded
        by Position[Terminal] because that's generic.
        """

    @abstractmethod
    def is_final(self) -> bool:
        """Is this a final position in the input, i.e., are we allowed to end here?"""

    @abstractmethod
    def get_span(self: P, other: P) -> Sequence[Terminal]:
        """
        Returns the terminals that range from `self` to `other`, inclusive.

        The arguments should satisfy `self < other`.
        """

    @abstractmethod
    def __len__(self) -> int:
        """
        A measurement of how far along the position is in the input (e.g., the prefix length).
        May be used by some control strategies to process positions in left-to-right order.
        """

    def __lt__(self, other: "Position[Terminal]") -> bool:
        return len(self) < len(other)


class SequencePosition(Position[Terminal]):
    """A position in a list of tokens.

    WARNING: Do not modify the contents of `tokens` outside this class.
    """

    def __init__(self, tokens: Sequence[Terminal], i: int = 0):
        self._tokens: Sequence[Terminal] = tokens
        self._i: int = i

    def scan(self, terminal: Terminal) -> Iterable["SequencePosition[Terminal]"]:
        if self.is_final() or self._tokens[self._i] != terminal:
            return ()
        else:
            return (SequencePosition[Terminal](self._tokens, self._i + 1),)

    def is_final(self) -> bool:
        return self._i == len(self._tokens)

    def get_span(self, other: "SequencePosition[Terminal]") -> Sequence[Terminal]:
        # pylint: disable=protected-access
        if self._tokens is not other._tokens:
            raise ValueError(
                "Can only get span between Positions belonging to the same sequence"
            )
        if not self < other:
            raise ValueError("Can only get span between Positions in increasing order")
        return self._tokens[self._i : other._i]

    def __len__(self) -> int:
        return self._i

    def __repr__(self) -> str:
        prefix = self._tokens[: self._i]
        # Turn some common kinds of `Sequence[Terminal]` into readable strings.
        # This is only used for debugging so we're not concerned about covering all the cases.
        if hasattr(prefix, "__bytes__"):
            prefix_str = bytes(cast(SupportsBytes, prefix)).decode("utf-8")
        elif (
            isinstance(prefix, np.ndarray)
            and prefix.dtype == np.uint8
            and prefix.ndim == 1
        ):
            prefix_str = bytes(prefix).decode("utf-8")
        else:
            prefix_str = "".join(str(c) for c in prefix)
        if prefix_str:
            return f"({self._i}) {prefix_str}"
        else:
            return f"({self._i})"

    def __eq__(self, other: "SequencePosition[Terminal]") -> bool:  # type: ignore
        """Uses reference equality for self._tokens.

        If you construct a separate SequencePosition from the same tokens,
        but stored in a different container, they will not compare equal.
        """

        return (
            isinstance(other, SequencePosition)
            and self._tokens is other._tokens
            and self._i == other._i
        )

    def __hash__(self) -> int:
        return hash((id(self._tokens), self._i))


@dataclass(frozen=True)
class StringPosition(Position[str]):
    """
    A position in an untokenized string of characters.
    Allows us to tokenize as we go.
    """

    string: str
    i: int = 0

    def scan(self, terminal: str) -> Iterable["StringPosition"]:
        if self.string.startswith(terminal, self.i):
            return [StringPosition(self.string, self.i + len(terminal))]
        else:
            return []

    def is_final(self) -> bool:
        return self.i == len(self.string)

    def get_span(self, other: "StringPosition") -> Sequence[str]:
        if self.string != other.string:
            raise ValueError(
                "Can only get span between Positions belonging to the same sequence"
            )
        if not self < other:
            raise ValueError("Can only get span between Positions in increasing order")
        return self.string[self.i : other.i]

    def __len__(self) -> int:
        return self.i

    def __repr__(self) -> str:
        return self.string[: self.i] + "^" + self.string[self.i :]


class SigmaStarTriePosition(Position[Terminal]):
    """
    A Position in a lazy trie of all possible token sequences (Σ*).
    Thus, it matches any prefix and retains the history of that prefix.
    This is useful in enumerating all strings that are accepted by the grammar.
    """

    # parent node if any
    _prev: Optional["SigmaStarTriePosition[Terminal]"]
    # label of edge to us from parent
    _last: Optional[Terminal]
    # length of path to us from root
    _len: int
    # transition function to child node: expanded on demand
    _next: KeyDefaultDict[Terminal, "SigmaStarTriePosition[Terminal]"]

    def __init__(
        self, edge: Optional[Tuple["SigmaStarTriePosition[Terminal]", Terminal]] = None
    ):
        """Constructs the root trie node by default, or a child of another node via a labeled edge."""
        if edge is None:
            self._prev, self._last, self._len = None, None, 0  # root node
        else:
            self._prev, self._last = edge  # child node
            self._len: int = 0 if self._prev is None else 1 + len(self._prev)

        self._next = KeyDefaultDict(
            lambda terminal: SigmaStarTriePosition[Terminal]((self, terminal))
        )

    def scan(self, terminal: Terminal) -> Iterable["SigmaStarTriePosition[Terminal]"]:
        return (self._next[terminal],)

    def is_final(self) -> bool:
        return True  # any string is a valid prefix, so we can always stop here

    def get_span(self, other: "SigmaStarTriePosition[Terminal]") -> Sequence[Terminal]:
        # pylint: disable=protected-access
        if not self < other:
            raise ValueError("Can only get span between Positions in increasing order")

        reversed_terminals: List[Terminal] = []
        cur = other
        while cur is not self:
            maybe_last_terminal = cur._last
            if cur._prev is None:
                break
            cur = cur._prev
            assert maybe_last_terminal is not None
            reversed_terminals.append(maybe_last_terminal)

        if cur is self:
            reversed_terminals.reverse()
            return reversed_terminals
        else:
            raise ValueError(
                "The two positions for `get_span` were not part of the same trie"
            )

    def __len__(self) -> int:
        return self._len

    def last(self) -> Optional[Terminal]:
        """The Terminal immediately before this Position, if any."""
        return self._last

    def prefix(self) -> List[Terminal]:
        """The sequence of Terminals leading up to this Position."""
        if self._prev is None:
            return []
        else:
            result = self._prev.prefix()
            result.append(cast(Terminal, self._last))
            return result

    def __repr__(self) -> str:
        return repr(self.prefix())
