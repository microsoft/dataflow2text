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

import abc
from abc import ABC
from typing import Generic, List, Optional, Sequence, Tuple, TypeVar

import torch

from clamp.tokenization.clamp_tokenizer import ClampTokenizer

HS = TypeVar("HS")


class AutoregressiveModel(Generic[HS], ABC):
    """Base class for language models and sequence-to-sequence models."""

    @property
    @abc.abstractmethod
    def vocab_size(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def tokenizer(self) -> ClampTokenizer:
        pass

    @abc.abstractmethod
    async def extend(
        self,
        tokens: Sequence[int],
        hidden_state: HS,
        drop_next_hidden_state: bool = False,
    ) -> Tuple[torch.Tensor, HS]:
        pass

    @abc.abstractmethod
    async def next_logprobs(self, hidden_state: HS) -> torch.Tensor:
        """Returns the distribution over the next token given the tokens in the hidden state."""

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        pass


class IncrementalLanguageModel(AutoregressiveModel[HS], ABC):
    @abc.abstractmethod
    async def execute(
        self,
        tokens: Sequence[int],
        hidden_state: Optional[HS] = None,
        drop_next_hidden_state: bool = False,
    ) -> Tuple[torch.Tensor, Optional[HS]]:
        """Run the language model on an input and a hidden state.

        tokens: List of token IDs, between 0 and `vocab_size - 1`.
        hidden_state: Returned from a previous call to this function.
        free_prev_hidden_state: Tell the backend that `hidden_state` is no longer needed after this call.
        drop_next_hidden_state: Tell the backend to not produce a return hidden state.

        Returns:
            a float32 tensor of size [seq len, vocab size] containing log probabilities.
            optionally, a hidden state that can be used in a future call to this function.
        """

    async def extend(
        self,
        tokens: Sequence[int],
        hidden_state: HS,
        drop_next_hidden_state: bool = False,
    ) -> Tuple[torch.Tensor, Optional[HS]]:
        return await self.execute(tokens, hidden_state, drop_next_hidden_state)

    async def logprob_of_completion(
        self, prefix_tokens: Sequence[int], completion_tokens: Sequence[int]
    ) -> Tuple[float, Sequence[float]]:
        """Return the log probability of `completion_tokens` following `prefix_tokens`."""
        logprobs, _ = await self.execute(
            tuple(prefix_tokens) + tuple(completion_tokens), drop_next_hidden_state=True
        )
        total_num_tokens = len(prefix_tokens) + len(completion_tokens)
        assert logprobs.shape[0] == len(prefix_tokens) + len(completion_tokens)

        completion_logprobs = logprobs[
            range(len(prefix_tokens) - 1, total_num_tokens - 1), completion_tokens
        ]
        score = completion_logprobs.sum().item()
        return score, completion_logprobs.tolist()


class Seq2SeqModel(AutoregressiveModel[HS], ABC):
    @property
    @abc.abstractmethod
    def decoder_bos_ids(self) -> List[int]:
        """Return the IDs for tokens that should appear at the start of the decoder sequence."""

    @property
    @abc.abstractmethod
    def decoder_eos_id(self) -> int:
        """Return the ID for the token which signals that decoding is finished."""

    @abc.abstractmethod
    def encode_for_encoder(self, s: str) -> List[int]:
        """Convert string into a sequence of token IDs for input into the encoder."""

    @abc.abstractmethod
    def encode_prefix_for_decoder(
        self, s: str, include_bos_ids: bool = True
    ) -> List[int]:
        """Convert string into a sequence of token IDs for input into the decoder."""

    @abc.abstractmethod
    def decode_output(self, ids: Sequence[int]) -> str:
        """Convert token IDs from the decoder into a properly formatted string.

        The list of IDs should not contain the EOS token nor `decoder_bos_ids`."""

    @abc.abstractmethod
    async def initial(
        self,
        encoder_tokens: Sequence[int],
        decoder_tokens: Sequence[int],
        drop_next_hidden_state: bool = False,
    ) -> Tuple[torch.Tensor, Optional[HS]]:
        """Run the language model on tokens for the encoder and the decoder.

        encoder_tokens: List of token IDs, between 0 and `vocab_size - 1`.
        decoder_tokens: List of token IDs, between 0 and `vocab_size - 1`.
        drop_next_hidden_state: Tell the backend to not produce a return hidden state.

        Returns:
            a float32 tensor of size [decoder_tokens len, vocab size] containing log probabilities.
            optionally, a hidden state that can be used in a future call to this function.
        """
