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
from typing import Callable, Generic, List, Sequence, Tuple

import torch

from clamp.decoding.partial_parse import PartialParse
from clamp.search.datum import DatumSub
from clamp.search.search_node import PackedSearchNode
from clamp.seq2seq.seq2seq_model import HS, Seq2SeqModel

PartialParseBuilder = Callable[[DatumSub], PartialParse]


@dataclass(frozen=True, eq=True)
class DatumPackedSearchNode(Generic[DatumSub], PackedSearchNode):
    test_datum: DatumSub

    def append(self, token: int) -> "DatumPackedSearchNode":
        return DatumPackedSearchNode(
            tokens=self.tokens + (token,), test_datum=self.test_datum
        )

    def extend(self, tokens: Sequence[int]) -> "DatumPackedSearchNode":
        if not tokens:
            return self

        return DatumPackedSearchNode(
            tokens=self.tokens + tuple(tokens), test_datum=self.test_datum
        )


@dataclass  # type: ignore
class DecodingSetup(Generic[DatumSub, HS], ABC):
    """Specifies how to start/setup the decoding for a datum, and when to finish.

    This interface encapsulates the knowledge about how to use a model.
    For example, using a fine-tuned seq2seq model requires processing the utterance in the encoder;
    using an autoregressive language model with few-shot in-context examples requires
    finding and assembling the training examples into a prompt and encoding it with the model.

    Instances are used in BeamSearchSemanticParser.
    """

    partial_parse_builder: PartialParseBuilder

    @abstractmethod
    async def unpack_node(
        self, packed_node: DatumPackedSearchNode[DatumSub]
    ) -> Tuple[PartialParse, HS, Sequence[float]]:
        """Prepares a PackedSearchNode for decoding.

        The PackedSearchNode is usually empty, but it may contain some tokens
        which is useful for interactive use cases (e.g. an auto-complete server)."""

    @property
    @abstractmethod
    def eos_tokens(self) -> torch.Tensor:
        """The set of tokens which denotes the end of the search."""

    @abstractmethod
    def finalize(self, tokens: List[int]) -> str:
        """Converts the result of decoding into a string.

        It's not just tokenizer.decode because further processing may be needed."""


@dataclass
class Seq2SeqDecodingSetup(DecodingSetup[DatumSub, HS]):
    seq2seq_model: Seq2SeqModel[HS]
    _eos_tokens: torch.Tensor = dataclasses.field(init=False)

    def __post_init__(self):
        # pylint: disable=not-callable
        self._eos_tokens = torch.tensor(
            [self.seq2seq_model.decoder_eos_id], dtype=torch.long
        )

    @property
    def eos_tokens(self) -> torch.Tensor:
        return self._eos_tokens

    async def unpack_node(
        self, packed_node: DatumPackedSearchNode
    ) -> Tuple[PartialParse, HS, Sequence[float]]:
        decoder_tokens = self.seq2seq_model.decoder_bos_ids + list(packed_node.tokens)
        logprobs, hidden_state = await self.seq2seq_model.initial(
            self.seq2seq_model.encode_for_encoder(packed_node.test_datum.natural),
            decoder_tokens,
        )
        assert hidden_state is not None
        # https://github.com/python/mypy/issues/708
        initial_partial_parse = self.partial_parse_builder(packed_node.test_datum)  # type: ignore
        for token in packed_node.tokens:
            initial_partial_parse = initial_partial_parse.append(token)

        return (
            initial_partial_parse,
            hidden_state,
            logprobs[
                list(
                    range(len(self.seq2seq_model.decoder_bos_ids), len(decoder_tokens))
                ),
                list(packed_node.tokens),
            ].tolist(),
        )

    def finalize(self, tokens: List[int]) -> str:
        return self.seq2seq_model.decode_output(tokens)
