from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.create_event_response import (
    CreateEventResponse,
)
from dataflow2text_domains.calflow.schemas.delete_event_response import (
    DeleteEventResponse,
)
from dataflow2text_domains.calflow.schemas.event import Event


@function
def ConfirmCreateAndReturnAction(
    constraint: Constraint[Event],
) -> CalflowIntension[CreateEventResponse]:
    raise NotImplementedError()


@function
def ConfirmDeleteAndReturnAction(
    constraint: Constraint[Event],
) -> CalflowIntension[DeleteEventResponse]:
    raise NotImplementedError()
