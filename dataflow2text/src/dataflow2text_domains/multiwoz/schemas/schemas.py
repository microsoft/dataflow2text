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
from datetime import datetime

from dataflow2text.dataflow.schema import (
    BaseSchema,
    Boolean,
    NullaryStructSchema,
    Number,
    Option,
    String,
)
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text_domains.calflow.helpers.conversions import (
    convert_python_time_to_calflow_time,
)
from dataflow2text_domains.calflow.schemas.time import Time

NONE_BOOL: Option[Boolean] = Option(Boolean.dtype_ctor(), None)
NONE_NUMBER: Option[Number] = Option(Number.dtype_ctor(), None)
NONE_STRING: Option[String] = Option(String.dtype_ctor(), None)
NONE_TIME: Option[Time] = Option(Time.dtype_ctor(), None)


def try_wrap(schema, inner, preproc=lambda x: x):
    match inner:
        case None | "?":
            result = Option(schema.dtype_ctor(), None)
            return result
        case _:
            match schema.dtype_ctor():
                case TypeName("Time"):
                    return Option.from_value(
                        convert_python_time_to_calflow_time(
                            datetime.strptime(inner, "%H:%M").time()
                        )
                    )
                case _:
                    return Option.from_value(schema(preproc(inner)))


def convert_boolean(value: str):
    value = value.lower()
    match value:
        case "yes" | "true":
            return True
        case "no" | "false":
            return False
        case _:
            raise ValueError(f"Cannot convert boolean {value}")


class MultiwozResult(BaseSchema):
    pass


@dataclass
class Hotel(MultiwozResult, NullaryStructSchema):
    postcode: Option[String] = NONE_STRING
    area: Option[String] = NONE_STRING
    name: Option[String] = NONE_STRING
    address: Option[String] = NONE_STRING
    price_single: Option[String] = NONE_STRING
    type: Option[String] = NONE_STRING
    phone: Option[String] = NONE_STRING
    stars: Option[Number] = NONE_NUMBER
    internet: Option[Boolean] = NONE_BOOL
    parking: Option[Boolean] = NONE_BOOL
    choice: Option[Number] = NONE_NUMBER

    @classmethod
    def from_json(cls, json):
        postcode = try_wrap(String, json.get("postcode"))
        area = try_wrap(String, json.get("area"))
        name = try_wrap(String, json.get("name"))
        address = try_wrap(String, json.get("address"))
        price = try_wrap(String, json.get("price"), preproc=str)
        type = try_wrap(String, json.get("type"))  # pylint: disable=redefined-builtin
        phone = try_wrap(String, json.get("phone"))
        stars = try_wrap(Number, json.get("stars"), preproc=float)
        internet = try_wrap(Boolean, json.get("internet"), preproc=convert_boolean)
        parking = try_wrap(Boolean, json.get("parking"), preproc=convert_boolean)
        choice = try_wrap(Number, json.get("choice"), preproc=float)

        if (
            len(
                set(json.keys())
                - {
                    "postcode",
                    "area",
                    "name",
                    "address",
                    "price",
                    "type",
                    "phone",
                    "stars",
                    "internet",
                    "parking",
                    "id",
                    "choice",
                }
            )
            > 0
        ):
            assert False, json
        return Hotel(
            postcode,
            area,
            name,
            address,
            price,
            type,
            phone,
            stars,
            internet,
            parking,
            choice,
        )


@dataclass
class Restaurant(MultiwozResult, NullaryStructSchema):
    food: Option[String] = NONE_STRING
    pricerange: Option[String] = NONE_STRING
    area: Option[String] = NONE_STRING
    address: Option[String] = NONE_STRING
    name: Option[String] = NONE_STRING
    postcode: Option[String] = NONE_STRING
    phone: Option[String] = NONE_STRING
    choice: Option[Number] = NONE_NUMBER

    @classmethod
    def from_json(cls, json):
        food = try_wrap(String, json.get("food"))
        pricerange = try_wrap(String, json.get("pricerange"))
        area = try_wrap(String, json.get("area"))
        address = try_wrap(String, json.get("address"))
        name = try_wrap(String, json.get("name"))
        postcode = try_wrap(String, json.get("postcode"))
        phone = try_wrap(String, json.get("phone"))
        choice = try_wrap(Number, json.get("choice"), preproc=float)
        if "price" in json.keys() or "type" in json.keys():
            raise ValueError()
        if (
            len(
                set(json.keys())
                - {
                    "food",
                    "pricerange",
                    "area",
                    "address",
                    "name",
                    "postcode",
                    "phone",
                    "id",
                    "choice",
                }
            )
            > 0
        ):
            assert False, json
        return Restaurant(
            food, pricerange, area, address, name, postcode, phone, choice
        )


