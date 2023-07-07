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

import itertools

# see https://github.com/pytorch/pytorch/issues/47027
from collections import abc as abc  # pylint: disable=C0414
from collections.abc import Sized
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Hashable,
    Iterable,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import numpy as np
from typing_extensions import Protocol

from clamp.earley.fsa import CompiledDFA
from clamp.earley.fsa_builders import NFAFrag, compile_dfa
from clamp.earley.input import Position, Terminal
from clamp.util.unit import UNIT

# Elements of a rule RHS.
Symbol = Union["Nonterm", Terminal]

# DottedRules can return a RuleResult when final.
RuleResult = TypeVar("RuleResult", bound=Hashable)


@dataclass(frozen=True)
class Nonterm:
    """Grammar nonterminal"""

    name: str

    def __repr__(self):
        return f"Nonterm({self.name})"

    def __str__(self):
        return f"\N{mathematical left angle bracket}{self.name}\N{mathematical right angle bracket}"

    # TODO: consider interning the string or using an integerizer, as a minor speedup
    # NOTE: nonterminals are sometimes structured (attributes, slashed gaps, etc.), so
    #       really we should make an abstract base class, and parameterize grammars
    #       on the particular Nonterm type (using a bounded type variable so it must
    #       be a subclass of that base class).


class DottedRule(Generic[Terminal, RuleResult], Protocol):
    @property
    def lhs(self) -> Nonterm:
        """The nonterminal for this rule."""

    @property
    def alias(self) -> Optional[str]:
        """A name for this specific DottedRule.

        TODO: Change contract so the alias is only accessed on completed DottedRules."""

    def next_symbols(self) -> Iterable[Symbol[Terminal]]:
        """Terminals or nonterminals that we are looking for next."""

    def is_final(self) -> Optional[RuleResult]:
        """Whether the "dot" is past the last symbol (thus we have produced a complete `lhs`)"""

    def scan_nonterm(
        self,
        nonterm: Nonterm,
        result: RuleResult,
        begin: Position[Terminal],
        end: Position[Terminal],
    ) -> "Iterable[DottedRule[Terminal, RuleResult]]":
        """Advance by the specified finished nonterminal, which has produced the given result."""

    def scan_terminal(
        self, terminal: Terminal
    ) -> "Iterable[DottedRule[Terminal, RuleResult]]":
        """Advance by the specified terminal"""


