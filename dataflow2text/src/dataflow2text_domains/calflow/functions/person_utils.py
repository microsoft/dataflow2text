from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Option
from dataflow2text_domains.calflow.errors.unable_to_implement_error import (
    UnableToImplementError,
)
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.person import DamonStraeter, DavidLax, Person
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@function
def CurrentUser() -> Person:
    # For most dialogues, the default user is DamonStraeter.
    # TODO: Some dialogues may have a different user (e.g., MeganBowen). We could store the info and do a look up
    #  based on dialogue ID.
    return DamonStraeter


@function
def RecipientWithNameLike(
    constraint: Constraint[Recipient], name: PersonName
) -> Constraint[Recipient]:
    def predicate(recipient: Recipient) -> bool:
        if not constraint.allows(recipient):
            return False

        # exact match
        if recipient.name == name:
            return True

        # the `name` is one of the tokens in `recipient.name`
        name_tokens = name.name.inner.lower().split(" ")
        recipient_name_tokens = recipient.name.name.inner.lower().split(" ")
        if len(name_tokens) == 1 and name_tokens[0] in recipient_name_tokens:
            return True

        return False

    return Constraint(type_arg=Recipient.dtype_ctor(), underlying=predicate)


@function
def toRecipient(person: Person) -> Recipient:
    return Recipient(
        emailAddress=Option.from_value(person.emailAddress), name=person.displayName
    )


@function
def FindManager(recipient: Recipient) -> Recipient:
    if recipient.emailAddress.inner == DamonStraeter.emailAddress:
        return Recipient(
            emailAddress=Option.from_value(DavidLax.emailAddress),
            name=DavidLax.displayName,
        )

    raise UnableToImplementError()
