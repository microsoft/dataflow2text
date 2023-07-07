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

from typing import List

from dataflow2text.dataflow.function import (
    BaseFunction,
    ListCtor,
    StringCtor,
    ValueCtor,
)
from dataflow2text.dataflow.schema import Boolean, Number, Option, String, Unit
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.do import do
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.multiwoz.functions.functions import (
    General,
    Inform,
    OfferBooked,
    Request,
)
from dataflow2text_domains.multiwoz.schemas.schemas import (
    Attraction,
    Hotel,
    Police,
    Restaurant,
    Taxi,
    Train,
)


def make_list(strings: List[str]) -> str:
    if len(strings) == 1:
        return strings[0]
    elif len(strings) == 2:
        return f"{strings[0]} and {strings[1]}"
    else:
        return ", ".join(strings[:-1]) + ", and " + strings[-1]


def pretty_field_name(field: str) -> str:
    match tuple(field.split(".")):
        case (_, "departure"):
            return "departure location"
        case (_, "destination"):
            return "destination"
        case (_, "arrive"):
            return "arrival time"
        case (_, "leave"):
            return "departure time"
        case (_, "area"):
            return "area"
        case ("restaurant", "food" | "type"):
            return "cuisine"
        case (_, "people"):
            return "size of your party"
        case (_, "price"):
            return "price range"
        case ("train", "day"):
            return "date of the trip"
        case (_, "stars"):
            return "star rating"
        case (_, "parking"):
            return "parking"
        case (_, "internet"):
            return "internet"
        case ("attraction", "type"):
            return "type of attraction"
        case ("hotel", "day"):
            return "date of your stay"
        case ("hotel", "time"):
            return "check in time"
        case ("hotel", "stay"):
            return "duration of your stay"
        case ("hotel", "type"):
            return "type of lodging"
        case ("taxi", "day"):
            return "pickup date"
        case ("restaurant", "time"):
            return "reservation time"
        case ("restaurant", "day"):
            return "reservation day"
        case ("general", prop):
            return prop
        case (domain, "name"):
            return f"name of the {domain}"
        case ("hospital", _):
            return None
        case _:
            return None
    raise ValueError(f"unexpected field: {field}")


@generation(
    act=DEFAULT_ACT,
    template="Can you tell me the [field_names] {{ that you're looking for | _ }}?",
)
def handle_request(c: BaseFunction):
    match c:
        case Request(ListCtor(_, paths)):  # type: ignore
            fields = [f.inner for f in paths]
            field_names = [pretty_field_name(f) for f in fields]
            field_names = [f for f in field_names if f is not None]
            if len(field_names) == 0:
                return None
            return {"field_names": StringCtor(make_list(field_names))}


@generation(act=DEFAULT_ACT, template="I found {NP [value]}.")
def handle_inform(c: BaseFunction):
    match c:
        case Inform(value):  # type: ignore
            return {"value": value}


@generation(
    act=DEFAULT_ACT, template="booking was successful. [name] [price] [reference]"
)
def handle_offer_booked(c: BaseFunction):
    match c:
        case OfferBooked(_, ListCtor(_, paths)):  # type: ignore
            results = {}
            for path in paths:
                if path.inner == "train.price":
                    results["price"] = StringCtor(
                        "the total fee is [value_price] gbp payable at the station."
                    )
                elif path.inner.endswith(".reference"):
                    results["reference"] = StringCtor(
                        "your reference number is [value_reference]."
                    )
                elif path.inner.endswith(".name"):
                    results["name"] = StringCtor("I have booked you at [value_name].")

            for key in ["name", "price", "reference"]:
                if key not in results:
                    results[key] = StringCtor("")

            return results


def stringify_time(time: Time) -> str:
    return time.to_python_time().strftime("%H:%M")


@generation(act="DT", template="{{ a | an }}")
def head_one(c: BaseFunction):
    match c:
        case ValueCtor(Option(_, Number(1))):
            return {}
        case ValueCtor(Option(_, None)):
            return {}


@generation(act="DT", template="[count]")
def head_many(c: BaseFunction):
    match c:
        case ValueCtor(
            Option(_, Number(n))
        ) if n > 1:  # pylint: disable=used-before-assignment
            return {"count": StringCtor(str(int(n)))}


