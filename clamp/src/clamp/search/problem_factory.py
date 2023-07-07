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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, MutableMapping, Optional

from cached_property import cached_property

from clamp.search.datum import DatumSub
from clamp.search.problem import ConstrainedDecodingProblem, Problem
from clamp.search.search_node import FullSearchNode, PackedSearchNode
from clamp.search.seq2seq_decoding_step import DatumPackedSearchNode, DecodingSetup
from clamp.seq2seq.seq2seq_model import HS, AutoregressiveModel


@dataclass  # type: ignore
class ProblemFactory(Generic[DatumSub, HS], ABC):
    """Sets up a Problem and the initial SearchNode for a given Datum.

    Different search strategies are encapsulated as different Problems
    (e.g. decoding token by token, or decoding many tokens at once)
    and this interface specifies which one to use.
    """

    # TODO: Merge this class with the Problem class
    # (unless we need to make `problem` a function of the datum).
    decoding_setup: DecodingSetup[DatumSub, HS]

    # pylint: disable=no-self-use
    def initial(self, datum: DatumSub) -> DatumPackedSearchNode:
        return DatumPackedSearchNode(tokens=(), test_datum=datum)

    @property
    @abstractmethod
    def problem(self) -> Problem[HS, DatumPackedSearchNode]:
        pass


@dataclass
class ConstrainedDecodingProblemFactory(ProblemFactory[DatumSub, HS]):
    autoregressive_model: AutoregressiveModel[HS]
    length_normalization: float = 0.7
    top_k: Optional[int] = None
    cache: Optional[MutableMapping[PackedSearchNode, List[FullSearchNode[HS]]]] = None

    @cached_property
    def problem(
        self,
    ) -> ConstrainedDecodingProblem[
        HS, DatumPackedSearchNode
    ]:  # pylint: disable=invalid-overridden-method
        return ConstrainedDecodingProblem(
            self.autoregressive_model,
            self.decoding_setup.unpack_node,
            self.decoding_setup.eos_tokens,
            self.length_normalization,
            self.top_k,
            self.cache,
        )
