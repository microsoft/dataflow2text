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

from collections import defaultdict
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from clamp.earley.grammar import DottedRule, Nonterm, RuleResult
from clamp.earley.input import Position, Terminal

T = TypeVar("T")


@dataclass(frozen=True)
class Item(Generic[Terminal, RuleResult]):
    """
    An item in the Earley parse table, representing one or more subtrees
    that could yield a particular substring.
    Note that items must be immutable, since they will be hashed for duplicate detection.
    """

    dotted_rule: DottedRule[Terminal, RuleResult]
    start_col: "Column[Terminal, RuleResult]"

    # note that we don't need to store the end_col, which is the col that the item is in

    def scan_nonterm(
        self,
        nonterm: Nonterm,
        rule_result: RuleResult,
        begin: Position[Terminal],
        end: Position[Terminal],
    ) -> Iterable["Item[Terminal, RuleResult]"]:
        """
        Nondestructively advances the item's dotted rule by this symbol,
        getting 0 or more new items (which preserve the original start column).
        """
        for new_dotted_rule in self.dotted_rule.scan_nonterm(
            nonterm, rule_result, begin, end
        ):
            yield Item(dotted_rule=new_dotted_rule, start_col=self.start_col)

    def scan_terminal(
        self, terminal: Terminal
    ) -> Iterable["Item[Terminal, RuleResult]"]:
        """
        Nondestructively advances the item's dotted rule by this symbol,
        getting 0 or more new items (which preserve the original start column).
        """
        for new_dotted_rule in self.dotted_rule.scan_terminal(terminal):
            yield Item(dotted_rule=new_dotted_rule, start_col=self.start_col)

    def __repr__(self) -> str:
        return f'Item("{self.start_col.pos}", {self.dotted_rule})'


class Bp(Generic[Terminal]):
    """
    A backpointer.
    Contains enough metadata about how an Item was created to trace
    back through the chart and reconstruct complete parses.
    """

    def __len__(self) -> int:
        raise NotImplementedError


@dataclass(frozen=True)
class Attach(Bp, Generic[Terminal]):
    server: Item[Terminal, Any]
    customer: Item[Terminal, Any]
    col: "Column[Terminal, Any]"

    def __len__(self):
        return len(self.server.start_col.pos)


@dataclass(frozen=True)
class Scan(Bp, Generic[Terminal]):
    item: Item[Terminal, Any]
    terminal: Terminal
    col: "Column[Terminal, Any]"

    def __len__(self):
        return len(self.col.pos)


@dataclass(frozen=True)
class Predict(Bp, Generic[Terminal]):
    new_item: Item[Terminal, Any]

    def __len__(self):
        return len(self.new_item.start_col)


# Zero or more backpointers
Meta = List[Bp[Terminal]]


class MetaOps(Generic[Terminal]):
    """Zero or more backpointers"""

    @staticmethod
    def zero() -> "Meta[Terminal]":
        return []

    @staticmethod
    def plus(a: "Meta[Terminal]", b: "Meta[Terminal]") -> "Meta[Terminal]":
        return a + b

    @staticmethod
    def pure(bp: Bp[Terminal]) -> "Meta[Terminal]":
        return [bp]


