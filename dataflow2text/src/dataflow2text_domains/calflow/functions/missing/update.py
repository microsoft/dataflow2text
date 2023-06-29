from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.update_event_response import (
    UpdateEventResponse,
)


@function
def UpdateEventIntensionConstraint() -> Constraint[CalflowIntension[Constraint[Event]]]:
    raise UnableToImplementError()


@function
def UpdateWrapper(findArg: Event, updateArg: Constraint[Event]) -> UpdateEventResponse:
    raise UnableToImplementError()