# TODO: Figure out how this class can satisfy
# DottedRule[Terminal, T] where T is a supertype of Unit (e.g. Union of Unit with something else)
@dataclass(frozen=True)
class DFADottedRule:
    lhs: Nonterm
    # TODO: Remove all parts of the DFA that are not reachable from state_id
    dfa: CompiledDFA[Nonterm]
    state_id: int
    # TODO: Put the alias inside the DFA so that we can have a different alias
    # depending on which state in the DFA was reached
    alias: Optional[str] = None

    def next_symbols(self) -> Iterable[Symbol[np.uint8]]:
        return self.dfa.next_labels(self.state_id)

    def is_final(self) -> Optional[Any]:
        return UNIT if self.dfa.is_final_dfa(self.state_id) else None

    def scan_nonterm(
        self,
        nonterm: Nonterm,
        result: Any,
        begin: Position[np.uint8],
        end: Position[np.uint8],
    ) -> "Iterable[DFADottedRule]":
        # TODO: Specialize `transition_dfa` for nonterminal
        del result, begin, end
        next_state_id = self.dfa.transition_dfa(self.state_id, nonterm)
        return (
            ()
            if next_state_id is None
            else (DFADottedRule(self.lhs, self.dfa, next_state_id),)
        )

    def scan_terminal(self, terminal: np.uint8) -> "Iterable[DFADottedRule]":
        # TODO: Specialize `transition_dfa` for terminal
        next_state_id = self.dfa.transition_dfa(self.state_id, terminal)
        return (
            ()
            if next_state_id is None
            else (DFADottedRule(self.lhs, self.dfa, next_state_id),)
        )

    @staticmethod
    def from_rule(
        lhs: Nonterm, rhs: NFAFrag[Nonterm], alias: Optional[str] = None
    ) -> "DFADottedRule":
        dfa = compile_dfa(rhs)
        return DFADottedRule(lhs, dfa, dfa.start_id, alias)

    def __repr__(self) -> str:
        """Produces a compact representation of the dotted rule.

        LHS → (symbols which can cause transition to this state) ● (subsequent symbols) (checkmark if is_final)
        """
        prev_symbols_strs, next_symbols_strs = (
            [
                str(s) if isinstance(s, Nonterm) else repr(bytes([s]))[2:-1]
                for s in sorted(symbols, key=lambda s: not isinstance(s, Nonterm))
            ]
            for symbols in (self.dfa.prev_labels(self.state_id), self.next_symbols())
        )
        if self.is_final():
            next_symbols_strs.append("\N{white heavy check mark}")

        prev_symbols_str = " | ".join(prev_symbols_strs) + (
            " " if prev_symbols_strs else ""
        )
        next_symbols_str = " | ".join(next_symbols_strs)
        return f"{self.lhs} → {prev_symbols_str}\N{black circle} {next_symbols_str}"


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class LinearDottedRule(Generic[Terminal]):
    """
    The residue of a grammar rule after part of it has been matched.
    A complete grammar rule (with the dot at the start) is a special case.
    A basic dotted rule, whose RHS consists of a sequence of remaining symbols
    that we need to match in order to complete the rule.
    We don't bother to store the "pre-dot" symbols that have already been
    matched.  That leads to a speedup in Earley's algorithm through more
    aggressive consolidation of duplicates.
    """

    # the left-hand side of the rule.  The other methods match against the right-hand side.
    lhs: Nonterm
    # TODO: we don't need this for recognition, only parsing. This prevents us from
    # recombining Items that share a common unconsumed suffix.
    # Could even recognize first, and then rerun with backpointers?
    # The full original rhs of the rule
    full_rhs: Tuple[Symbol[Terminal], ...]
    # TODO: turn this into a state in a reverse trie of rules, for hashing efficiency
    # The unconsumed portion of the rhs
    rhs: Tuple[Symbol[Terminal], ...]
    # a distinct identifier for this rule
    alias: Optional[str] = None

    def next_symbols(self) -> Iterable[Symbol[Terminal]]:
        return self.rhs[:1]

    def is_final(self) -> Optional[Any]:
        return UNIT if not self.rhs else None

    def scan_nonterm(
        self,
        nonterm: Nonterm,
        result: Any,
        begin: Position[Terminal],
        end: Position[Terminal],
    ) -> Iterable["LinearDottedRule[Terminal]"]:
        """
        Returns new LinearDottedRules where the nonterm has been consumed if it matches the RHS.
        If the nonterm is the first element of `rhs`, then it is removed from `rhs`.
        """
        del result, begin, end
        if not self.rhs:
            return ()
        first_rhs = self.rhs[0]
        if first_rhs == nonterm:
            # Exact match case: drop first element of RHS
            return (
                LinearDottedRule[Terminal](
                    lhs=self.lhs,
                    full_rhs=self.full_rhs,
                    rhs=self.rhs[1:],
                    alias=self.alias,
                ),
            )

        return ()

    def scan_terminal(
        self, terminal: Terminal
    ) -> Iterable["LinearDottedRule[Terminal]"]:
        """
        Returns new LinearDottedRules where the symbol has been consumed if it matches the RHS.

        If the symbol exactly matches the first element of `rhs`, then it is removed from `rhs`.
        If the symbol is a prefix of the first element of `rhs`, then the prefix is removed.

        Example `rhs`: ("meeting", "at", Nonterminal(time))
        If symbol is "meeting", then the new `rhs` is ("at", Nonterminal(time)).
        If symbol is "meet", then the new `rhs` is ("ing", "at", Nonterminal(time)).
        """

        if not self.rhs:
            return ()
        first_rhs = self.rhs[0]
        if first_rhs == terminal:
            # Exact match case: drop first element of RHS
            return (
                LinearDottedRule[Terminal](
                    lhs=self.lhs,
                    full_rhs=self.full_rhs,
                    rhs=self.rhs[1:],
                    alias=self.alias,
                ),
            )
        if isinstance(first_rhs, Nonterm):
            # If either is Nonterm, then a partial match is impossible, so give up here.
            return ()

        if (
            isinstance(first_rhs, abc.Sequence)
            and isinstance(terminal, Sized)
            and first_rhs[: len(terminal)] == terminal
        ):
            # Partial match succeeded.
            return (
                LinearDottedRule[Terminal](
                    lhs=self.lhs,
                    full_rhs=self.full_rhs,
                    rhs=(first_rhs[len(terminal) :],) + self.rhs[1:],  # type: ignore
                    alias=self.alias,
                ),
            )
        return ()

    def __repr__(self) -> str:
        """Produces a compact representation of the dotted rule.

        LHS → (already matched RHS) ● (remaining RHS)
        """
        consumed_len = len(self.full_rhs) - len(self.rhs)
        dotted_rhs = itertools.chain(
            (str(x) for x in self.full_rhs[:consumed_len]),
            ["\N{black circle}"],
            (str(x) for x in self.rhs),
        )
        return f"{self.lhs} → {' '.join(dotted_rhs)}"

    @staticmethod
    def from_rule(
        lhs: Nonterm, rhs: Tuple[Symbol[Terminal], ...], alias: Optional[str] = None
    ) -> "LinearDottedRule[Terminal]":
        return LinearDottedRule(lhs, rhs, rhs, alias=alias)


