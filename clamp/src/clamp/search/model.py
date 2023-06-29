import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Tuple

from clamp.search.datum import DatumSub


@dataclass
class ModelResult:
    text: str
    cost: float
    token_costs: List[Tuple[str, float]] = dataclasses.field(default_factory=list)


class Model(Generic[DatumSub], ABC):
    """Performs the decoding for a given datum."""

    @abstractmethod
    async def predict(self, test_datum: DatumSub) -> List[ModelResult]:
        pass