@generation(act="NP", template="{DT [count]} [head_str]{{_ | s}} [result_str]")
def taxi(c: BaseFunction):
    match c:
        case ValueCtor(
            Taxi(taxi_type, taxi_phone, leave, arrive, departure, destination, choice)
        ):
            result_parts = []
            match taxi_type:
                case Option(_, String(type_str)):
                    head_str = type_str
                case _:
                    head_str = "taxi"
            match leave:
                case Option(_, Time(h, m, s, n)):
                    result_parts.append(
                        f"leaving at {stringify_time(Time(h, m, s, n))}"
                    )
            match departure:
                case Option(_, String(departure_str)):
                    result_parts.append(f"from {departure_str}")
            match arrive:
                case Option(_, Time(h, m, s, n)):
                    result_parts.append(
                        f"arriving at {stringify_time(Time(h, m, s, n))}"
                    )
            match destination:
                case Option(_, String(destination_str)):
                    result_parts.append(f"to {destination_str}")
            match taxi_phone:
                case Option(_, String(phone_str)):
                    result_parts.append(f"with phone number {phone_str}")
            result_str = " ".join(result_parts)
            return {
                "count": ValueCtor(choice),
                "head_str": StringCtor(head_str),
                "result_str": StringCtor(result_str),
            }


@generation(act="NP", template="{DT [count]} [head_str]{{_ | s}} [result_str]")
def attraction(c: BaseFunction):
    match c:
        case ValueCtor(
            Attraction(
                attraction_type,
                price,
                area,
                name,
                address,
                postcode,
                phone_number,
                choice,
            )
        ):
            result_parts = []
            match attraction_type:
                case Option(_, String(type_str)):
                    head_str = type_str
                case _:
                    head_str = "attraction"
            match name:
                case Option(_, String(name_str)):
                    result_parts.append(f"called {name_str}")
            match price:
                case Option(_, String(price_str)):
                    result_parts.append(f"costing {price_str}")
            match address:
                case Option(_, String(address_str)):
                    result_parts.append(f"at {address_str}")
                    match postcode:
                        case Option(_, String(postcode_str)):
                            result_parts.append(f", {postcode_str}")
                case Option(_, None):
                    match postcode:
                        case Option(_, String(postcode_str)):
                            result_parts.append(f"at postcode {postcode_str}")
            match area:
                case Option(_, String(area_str)):
                    result_parts.append(f"in the {area_str}")
            match phone_number:
                case Option(_, String(phone_str)):
                    result_parts.append(f"(phone number {phone_str})")
            result_str = " ".join(result_parts)
            return {
                "count": ValueCtor(choice),
                "head_str": StringCtor(head_str),
                "result_str": StringCtor(result_str),
            }


@generation(act="NP", template="{DT [count]} [head_str]{{_ | s}} [result_str]")
def hotel(c: BaseFunction):
    match c:
        case ValueCtor(
            Hotel(
                postcode,
                area,
                name,
                address,
                _,
                hotel_type,
                hotel_phone,
                _,
                internet,
                parking,
                choice,
            )
        ):
            sentences = []
            result_parts = []
            match hotel_type:
                case Option(_, String(type_str)):
                    head_str = type_str
                case _:
                    head_str = "hotel"
            match name:
                case Option(_, String(name_str)):
                    result_parts.append(f"named {name_str}")
            match address:
                case Option(_, String(address_str)):
                    result_parts.append(f"at {address_str}")
                    match postcode:
                        case Option(_, String(postcode_str)):
                            result_parts.append(f", {postcode_str}")
                case Option(_, None):
                    match postcode:
                        case Option(_, String(postcode_str)):
                            result_parts.append(f"at postcode {postcode_str}")
            match area:
                case Option(_, String(area_str)):
                    result_parts.append(f"in the {area_str}")
            match hotel_phone:
                case Option(_, String(phone_str)):
                    if len(result_parts) > 0:
                        sentences.append(result_parts)
                        result_parts = []
                    result_parts.append(f"Their phone number is {phone_str}")
            sentences.append(result_parts)
            attributes = []
            match internet:
                case Option(_, Boolean(True)):
                    attributes.append("internet")
            match parking:
                case Option(_, Boolean(True)):
                    attributes.append("parking")

            attribute_str = ""
            if len(attributes) == 1:
                attribute_str = attributes[0]
            elif len(attributes) == 2:
                attribute_str = f"{attributes[0]} and {attributes[1]}"
            elif len(attributes) > 2:
                attribute_str = ", ".join(attributes[:-1]) + " and " + attributes[-1]
            if len(attribute_str) > 0:
                sentences.append([f"They have {attribute_str}"])
            result_str = ". ".join([" ".join(sentence) for sentence in sentences])
            return {
                "count": ValueCtor(choice),
                "head_str": StringCtor(head_str),
                "result_str": StringCtor(result_str),
            }


