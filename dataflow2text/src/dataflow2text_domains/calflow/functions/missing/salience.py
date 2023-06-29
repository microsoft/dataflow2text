from typing import TypeVar

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import BaseSchema
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint

_T = TypeVar("_T", bound=BaseSchema)
_R = TypeVar("_R", bound=BaseSchema)


@function
def NewClobber(
    intension: CalflowIntension[_R],
    slotConstraint: Constraint[CalflowIntension[_T]],
    value: CalflowIntension[_T],
) -> CalflowIntension[_R]:
    raise UnableToImplementError()


@function
def refer(constraint: Constraint[CalflowIntension[_T]]) -> CalflowIntension[_T]:
    raise UnableToImplementError()


@function
def ClobberWrapper(
    oldLocation: Constraint[CalflowIntension[Constraint[_T]]], new: Constraint[_T]
) -> _R:  # type: ignore
    raise UnableToImplementError()


@function
def NewClobberWrapper(oldArg: Constraint[CalflowIntension[_T]], newArg: _T) -> _R:  # type: ignore
    raise UnableToImplementError()
