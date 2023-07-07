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

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Awaitable,
    Callable,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

from clamp.decoding.partial_parse import PartialParse
from clamp.seq2seq.seq2seq_model import HS

PSNSub = TypeVar("PSNSub", bound="PackedSearchNode")


# https://github.com/python/mypy/issues/5374
@dataclass(frozen=True, eq=True)  # type: ignore
class PackedSearchNode(ABC):
    """Contains all state for SearchNode in compact form.

    ConstrainedDecodingProblem contains a cache for `expand`, with PackedSearchNode as the key.
    In order to start beam search from some arbitrary state, clients can construct PackedSearchNode cheaply
    (i.e. without actually running a neural network, or creating a PartialParse object).
    Then, if the PackedSearchNode is in the cache already, then we can look up its expansion cheaply.
    If it's not in the cache, `ConstrainedDecodingProblem.unpacker` can turn it into a SearchNode.
    """

    # Output tokens generated so far.
    tokens: Tuple[int, ...]

    @abstractmethod
    def append(self: PSNSub, token: int) -> PSNSub:
        pass

    def extend(self: PSNSub, tokens: Sequence[int]) -> PSNSub:
        result = self
        for token in tokens:
            result = result.append(token)
        return result


# TODO: Make a new class for finished search nodes?
# It can omit partial_parse and hidden_state.
@dataclass
class FullSearchNode(Generic[HS]):
    packed: PackedSearchNode

    partial_parse: PartialParse
    hidden_state: Optional[HS] = dataclasses.field(repr=False)

    is_finished: bool = False
    cost: float = 0
    unnormalized_cost: float = 0
    token_costs: List[float] = dataclasses.field(default_factory=list)

    @property
    def tokens(self) -> Tuple[int, ...]:
        return self.packed.tokens

    # This function duplicates the above but its form is more convenient sometimes.
    def get_tokens(self) -> Tuple[int, ...]:
        return self.packed.tokens


SearchNode = Union[FullSearchNode[HS], PSNSub]
SearchNodeUnpacker = Callable[
    [PSNSub], Awaitable[Tuple[PartialParse, HS, Sequence[float]]]
]
