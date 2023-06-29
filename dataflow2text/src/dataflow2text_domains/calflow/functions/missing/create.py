from dataflow2text.dataflow.function import function
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.create_commit_event import CreateCommitEvent
from dataflow2text_domains.calflow.schemas.create_event_response import (
    CreateEventResponse,
)
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@function
def CreateCommitEventWrapper(event: CreateCommitEvent) -> CreateEventResponse:
    raise NotImplementedError()


@function
def CreatePreflightEventWrapper(constraint: Constraint[Event]) -> CreateCommitEvent:
    raise NotImplementedError()


@function
def CreateAddPerson(name: PersonName) -> Recipient:
    raise NotImplementedError()
