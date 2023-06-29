from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean
from dataflow2text_domains.calflow.schemas.weather_table import WeatherTable


@function
def IsCloudy(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsCold(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsHot(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsHighUV(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsRainy(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsSnowy(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsStormy(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsSunny(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def IsWindy(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def WillSleet(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def WillRain(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def WillSnow(table: WeatherTable) -> Boolean:
    raise NotImplementedError()


@function
def NeedsJacket(table: WeatherTable) -> Boolean:
    raise NotImplementedError()
