from dataclasses import dataclass
from typing import Optional, TypeVar


@dataclass(frozen=True, eq=True)
class Datum:
    dialogue_id: Optional[str]
    turn_index: Optional[int]
    agent_context: Optional[str]
    natural: str


@dataclass(frozen=True, eq=True)
class FullDatum(Datum):
    canonical: str


# Not contravariant since it is produced in a DataRetriever.
FullDatumSub = TypeVar("FullDatumSub", bound=FullDatum)
# Contravariant since it is ingested by either DataRetriever, DataFilter, or PromptBuilder, but never produced
DatumSub = TypeVar("DatumSub", bound=Datum, contravariant=True)
