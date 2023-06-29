from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import List, Long, TSchema, Unit
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.path import Path


@function
def AgentStillHere() -> Unit:
    return Unit()


@function
def CancelScreen() -> Unit:
    return Unit()


@function
def DoNotConfirm() -> Unit:
    return Unit()


@function
def UserPauseResponse() -> Unit:
    return Unit()


@function
def numberToIndexPath(number: Long) -> Path:
    return Path(f"[{number}]")


# pylint: disable=redefined-builtin
@function
def minBy(list: List[TSchema], path: Path) -> TSchema:
    raise NotImplementedError()


@function
def roomRequest() -> Constraint[LocationKeyphrase]:
    """Returns a constraint that requests a conference room.

    For now the predicate always returns true.
    """

    def predicate(x: LocationKeyphrase) -> bool:
        return True

    return Constraint(type_arg=LocationKeyphrase.dtype_ctor(), underlying=predicate)


@function
def RepeatAgent() -> Unit:
    raise NotImplementedError()
