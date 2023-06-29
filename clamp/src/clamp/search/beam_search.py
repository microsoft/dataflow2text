import asyncio
import gc
import itertools
from typing import Dict, List, Optional, Set, Tuple

import torch

from clamp.search.beam_search_event_listener import (
    BeamSearchEventListener,
    FullSearchNode,
    HashableNodeWrapper,
)
from clamp.search.problem import Problem, PSNSub, SearchNode
from clamp.seq2seq.seq2seq_model import HS

MAX_STEPS = 1000


async def beam_search(
    problem: Problem[HS, PSNSub],
    initial: SearchNode[HS, PSNSub],
    beam_size: int,
    max_steps: Optional[int] = None,
    event_listener: BeamSearchEventListener = BeamSearchEventListener(),
    keep_finished_nodes: bool = False,
) -> List[FullSearchNode[HS]]:
    max_steps = MAX_STEPS if max_steps is None else max_steps

    finished: Set[HashableNodeWrapper[HS]] = set()
    finished_extra: Set[HashableNodeWrapper[HS]] = set()

    beam: List[SearchNode[HS, PSNSub]] = [initial]

    for step_index in range(max_steps):
        if not beam:
            break

        async def expand(
            node: SearchNode[HS, PSNSub]
        ) -> Tuple[SearchNode[HS, PSNSub], List[FullSearchNode]]:
            expansions = await problem.expand(node)
            return node, expansions

        candidates: Set[HashableNodeWrapper[HS]] = set()
        step_info: Dict[
            Tuple[int, ...], Tuple[SearchNode[HS, PSNSub], List[FullSearchNode[HS]]]
        ] = {}
        for node, per_node_expansion in await asyncio.gather(
            *(expand(node) for node in beam)
        ):
            candidates_for_node: List[FullSearchNode] = []
            packed_node = node.packed if isinstance(node, FullSearchNode) else node
            step_info[packed_node.tokens] = (node, candidates_for_node)
            for new_node in per_node_expansion:
                candidates_for_node.append(new_node)
                candidates.add(HashableNodeWrapper(new_node))
        event_listener.step(step_info)

        # We allow `candidates` and `finished` to compete with each other,
        # as the score will no longer decrease monotonically when we have a length penalty.
        sorted_candidates_plus_finished = sorted(
            itertools.chain(candidates, finished), key=lambda n: n.underlying.cost
        )
        beam = []
        finished.clear()
        for n in sorted_candidates_plus_finished[:beam_size]:
            if n.underlying.is_finished:
                finished.add(n)
            else:
                beam.append(n.underlying)

        # If there's a less-competitive candidate which is finished, then keep it for later
        if keep_finished_nodes:
            for n in sorted_candidates_plus_finished[beam_size:]:
                if n.underlying.is_finished:
                    finished_extra.add(n)

        # Due to cycles or some other reason, hidden states are not freed on
        # time unless we manually collect.
        if step_index % 50 == 0 and step_index > 0:
            print("Garbage collecting ...")
            gc.collect()
            torch.cuda.empty_cache()

    print("Garbage collecting ...")
    gc.collect()
    torch.cuda.empty_cache()

    return sorted(
        (x.underlying for x in itertools.chain(finished, finished_extra)),
        key=lambda n: n.cost,
    )[: beam_size * 2]
