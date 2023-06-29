from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, Option, String, TSchema
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_candidate_with_and_without_conflicts import (
    EventCandidatesWithAndWithoutConflicts,
)


@function
def IsBusy(eventCandidates: EventCandidatesWithAndWithoutConflicts) -> Boolean:
    """Returns true if the object passed in includes no Event candidates without conflicts."""
    raise NotImplementedError()


@function
def IsFree(eventCandidates: EventCandidatesWithAndWithoutConflicts) -> Boolean:
    raise NotImplementedError()


@function
def item(t: TSchema) -> Event:
    # In the CalFlow 2.0 data, the lispress program explicitly uses a type arg for `item` (e.g., `item[Dynamic](...)`).
    # However, unlike `roleConstraint` etc., this method does not need to be defined as a generic class in Python.
    # Therefore, we drop the type arg when converting the lispress program to python program.
    raise UnableToImplementError()


@function
def hasTeamsLink() -> Constraint[Option[String]]:
    raise NotImplementedError()
