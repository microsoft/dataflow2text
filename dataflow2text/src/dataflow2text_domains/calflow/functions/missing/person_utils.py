from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, List
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_candidate_with_and_without_conflicts import (
    EventCandidatesWithAndWithoutConflicts,
)
from dataflow2text_domains.calflow.schemas.person import Person
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@function
def PersonFromRecipient(recipient: Recipient) -> Person:
    raise NotImplementedError()


@function
def PersonOnTeam(person: Person, team: List[Person]) -> Boolean:
    raise NotImplementedError()


@function
def PersonWithNameLike(
    constraint: Constraint[Person], name: PersonName
) -> Constraint[Person]:
    raise NotImplementedError()


@function
def RecipientAvailability(
    eventConstraint: Constraint[Event], includingMe: Boolean
) -> EventCandidatesWithAndWithoutConflicts:
    raise NotImplementedError()


@function
def RecipientFromRecipientConstraint(constraint: Constraint[Recipient]) -> Recipient:
    raise NotImplementedError()
