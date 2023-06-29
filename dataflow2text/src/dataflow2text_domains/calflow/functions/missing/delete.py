from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.delete_commit_event import DeleteCommitEvent
from dataflow2text_domains.calflow.schemas.delete_event_response import (
    DeleteEventResponse,
)
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_id import EventId


@function
def DeleteCommitEventWrapper(event: DeleteCommitEvent) -> DeleteEventResponse:
    raise UnableToImplementError()


# pylint: disable=redefined-builtin
@function
def DeletePreflightEventWrapper(id: EventId) -> DeleteCommitEvent:
    raise UnableToImplementError()


@function
def DeleteWrapper(findArg: Event) -> DeleteEventResponse:
    raise UnableToImplementError()