class Agenda(Generic[T, Terminal]):
    """
    An agenda of items of type T that need to be processed.  Newly built items
    may be enqueued for processing by `push()`, and should eventually be
    dequeued by `pop()`.

    This implementation of an agenda also remembers which items have
    been pushed before, even if they have subsequently been popped.
    This is because already popped items must still be found by
    duplicate detection and as customers for attach.

    (In general, AI algorithms often maintain a "closed list" (or
    "chart") of items that have already been popped, in addition to
    the "open list" (or "agenda") of items that are still waiting to pop.)

    In Earley's algorithm, each end position has its own agenda -- a column
    in the parse chart.  (This contrasts with agenda-based parsing, which uses
    a single agenda for all items.)

    Standardly, each column's agenda is implemented as a FIFO queue
    with duplicate detection, and that is what is implemented here.
    However, other implementations are possible -- and could be useful
    when dealing with weights, backpointers, and optimizations.

    # TODO: add a type parameter for Semiring (instead of Weight)
    """

    def __init__(self, use_backpointers: bool) -> None:
        self.use_backpointers: bool = use_backpointers
        # list of all items that were *ever* pushed
        self._items: List[T] = []
        # index of first item that has not yet been popped
        self._next_index = 0
        # stores index of an item if it has been pushed before
        self.index: Dict[T, int] = {}
        # parallel with `self._items`.
        # We keep this as a parallel list instead of including the weight
        # inside the Item, because we want to be able to mutate the weight
        # (as new partial parses come in) without losing the identity of the
        # Item.
        self.metas: List[Meta[Terminal]] = []

    def __len__(self) -> int:
        """Returns number of items that are still waiting to be popped.
        Enables `len(my_agenda)`."""
        return len(self._items) - self._next_index

    def push(self, item: T, meta: Optional[Meta[Terminal]]) -> bool:
        """
        Enqueues the item, unless it was previously added.
        Returns whether it was added (or False if it was already enqueued).
        """
        i = self.index.get(item)
        if i is None:
            self._items.append(item)
            self.metas.append(meta)  # type: ignore
            self.index[item] = len(self._items) - 1
            return True
        else:
            if self.use_backpointers:
                assert meta is not None
                # TODO: r/MetaOps/semiring/ ?
                self.metas[i] = MetaOps.plus(self.metas[i], meta)
            return False

    def get_meta(self, item: T) -> Meta[Terminal]:
        return self.metas[self.index[item]]

    def pop(self) -> T:
        """
        Returns one of the items that was waiting to be popped (dequeued).
        Raises IndexError if there are no items waiting.
        """
        if len(self) == 0:
            raise IndexError
        item = self._items[self._next_index]
        self._next_index += 1
        return item

    def all_items(self) -> Iterable[Tuple[T, Meta[Terminal]]]:
        """
        Collection of all items that have ever been pushed, even if
        they've already been popped.
        """
        return zip(self._items, self.metas)

    @property
    def remaining(self):
        return self._items[self._next_index :]

    @property
    def popped(self):
        return self._items[: self._next_index]

    def __repr__(self):
        """Provide a representation of the instance for printing."""
        return f"{self.__class__.__name__}({self.popped}; {self.remaining})"


class Column(Agenda[Item[Terminal, RuleResult], Terminal]):
    """
    A column in Earley's algorithm, storing all partial items that end at a
    particular position (input state).
    """

    def __init__(self, pos: Position[Terminal], use_backpointers: bool):
        super().__init__(use_backpointers=use_backpointers)
        self.pos: Position[Terminal] = pos  # a representation of the input state
        # speedup: which nonterminals in this column have we predicted already?
        self.predicted: Set[Nonterm] = set()
        self.customers: Dict[Nonterm, List[Item[Terminal, RuleResult]]] = defaultdict(
            list
        )
        # speedup: who's looking for each nonterminal?
        self.servers: Dict[
            Nonterm,
            List[
                Tuple[
                    Item[Terminal, RuleResult],
                    "Column[Terminal, RuleResult]",
                    RuleResult,
                ]
            ],
        ] = defaultdict(list)
        # a corresponding "row" of complete constituents that start at self.pos,
        # to complement the "column" of complete and incomplete constituents
        # that end at self.pos.  We need this to deal with cases where
        # the right item came to this column to serve a "customer" (left item)
        # that hadn't been built yet; this "order violation" can happen due
        # to 0-width constituents or cyclic FSA input.  So we store the right item
        # in this row so that the customer can look for it when it's built.
        # Really we should turn it into a "reversed item" that stores
        # end_pos instead of start_pos, but for simplicity and speed, we
        # just pair it with the end_pos in the row.  An alternative would
        # be to have all items store their start_pos *and* end_pos.

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.pos})"

    def unpop_using_pred(
        self, pred: Callable[[Item[Terminal, RuleResult]], bool]
    ) -> None:
        """Rearrange items in the Column so that it is not popped iff `pred`.

        After this function, `pred` entirely determines whether an item is popped or not.
        Whether it was popped before is not taken into account.
        """
        false_items: List[Item[Terminal, RuleResult]] = []
        false_metas: List[Meta[Terminal]] = []
        true_items: List[Item[Terminal, RuleResult]] = []
        true_metas: List[Meta[Terminal]] = []

        for item, meta in self.all_items():
            if pred(item):
                true_items.append(item)
                true_metas.append(meta)
            else:
                false_items.append(item)
                false_metas.append(meta)
        self._items = false_items + true_items
        self._next_index = len(false_items)
        self.index = dict((x, i) for i, x in enumerate(self._items))
        self.metas = false_metas + true_metas
