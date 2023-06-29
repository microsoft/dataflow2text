"""This file contains conversion methods from python native types to calflow schemas or other python native types.

Conversions from calflow types to python native types are usually defined on the type dataclasses themselves.
"""
import datetime
from typing import cast

import pytz

from dataflow2text.dataflow.schema import Long, String
from dataflow2text_domains.calflow.schemas.date import Date
from dataflow2text_domains.calflow.schemas.date_time import DateTime, TimeZone
from dataflow2text_domains.calflow.schemas.day import Day
from dataflow2text_domains.calflow.schemas.month import Month
from dataflow2text_domains.calflow.schemas.time import Time
from dataflow2text_domains.calflow.schemas.year import Year


def convert_python_date_to_calflow_date(python_date: datetime.date) -> Date:
    return Date(
        year=Year(python_date.year),
        month=Month(python_date.month),
        day=Day(python_date.day),
    )


def convert_python_time_to_calflow_time(python_time: datetime.time) -> Time:
    return Time(
        hour=Long(python_time.hour),
        minute=Long(python_time.minute),
        second=Long(python_time.second),
        nanosecond=Long(python_time.microsecond * 1000),
    )


def convert_python_datetime_to_calflow_datetime(
    python_datetime: datetime.datetime,
) -> DateTime:
    tzinfo = python_datetime.tzinfo
    if tzinfo is None:
        timeZone = TimeZone(id=String("UTC"))
    else:
        timeZone = TimeZone(id=String(cast(pytz.BaseTzInfo, tzinfo).zone))

    return DateTime(
        date=convert_python_date_to_calflow_date(python_datetime.date()),
        time=convert_python_time_to_calflow_time(python_datetime.time()),
        timeZone=timeZone,
    )


def convert_time_to_datetime(time: datetime.time) -> datetime.datetime:
    return datetime.datetime(
        year=1,
        month=1,
        day=1,
        hour=time.hour,
        minute=time.minute,
        second=time.second,
        microsecond=time.microsecond,
    )
