from dataclasses import dataclass

from dataflow2text.dataflow.schema import NullaryStructSchema, String
from dataflow2text_domains.calflow.schemas.email_address import EmailAddress
from dataflow2text_domains.calflow.schemas.person_name import PersonName


@dataclass(frozen=True)
class Person(NullaryStructSchema):
    emailAddress: EmailAddress
    displayName: PersonName
    surname: PersonName
    givenName: PersonName
    officeLocation: String
    phoneNumber: String
    jobTitle: String


MeganBowen = Person(
    emailAddress=EmailAddress(String("MeganB@M365x831188.OnMicrosoft.com")),
    displayName=PersonName(String("Megan Bowen")),
    givenName=PersonName(String("Megan")),
    surname=PersonName(String("Bowen")),
    officeLocation=String(""),
    phoneNumber=String(""),
    jobTitle=String(""),
)

DavidLax = Person(
    emailAddress=EmailAddress(String("dlax@thenextunicorn.com")),
    displayName=PersonName(String("David Lax")),
    givenName=PersonName(String("David")),
    surname=PersonName(String("Lax")),
    officeLocation=String(""),
    phoneNumber=String(""),
    jobTitle=String(""),
)

DamonStraeter = Person(
    emailAddress=EmailAddress(String("dstraetor@thenextunicorn.com")),
    displayName=PersonName(String("Damon Straeter")),
    givenName=PersonName(String("Damon")),
    surname=PersonName(String("Straeter")),
    officeLocation=String("STRAETER/2000"),
    phoneNumber=String("800-555-1234"),
    jobTitle=String(""),
)
