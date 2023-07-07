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

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterator, List, MutableMapping, Optional, Tuple

import torch

from clamp.search.search_node import (
    FullSearchNode,
    PackedSearchNode,
    PSNSub,
    SearchNode,
    SearchNodeUnpacker,
)
from clamp.seq2seq.seq2seq_model import HS, AutoregressiveModel


class Problem(Generic[HS, PSNSub], ABC):
    """Defines the formal search problem used for decoding.

    Instances specify how to create successor search nodes given an existing
    one. A search algorithm, such as beam search, uses this interface to find
    suitable finished search nodes from an initial one.
    """

    @abstractmethod
    async def expand(
        self, maybe_packed_node: SearchNode[HS, PSNSub]
    ) -> List[FullSearchNode[HS]]:
        pass


@dataclass
class ConstrainedDecodingProblem(Problem[HS, PSNSub]):
    model: AutoregressiveModel[HS]
    # This function knows how to expand PackedSearchNodes.
    unpacker: SearchNodeUnpacker[PSNSub, HS]

    # A 1D Long tensor containing the IDs of tokens indicating the end.
    eos: torch.Tensor
    length_normalization: float
    # Only use the top_k most likely next tokens in `expand`.
    # This can be set to the beam size.
    top_k: Optional[int] = None

    # TODO: PackedSearchNode may not always be Hashable.
    cache: Optional[MutableMapping[PackedSearchNode, List[FullSearchNode[HS]]]] = None

    async def expand(
        self, maybe_packed_node: SearchNode[HS, PSNSub]
    ) -> List[FullSearchNode[HS]]:
        if self.cache is not None:
            if isinstance(maybe_packed_node, FullSearchNode):
                packed_node = maybe_packed_node.packed
            else:
                packed_node = maybe_packed_node
            existing = self.cache.get(packed_node)
            if existing is not None:
                logging.debug("\N{DIRECT HIT} %s", packed_node)
                return existing
            else:
                logging.debug("\N{HOURGLASS WITH FLOWING SAND} %s", packed_node)

        if isinstance(maybe_packed_node, FullSearchNode):
            assert not maybe_packed_node.is_finished
            assert maybe_packed_node.hidden_state
            logprobs, new_hidden_state = await self.model.extend(
                maybe_packed_node.tokens[-1:], maybe_packed_node.hidden_state
            )

            next_logprobs = logprobs[0]  # Remove the sequence dimension
            unnormalized_cost = maybe_packed_node.unnormalized_cost
            packed_node = maybe_packed_node.packed
            partial_parse = maybe_packed_node.partial_parse
            token_logprobs = maybe_packed_node.token_costs
            # new_hidden_state already set
        else:
            (
                partial_parse,
                hidden_state,
                existing_logprobs,
            ) = await self.unpacker(  # type: ignore
                maybe_packed_node
            )

            next_logprobs = await self.model.next_logprobs(hidden_state)
            unnormalized_cost = -sum(existing_logprobs)
            packed_node = maybe_packed_node
            # partial_parse already set
            new_hidden_state = hidden_state
            token_logprobs = []

        del maybe_packed_node

        allowed_next, can_end = partial_parse.allowed_next(
            argsort_without_negative_inf(next_logprobs, descending=True), self.top_k
        )

        result: List[FullSearchNode[HS]] = []
        if can_end:
            eos_logprob = torch.logsumexp(next_logprobs[self.eos], dim=0)

            new_unnorm_cost = unnormalized_cost - eos_logprob.item()
            result.append(
                FullSearchNode(
                    packed_node,
                    partial_parse,
                    hidden_state=None,
                    is_finished=True,
                    cost=gnmt_length_normalization(
                        self.length_normalization,
                        new_unnorm_cost,
                        len(packed_node.tokens) + 1,
                    ),
                    unnormalized_cost=new_unnorm_cost,
                    token_costs=token_logprobs + [-eos_logprob.item()],
                )
            )
        token_and_logprob_iter: Iterator[Tuple[int, torch.Tensor]]
        if allowed_next is None:
            indices = torch.arange(next_logprobs.shape[0])
            eligible_logprobs = next_logprobs
        else:
            indices = allowed_next
            eligible_logprobs = next_logprobs[allowed_next]

        if self.top_k is None:
            token_and_logprob_iter = (
                # .item() converts 0D tensor to a Python number
                (token_id_tensor.item(), logprob)  # type: ignore
                for token_id_tensor, logprob in zip(indices, eligible_logprobs)
            )
        else:
            topk_eligible_logprobs = torch.topk(
                eligible_logprobs,
                k=min(self.top_k, eligible_logprobs.shape[0]),
                sorted=False,
            )
            token_and_logprob_iter = (
                (token_id_tensor.item(), logprob)  # type: ignore
                for token_id_tensor, logprob in zip(
                    indices[topk_eligible_logprobs.indices],
                    topk_eligible_logprobs.values,
                )
            )

        for token, logprob in token_and_logprob_iter:
            if token in self.eos:
                continue
            new_unnorm_cost = unnormalized_cost - logprob.item()
            result.append(
                FullSearchNode(
                    packed_node.append(token),
                    partial_parse.append(token),
                    new_hidden_state,
                    cost=gnmt_length_normalization(
                        self.length_normalization,
                        new_unnorm_cost,
                        len(packed_node.tokens) + 1,
                    ),
                    unnormalized_cost=new_unnorm_cost,
                    token_costs=token_logprobs + [-logprob.item()],
                )
            )

        if self.cache is not None:
            self.cache[packed_node] = result
        return result


def gnmt_length_normalization(alpha: float, unnormalized: float, length: int) -> float:
    """
    Eq 14 from https://arxiv.org/abs/1609.08144, but missing the coverage term.
    TODO switch to something similar since this is probably overtuned for MT.
    :param unnormalized: log prob
    :param length: |Y|, or length of sequence.
    :return:
    """
    lp = (5 + length) ** alpha / (5 + 1) ** alpha
    return unnormalized / lp


def argsort_without_negative_inf(
    t: torch.Tensor, descending: bool = True
) -> torch.Tensor:
    """Perform argsort on `t`, only on values of `t` which are not -inf.

    This is useful as IncrementalOpenAIGPT3 returns logprob tensors where most entries are -inf.
    Only tested on 1D tensors.

    Example usage:
    >>> argsort_without_negative_inf(torch.tensor([1, 3, float("-inf"), 2]))
    Tensor([1, 3, 0])
    """

    mask = t != -float("inf")
    sorted_t = torch.argsort(t, descending=descending)
    return sorted_t[mask[sorted_t]]
