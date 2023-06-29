from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Long, TSchema
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.update_event_response import (
    UpdateEventResponse,
)


@function
def ChoosePersonFromConstraint(
    constraint: Constraint[Recipient], intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()


@function
def ChooseCreateEventFromConstraint(
    constraint: Constraint[Event], intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()


@function
def ChooseUpdateEvent(
    index: Long, intension: CalflowIntension[UpdateEventResponse]
) -> CalflowIntension[UpdateEventResponse]:
    raise NotImplementedError()


@function
def ChooseUpdateEventFromConstraint(
    constraint: Constraint[Event], intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()


@function
def ChooseUpdateEventFromConstraintWrapper(constraint: Constraint[Event]) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseUpdateEventWrapper(index: Long) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseCreateEventFromConstraintWrapper(constraint: Constraint[Event]) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChoosePersonFromConstraintWrapper(constraint: Constraint[Recipient]) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseCreateEventWrapper(index: Long) -> TSchema:  # type: ignore
    raise NotImplementedError()


@function
def ChooseCreateEvent(
    index: Long, intension: CalflowIntension[TSchema]
) -> CalflowIntension[TSchema]:
    raise NotImplementedError()
