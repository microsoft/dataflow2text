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

from math import atan2, cos, radians, sin, sqrt

from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, Number
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.length_unit import LengthUnit
from dataflow2text_domains.calflow.schemas.place import Place
from dataflow2text_domains.calflow.schemas.place_feature import PlaceFeature
from dataflow2text_domains.calflow.schemas.weather_property import Length, Point


def _distance(point1: Point, point2: Point) -> Length:
    # copied from https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    earth_radius_in_km = 6373.0

    lat1 = radians(point1.lat.inner)
    lon1 = radians(point2.lon.inner)
    lat2 = radians(point2.lat.inner)
    lon2 = radians(point2.lon.inner)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = earth_radius_in_km * c

    return Length(Number(dist), LengthUnit.Kilometers())


@function
def within(point: Point, constraintDistance: Length) -> Constraint[Point]:
    def predicate(queryPoint: Point) -> bool:
        return _distance(point, queryPoint) <= constraintDistance

    return Constraint(type_arg=Point.dtype_ctor(), underlying=predicate)


@function
def Here() -> Place:
    raise NotImplementedError()


@function
def PlaceDescribableLocation(place: Place) -> Place:
    return place


@function
def PlaceHasFeature(feature: PlaceFeature, place: Place) -> Boolean:
    return Boolean(feature in place.features.inner)


@function
def AtPlace(place: Place) -> Constraint[Point]:
    def predicate(pt: Point) -> bool:
        return _distance(pt, place.location) <= Length(
            Number(10), LengthUnit.Kilometers()
        )

    return Constraint(type_arg=Point.dtype_ctor(), underlying=predicate)
