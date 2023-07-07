# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
