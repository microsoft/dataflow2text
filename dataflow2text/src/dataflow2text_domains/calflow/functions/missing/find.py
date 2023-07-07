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
