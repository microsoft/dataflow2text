from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import List, Long
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.person import Person
from dataflow2text_domains.calflow.schemas.person_name import PersonName
from dataflow2text_domains.calflow.schemas.place import Place
from dataflow2text_domains.calflow.schemas.place_search_response import (
    PlaceSearchResponse,
)
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.weather_property import Point


@function
def FindPlaceAtHere(
    place: LocationKeyphrase, radiusConstraint: Constraint[Point]
) -> PlaceSearchResponse:
    raise NotImplementedError()


@function
def FindPlaceMultiResults(place: LocationKeyphrase) -> PlaceSearchResponse:
    raise NotImplementedError()


@function
def FindReports(recipient: Recipient) -> List[Person]:
    raise NotImplementedError()


@function
def FindTeamOf(recipient: Recipient) -> List[Person]:
    raise NotImplementedError()


@function
def FindAddPerson(name: PersonName) -> Constraint[List[Attendee]]:
    raise NotImplementedError()


@function
def FindNumNextEventWrapper(constraint: Constraint[Event], number: Long) -> Event:
    raise NotImplementedError()


@function
def FindPlace(keyphrase: LocationKeyphrase) -> Place:
    raise NotImplementedError()