@dataclass
class Train(MultiwozResult, NullaryStructSchema):
    day: Option[String] = NONE_STRING
    leave: Option[Time] = NONE_TIME
    arrive: Option[Time] = NONE_TIME
    departure: Option[String] = NONE_STRING
    destination: Option[String] = NONE_STRING
    price: Option[String] = NONE_STRING
    train_id: Option[String] = NONE_STRING
    time: Option[
        String
    ] = NONE_STRING  # TODO: we could eventually use the Duration schema for this
    choice: Option[Number] = NONE_NUMBER

    @classmethod
    def from_json(cls, json):
        day = try_wrap(String, json.get("day"))
        leave = try_wrap(Time, json.get("leave"))
        arrive = try_wrap(Time, json.get("arrive"))
        departure = try_wrap(String, json.get("departure"))
        destination = try_wrap(String, json.get("destination"))
        price = try_wrap(String, json.get("price"))
        train_id = try_wrap(String, json.get("id"))
        time = try_wrap(String, json.get("time"))
        choice = try_wrap(Number, json.get("choice"), preproc=float)
        if (
            "area" in json.keys()
            or "food" in json.keys()
            or "name" in json.keys()
            or "type" in json.keys()
            or "area" in json.keys()
        ):
            raise ValueError()
        if (
            len(
                set(json.keys())
                - {
                    "day",
                    "choice",
                    "leave",
                    "arrive",
                    "id",
                    "departure",
                    "destination",
                    "price",
                    "choice",
                    "people",
                    "time",
                }
            )
            > 0
        ):
            assert False, json
        return Train(
            day, leave, arrive, departure, destination, price, train_id, time, choice
        )


@dataclass
class Attraction(MultiwozResult, NullaryStructSchema):
    type: Option[String] = NONE_STRING
    price: Option[String] = NONE_STRING
    area: Option[String] = NONE_STRING
    name: Option[String] = NONE_STRING
    address: Option[String] = NONE_STRING
    postcode: Option[String] = NONE_STRING
    phone: Option[String] = NONE_STRING
    choice: Option[Number] = NONE_NUMBER

    @classmethod
    def from_json(cls, json):
        price = try_wrap(String, json.get("price"), preproc=str)
        type = try_wrap(  # pylint: disable=redefined-builtin
            String, json.get("type"), preproc=str
        )
        area = try_wrap(String, json.get("area"))
        name = try_wrap(String, json.get("name"))
        address = try_wrap(String, json.get("address"))
        postcode = try_wrap(String, json.get("postcode"))
        phone = try_wrap(String, json.get("phone"))
        choice = try_wrap(Number, json.get("choice"), preproc=float)
        if "stars" in json.keys() or "destination" in json.keys():
            raise ValueError()
        if (
            len(
                set(json.keys())
                - {
                    "type",
                    "price",
                    "area",
                    "address",
                    "name",
                    "postcode",
                    "phone",
                    "choice",
                    "id",
                }
            )
            > 0
        ):
            assert False, json
        return Attraction(type, price, area, name, address, postcode, phone, choice)


@dataclass
class Parking(MultiwozResult, NullaryStructSchema):
    @classmethod
    def from_json(cls, json):
        if len(set(json.keys())) > 0:
            assert False, json
        return Parking()


@dataclass
class Police(MultiwozResult, NullaryStructSchema):
    name: Option[String] = NONE_STRING
    phone: Option[String] = NONE_STRING
    address: Option[String] = NONE_STRING

    @classmethod
    def from_json(cls, json):
        name = try_wrap(String, json.get("name"))
        phone = try_wrap(String, json.get("phone"))
        address = try_wrap(String, json.get("address"))
        if len(set(json.keys()) - {"name", "phone", "address"}) > 0:
            assert False, json
        return Police(name, phone, address)


@dataclass
class Taxi(MultiwozResult, NullaryStructSchema):
    taxi_types: Option[String] = NONE_STRING
    taxi_phone: Option[String] = NONE_STRING
    leave: Option[Time] = NONE_TIME
    arrive: Option[Time] = NONE_TIME
    departure: Option[String] = NONE_STRING
    destination: Option[String] = NONE_STRING
    choice: Option[Number] = NONE_NUMBER

    @classmethod
    def from_json(cls, json):
        taxi_types = try_wrap(String, json.get("taxi_types"))
        taxi_phone = try_wrap(String, json.get("taxi_phone"))
        leave = try_wrap(Time, json.get("leave"))
        arrive = try_wrap(Time, json.get("arrive"))
        departure = try_wrap(String, json.get("departure"))
        destination = try_wrap(String, json.get("destination"))
        choice = try_wrap(Number, json.get("choice"), preproc=float)
        if "name" in json.keys():
            raise ValueError()
        if (
            len(
                set(json.keys())
                - {
                    "taxi_types",
                    "taxi_phone",
                    "leave",
                    "arrive",
                    "departure",
                    "destination",
                    "choice",
                    "id",
                }
            )
            > 0
        ):
            assert False, json
        return Taxi(
            taxi_types, taxi_phone, leave, arrive, departure, destination, choice
        )
