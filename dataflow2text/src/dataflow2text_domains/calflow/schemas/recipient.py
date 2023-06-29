from dataclasses import dataclass
from typing import Any, Dict

from dataflow2text.dataflow.schema import NullaryStructSchema, Option
from dataflow2text_domains.calflow.schemas.email_address import EmailAddress
from dataflow2text_domains.calflow.schemas.person import Person
from dataflow2text_domains.calflow.schemas.person_name import PersonName


@dataclass(frozen=True)
class Recipient(NullaryStructSchema):
    name: PersonName
    emailAddress: Option[EmailAddress]

    @classmethod
    def from_typed_json(cls, json_obj: Dict[str, Any]) -> "Recipient":
        schema = json_obj.get("schema")
        assert schema == "Recipient"
        underlying = json_obj.get("underlying")
        assert underlying is not None

        email_address_obj = underlying.get("emailAddress")
        if email_address_obj is None:
            email_address = None
        else:
            email_address = EmailAddress.from_typed_json(underlying.get("emailAddress"))

        return Recipient(
            emailAddress=Option(
                type_arg=EmailAddress.dtype_ctor(), inner=email_address
            ),
            name=PersonName.from_typed_json(underlying.get("name")),
        )

    @classmethod
    def from_person(cls, person: Person) -> "Recipient":
        return Recipient(
            emailAddress=Option.from_value(person.emailAddress), name=person.displayName
        )