class Grammar(Generic[Terminal, RuleResult], Protocol):
    """A context-free grammar.

    The set of rules can be dynamically generated based on the nonterminal."""

    @property
    def root(self) -> Nonterm:
        """The root nonterminal of the grammar."""

    def get_expansions(
        self, nonterm: Nonterm
    ) -> Iterable[DottedRule[Terminal, RuleResult]]:
        pass


@dataclass(frozen=True)
class InitialSpaceGrammar(Generic[RuleResult]):
    """A wrapper around a grammar that adds an initial space."""

    underlying: Grammar[np.uint8, RuleResult]
    root: ClassVar[Nonterm] = Nonterm("<space_before_root>")

    def get_expansions(
        self, nonterm: Nonterm
    ) -> Iterable[DottedRule[np.uint8, RuleResult]]:
        if nonterm == self.root:
            return (
                LinearDottedRule.from_rule(
                    self.root, (np.uint8(ord(b" ")), self.underlying.root)
                ),
            )
        else:
            return self.underlying.get_expansions(nonterm)


@dataclass(frozen=True)
class FixedGrammar(Generic[Terminal, RuleResult]):
    """A context-free grammar where the set of rules is fixed ahead of time."""

    root: Nonterm
    expansions: Dict[Nonterm, Set[DottedRule[Terminal, RuleResult]]]

    def get_expansions(
        self, nonterm: Nonterm
    ) -> Iterable[DottedRule[Terminal, RuleResult]]:
        return self.expansions[nonterm]


@dataclass(frozen=True)
class DFAGrammar:
    """A context-free grammar where all expansions are single DFAs.

    DFAGrammar satisfies Grammar[np.uint8, Any]."""

    root: Nonterm
    expansions: Dict[Nonterm, DFADottedRule]

    def get_expansions(self, nonterm: Nonterm) -> Iterable[DottedRule[np.uint8, Any]]:
        if nonterm in self.expansions:
            return (self.expansions[nonterm],)
        else:
            return ()
