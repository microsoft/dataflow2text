from dataclasses import dataclass

from dataflow2text.dataflow.schema import List, NullaryStructSchema, Number, String
from dataflow2text_domains.calflow.schemas.money import Money
from dataflow2text_domains.calflow.schemas.open_period import OpenPeriod
from dataflow2text_domains.calflow.schemas.place_feature import PlaceFeature
from dataflow2text_domains.calflow.schemas.weather_property import Point


@dataclass(frozen=True)
class Place(NullaryStructSchema):
    formattedAddress: String
    phoneNumber: String
    price: Money
    rating: Number
    url: String
    hours: List[OpenPeriod]
    features: List[PlaceFeature]
    location: Point