@generation(act="NP", template="{DT [count]} [head_str]{{_ | s}} [result_str]")
def restaurant(c: BaseFunction):
    match c:
        case ValueCtor(
            Restaurant(
                food, pricerange, area, address, name, postcode, phone_number, choice
            )
        ):
            sentences = []
            head_str_parts = []
            result_parts = []
            match pricerange:
                case Option(_, String(price_str)):
                    head_str_parts.append(price_str)
            match food:
                case Option(_, String(food_str)):
                    head_str_parts.append(f"{food_str} restaurant")
                case _:
                    head_str_parts.append("restaurant")
            match name:
                case Option(_, String(name_str)):
                    result_parts.append(f"named {name_str}")
            match area:
                case Option(_, String(area_str)):
                    result_parts.append(f"in the {area_str}")
            match address:
                case Option(_, String(address_str)):
                    result_parts.append(f"located at {address_str}")
                    match postcode:
                        case Option(_, String(postcode_str)):
                            result_parts.append(f", {postcode_str}")
                case Option(_, None):
                    match postcode:
                        case Option(_, String(postcode_str)):
                            result_parts.append(f"at postcode {postcode_str}")
            match phone_number:
                case Option(_, String(phone_str)):
                    if len(result_parts) > 0:
                        sentences.append(result_parts)
                        result_parts = []
                    result_parts.append(f". Their phone number is {phone_str}")

            if len(result_parts) > 0:
                sentences.append(result_parts)
            head_str = " ".join(head_str_parts)
            result_str = " ".join([" ".join(sentence) for sentence in sentences])
            return {
                "count": ValueCtor(choice),
                "head_str": StringCtor(head_str),
                "result_str": StringCtor(result_str),
            }


@generation(act="NP", template="{DT [count]} train{{_ | s}} [result_str]")
def train(c: BaseFunction):
    match c:
        case ValueCtor(
            Train(
                day,
                leave,
                arrive,
                departure,
                destination,
                price,
                train_id,
                time,
                choice,
            )
        ):
            result_parts = []
            match train_id:
                case Option(_, String(train_id_str)):
                    result_parts.append(f"{train_id_str}")
            match day:
                case Option(_, String(day_str)):
                    result_parts.append(f"on {day_str}")
            match leave:
                case Option(_, Time(h, m, s, n)):
                    result_parts.append(
                        f"leaving at {stringify_time(Time(h, m, s, n))}"
                    )
            match departure:
                case Option(_, String(dep_str)):
                    result_parts.append(f"from {dep_str}")
            match arrive:
                case Option(_, Time(h, m, s, n)):
                    result_parts.append(
                        f"arriving at {stringify_time(Time(h, m, s, n))}"
                    )
            match destination:
                case Option(_, String(dest_str)):
                    result_parts.append(f"to {dest_str}")
            match time:
                case Option(_, String(duration_str)):
                    result_parts.append(f"with a travel time of {duration_str}")
            match price:
                case Option(_, String(price_str)):
                    result_parts.append(f"for {price_str}")
            result_str = " ".join(result_parts)
            return {"count": ValueCtor(choice), "result_str": StringCtor(result_str)}


@generation(act="NP", template="[result_str]")
def police(c: BaseFunction):
    match c:
        case ValueCtor(Police(name, phone, address)):
            result_parts = []
            match name:
                case Option(_, String(name_str)):
                    result_parts.append(name_str)
            result_parts.append("police")
            match address:
                case Option(_, String(address_str)):
                    result_parts.append(f"at {address_str}")
            match phone:
                case Option(_, String(phone_str)):
                    result_parts.append(f"with the phone number {phone_str}")
            result_str = " ".join(result_parts)
            return {"result_str": StringCtor(result_str)}


@generation(act=DEFAULT_ACT, template="[utt]")
def handle_general(c: BaseFunction):
    match c:
        case General(StringCtor("bye")):  # type: ignore
            return {"utt": StringCtor("Goodbye!")}
        case General(StringCtor("offerbook")):  # type: ignore
            return {"utt": StringCtor("Would you like me to book it?")}
        case General(StringCtor("reqmore")):  # type: ignore
            return {"utt": StringCtor("Can I help you with anything else?")}
        case General(StringCtor("welcome")):  # type: ignore
            return {"utt": StringCtor("You're very welcome!")}
        case General(StringCtor("offerbooked")):  # type: ignore
            return {"utt": StringCtor("Ok, I've booked that for you.")}
        case General(StringCtor("nooffer")):  # type: ignore
            return {
                "utt": StringCtor(
                    "Sorry, I wasn't able to find anything satisfying your request."
                )
            }
        case General(StringCtor("select")):  # type: ignore
            return {"utt": StringCtor("MYSTERY")}
        case General(StringCtor("hospital")):  # type: ignore
            return None
        case General(_):  # type: ignore
            # this is a malformed MR
            return None


@generation(act=DEFAULT_ACT, template="Ok.")
def handle_unit(c: BaseFunction):
    match c:
        case ValueCtor(Unit()):
            return {}


@generation(
    act=DEFAULT_ACT, template=f"{{ {DEFAULT_ACT} [x] }} {{ {DEFAULT_ACT} [y] }}"
)
def handle_do(c: BaseFunction):
    match c:
        case do(x, y):
            return {"x": x, "y": y}
