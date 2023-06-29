from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import List, Number, TSchema
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.lambd import Lambda
from dataflow2text_domains.calflow.schemas.weather_property import (
    Angle,
    Dimensionless,
    Length,
    Point,
    Pressure,
    Temperature,
    Velocity,
)
from dataflow2text_domains.calflow.schemas.weather_quantifier import WeatherQuantifier
from dataflow2text_domains.calflow.schemas.weather_table import WeatherTable


@function
def temperature() -> Lambda[WeatherTable, Temperature]:
    raise NotImplementedError()


@function
def apparentTemperature() -> Lambda[WeatherTable, Temperature]:
    raise NotImplementedError()


@function
def precipProbability() -> Lambda[WeatherTable, Dimensionless]:
    raise NotImplementedError()


@function
def precipAccumulation() -> Lambda[WeatherTable, Length]:
    raise NotImplementedError()


@function
def precipIntensity() -> Lambda[WeatherTable, Velocity]:
    raise NotImplementedError()


@function
def rainPrecipProbability() -> Lambda[WeatherTable, Dimensionless]:
    raise NotImplementedError()


@function
def snowPrecipProbability() -> Lambda[WeatherTable, Dimensionless]:
    raise NotImplementedError()


@function
def snowPrecipAccumulation() -> Lambda[WeatherTable, Length]:
    raise NotImplementedError()


@function
def rainPrecipAccumulation() -> Lambda[WeatherTable, Length]:
    raise NotImplementedError()


@function
def snowPrecipIntensity() -> Lambda[WeatherTable, Velocity]:
    raise NotImplementedError()


@function
def rainPrecipIntensity() -> Lambda[WeatherTable, Velocity]:
    raise NotImplementedError()


@function
def dewPoint() -> Lambda[WeatherTable, Temperature]:
    raise NotImplementedError()


@function
def pressure() -> Lambda[WeatherTable, Pressure]:
    raise NotImplementedError()


@function
def cloudCover() -> Lambda[WeatherTable, Dimensionless]:
    raise NotImplementedError()


@function
def humidity() -> Lambda[WeatherTable, Dimensionless]:
    raise NotImplementedError()


@function
def sunsetTime() -> Lambda[WeatherTable, DateTime]:
    raise NotImplementedError()


@function
def sunriseTime() -> Lambda[WeatherTable, DateTime]:
    raise NotImplementedError()


@function
def windSpeed() -> Lambda[WeatherTable, Velocity]:
    raise NotImplementedError()


@function
def windBearing() -> Lambda[WeatherTable, Angle]:
    raise NotImplementedError()


@function
def uvIndex() -> Lambda[WeatherTable, Number]:
    raise NotImplementedError()


@function
def visibility() -> Lambda[WeatherTable, Length]:
    raise NotImplementedError()


@function
def toFahrenheit(temperature_: Number) -> Temperature:
    raise NotImplementedError()


@function
def toCelsius(temperature_: Number) -> Temperature:
    raise NotImplementedError()


@function
def inFahrenheit(temperature_: Temperature) -> Temperature:
    raise NotImplementedError()


@function
def inCelsius(temperature_: Temperature) -> Temperature:
    raise NotImplementedError()


@function
def inInches(length: Length) -> Length:
    raise NotImplementedError()


@function
def inUsMilesPerHour(speed: Velocity) -> Velocity:
    raise NotImplementedError()


@function
def inKilometersPerHour(speed: Velocity) -> Velocity:
    raise NotImplementedError()


@function
def WeatherForEvent(event: Event) -> WeatherTable:
    raise NotImplementedError()


@function
def NumberInDefaultTempUnits(number: Number) -> Temperature:
    raise NotImplementedError()


# pylint: disable=redefined-builtin
@function
def WhenProperty(
    property: Lambda[WeatherTable, TSchema],
    quantifier: WeatherQuantifier,
    wt: WeatherTable,
) -> List[DateTime]:
    raise NotImplementedError()


@function
def WeatherQueryApi(
    place: Constraint[Point], time: Constraint[DateTime]
) -> WeatherTable:
    raise NotImplementedError()


# pylint: disable=redefined-builtin
@function
def WeatherAggregate(
    quantifier: WeatherQuantifier,
    property: Lambda[WeatherTable, TSchema],
    table: WeatherTable,
) -> TSchema:
    raise NotImplementedError()
