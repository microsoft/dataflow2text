import dataclasses
import heapq
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Set, Tuple

from clamp.search.search_node import FullSearchNode, SearchNode
from clamp.seq2seq.seq2seq_model import HS
from clamp.tokenization.clamp_tokenizer import ClampTokenizer


@dataclass
class HashableNodeWrapper(Generic[HS]):
    underlying: FullSearchNode[HS]
    _key: Tuple[Tuple[int, ...], bool] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._key = (self.underlying.tokens, self.underlying.is_finished)

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, HashableNodeWrapper):
            return False
        return self._key == other._key


class BeamSearchEventListener:
    def step(
        self,
        expansions: Dict[
            Tuple[int, ...], Tuple[SearchNode[Any, Any], List[FullSearchNode[Any]]]
        ],
    ) -> None:
        pass


@dataclass
class LoggingEventListener(BeamSearchEventListener):
    tokenizer: ClampTokenizer
    beam_size: int
    last_step: int = 0

    # pylint: disable=arguments-renamed
    def step(
        self,
        all_expansions: Dict[
            Tuple[int, ...], Tuple[SearchNode[Any, Any], List[FullSearchNode[Any]]]
        ],
    ) -> None:
        # TODO: Print which of the expansions are being kept in the beam/finished lists.
        already_printed: Set[HashableNodeWrapper] = set()
        header = f"===== DEPTH {self.last_step} ====="
        print(header)
        # Instrumentation.print_last_requests()
        for _, (node, expansions) in all_expansions.items():
            if isinstance(node, FullSearchNode):
                node_cost_str = f" [{node.cost:.3f}]"
            else:
                node_cost_str = ""

            duplicates = 0
            # `node` expands to the nodes in `expansions`.
            print(
                f"Completions for {self.tokenizer.decode(list(node.tokens))!r}{node_cost_str}:"
            )
            for expansion in heapq.nsmallest(
                self.beam_size * 2, expansions, key=lambda n: n.cost
            ):
                deduplicating_node = HashableNodeWrapper(expansion)
                if deduplicating_node in already_printed:
                    duplicates += 1
                    continue
                already_printed.add(deduplicating_node)

                if expansion.is_finished:
                    complete = self.tokenizer.decode(list(expansion.tokens))
                    print(f"- Finished: {complete!r} -> [{expansion.cost:.3f}]")
                else:
                    last_token = self.tokenizer.decode(
                        list(expansion.tokens[len(node.tokens) :])
                    )
                    if isinstance(node, FullSearchNode):
                        print(
                            f"- {last_token!r} [{expansion.unnormalized_cost - node.unnormalized_cost:.3f}] -> [{expansion.cost:.3f}]"
                        )
                    else:
                        # TODO: Get the cost of the node so that we can report the difference
                        print(f"- {last_token!r} -> [{expansion.cost:.3f}]")

            if duplicates:
                print(f"- [{duplicates} duplicates of already printed in depth]")
            if len(expansions) > self.beam_size * 2:
                print(f"... and {len(expansions) - self.beam_size * 2} more")
        print("=" * len(header))
        self.last_step += 1
