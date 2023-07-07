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

from dataclasses import dataclass
from typing import Callable, Generic, List, Optional

from clamp.search.beam_search import beam_search
from clamp.search.beam_search_event_listener import LoggingEventListener
from clamp.search.datum import DatumSub, FullDatumSub
from clamp.search.model import Model, ModelResult
from clamp.search.problem_factory import ProblemFactory
from clamp.seq2seq.seq2seq_model import HS
from clamp.tokenization.clamp_tokenizer import ClampTokenizer


@dataclass
class BeamSearchSemanticParser(Model[DatumSub], Generic[DatumSub, FullDatumSub, HS]):
    problem_factory: ProblemFactory[DatumSub, HS]
    tokenizer: ClampTokenizer

    # Beam search-related parameters.
    # They could be moved to its own class so that we can also parametrize search methods.
    beam_size: int
    max_steps_fn: Optional[Callable[[DatumSub], Optional[int]]] = None
    keep_finished_nodes: bool = False  # save finished entries in beam separately

    async def predict(self, test_datum: DatumSub) -> List[ModelResult]:
        """Returns tuple of (hypothesis, whether hypothesis was artificially kept
        alive using force_decode, k-best list"""
        max_steps = self.max_steps_fn(test_datum) if self.max_steps_fn else None
        results = await beam_search(
            self.problem_factory.problem,
            self.problem_factory.initial(test_datum),
            self.beam_size,
            event_listener=LoggingEventListener(self.tokenizer, self.beam_size),
            max_steps=max_steps,
            keep_finished_nodes=self.keep_finished_nodes,
        )
        model_results = []
        for n in results:
            text = self.problem_factory.decoding_setup.finalize(n.tokens)  # type: ignore
            token_costs = [
                (self.tokenizer.id_to_utf8_token_map[t], cost)
                for t, cost in zip(n.tokens, n.token_costs)
            ]
            model_results.append(ModelResult(text, n.cost, token_costs))
        return model_results
