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

"""Constrained decoding for Earley grammars where terminals are np.uint8.

UInt8EarleyPartialParse is similar to EarleyPartialParse, except that it only
works for grammars where all terminals are np.uint8.
It also currently lacks support for input utterance copying constraints.

TODO: We can generalize UInt8EarleyPartialParse to "Atomic"EarleyPartialParse by
replacing np.uint8 with a type parameter.
"""

import dataclasses
import itertools
from dataclasses import dataclass
from typing import Mapping  # pylint: disable=unused-import
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
)

import numpy as np
import torch
from cached_property import cached_property

from clamp.decoding.partial_parse import PartialParse
from clamp.earley.earley import EarleyChart
from clamp.earley.grammar import Grammar
from clamp.earley.input import Position, SigmaStarTriePosition
from clamp.tokenization.clamp_tokenizer import ClampTokenizer

T = TypeVar("T")


def get_only(items: Iterable[T]) -> T:
    """Returns the single value in `items`.

    This function raises an exception if items contains 0 or 2+ items.
    """
    [item] = items
    return item


@dataclass
class UInt8GrammarNode:
    chart: EarleyChart[np.uint8, Any]
    lazy_pos: Callable[[], Position[np.uint8]]

    @cached_property
    def pos(self) -> Position[np.uint8]:
        return self.lazy_pos()

    @cached_property
    def children(self) -> "Mapping[np.uint8, UInt8GrammarNode]":
        # TODO: Consider using a list instead.
        return {
            terminal: UInt8GrammarNode(
                self.chart,
                lambda terminal=terminal, items=items: get_only(  # type: ignore
                    self.chart.advance_with_terminal(self.pos, terminal, items)
                ),
            )
            for terminal, items in self.chart.advance_only_nonterminals(
                self.pos, unpop_terminals=False
            ).items()
        }

    def advance(self, seq: Sequence[np.uint8]) -> "Optional[UInt8GrammarNode]":
        result = self
        for byte in seq:
            result = result.children.get(byte)
            if result is None:
                break
        return result


@dataclass
class UInt8GrammarTokenizerInfo:
    grammar: Grammar[np.uint8, Any]
    tokens: Sequence[Sequence[np.uint8]]
    # Used for special tokens like `<|endoftext|>` which we should never allow.
    banned_token_ids: Set[int]

    @cached_property
    def vocab_size(self) -> int:
        return len(self.tokens)

    @staticmethod
    def from_clamp_tokenizer(
        grammar: Grammar[np.uint8, Any], tokenizer: ClampTokenizer
    ) -> "UInt8GrammarTokenizerInfo":
        (
            encoded_tokens,
            banned_token_ids,
        ) = UInt8GrammarTokenizerInfo.prepare_tokens_from_clamp_tokenizer(tokenizer)
        return UInt8GrammarTokenizerInfo(grammar, encoded_tokens, banned_token_ids)

    @staticmethod
    def prepare_tokens_from_clamp_tokenizer(
        tokenizer: ClampTokenizer,
    ) -> Tuple[Sequence[Sequence[np.uint8]], Set[int]]:
        return (
            [
                np.frombuffer(tokenizer.id_to_utf8_token_map[i], dtype=np.uint8)
                for i in range(len(tokenizer.id_to_utf8_token_map))
            ],
            {tokenizer.eos_token_id, tokenizer.pad_token_id, tokenizer.unk_token_id},
        )


@dataclass
class UInt8EarleyPartialParse(PartialParse):
    grammar_node: UInt8GrammarNode
    info: UInt8GrammarTokenizerInfo
    start_pos: Position[np.uint8]
    _next_node_cache: Dict[int, Optional[UInt8GrammarNode]] = dataclasses.field(
        default_factory=dict
    )

    def allowed_next(
        self, ordered_ids: Optional[torch.Tensor] = None, top_k: Optional[int] = None
    ) -> Tuple[Optional[torch.Tensor], bool]:
        # TODO: Use optimizations already in EarleyPartialParse, and others identified but not implemented:
        # - Only check the first N tokens from ordered_ids with `token_id_is_valid`;
        #   for the rest, intersect grammar_node with the vocab trie
        assert ordered_ids is not None
        ordered_ids_list = ordered_ids.tolist()
        all_tokens = self.info.tokens
        vocab_size = self.info.vocab_size
        node = self.grammar_node

        def token_id_is_valid(i: int) -> bool:
            if not 0 <= i < vocab_size or i in self.info.banned_token_ids:
                return False
            next_node = node.advance(all_tokens[i])
            self._next_node_cache[i] = next_node
            return next_node is not None

        def produce_valid_tokens() -> Iterator[int]:
            for i in ordered_ids_list:
                if token_id_is_valid(i):
                    yield i

        # TODO: Add special case where grammar_node.children has no elements
        # (i.e. tokens_list will be empty)
        tokens_list = list(itertools.islice(produce_valid_tokens(), top_k))
        can_end = self.grammar_node.chart.was_found(
            self.grammar_node.chart.grammar.root, self.start_pos, self.grammar_node.pos
        )
        # pylint: disable=not-callable
        return torch.tensor(tokens_list, dtype=torch.long), can_end

    def append(self, token: int) -> "UInt8EarleyPartialParse":
        """Return a new PartialParse created by appending this token."""
        if token in self._next_node_cache:
            node_for_result = self._next_node_cache[token]
        else:
            if not 0 <= token < self.info.vocab_size:
                raise ValueError("token was not in the vocabulary")
            node_for_result = self.grammar_node.advance(self.info.tokens[token])

        if node_for_result is None:
            raise ValueError("invalid token to continue with")

        return UInt8EarleyPartialParse(node_for_result, self.info, self.start_pos)

    @staticmethod
    def initial(info: UInt8GrammarTokenizerInfo) -> "UInt8EarleyPartialParse":
        chart = EarleyChart(info.grammar, use_backpointers=False)
        start_pos = SigmaStarTriePosition[np.uint8]()
        chart.seek(info.grammar.root, start_pos)
        grammar_node = UInt8GrammarNode(chart, lambda: start_pos)
        return UInt8EarleyPartialParse(grammar_node, info, start_pos)
