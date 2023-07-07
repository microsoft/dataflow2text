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
from dataflow2text.dataflow.schema import Long
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.time import Time


@function
def NumberAM(number: Long) -> Time:
    return Time(hour=number)


@function
def NumberPM(number: Long) -> Time:
    if number.inner == 12:
        return Time(hour=number)
    return Time(hour=Long(number.inner + 12))


@function
def ConvertTimeToAM(time: Time) -> Time:
    if time.hour.inner < 12:
        return time

    return Time(
        hour=Long(time.hour.inner - 12),
        minute=time.minute,
        second=time.second,
        nanosecond=time.nanosecond,
    )


@function
def ConvertTimeToPM(time: Time) -> Time:
    if time.hour.inner >= 12:
        return time

    return Time(
        hour=Long(time.hour.inner + 12),
        minute=time.minute,
        second=time.second,
        nanosecond=time.nanosecond,
    )


@function
def HourMinuteAm(hours: Long, minutes: Long) -> Time:
    return Time(hour=hours, minute=minutes)


@function
def HourMinutePm(hours: Long, minutes: Long) -> Time:
    if hours.inner == 12:
        return Time(hour=hours, minute=minutes)
    return Time(hour=Long(hours.inner + 12), minute=minutes)


@function
def HourMilitary(hours: Long) -> Time:
    return Time(hour=hours)


@function
def HourMinuteMilitary(hours: Long, minutes: Long) -> Time:
    return Time(hour=hours, minute=minutes)


@function
def Brunch() -> Time:
    return Time(hour=Long(10))


@function
def Lunch() -> Time:
    return Time(hour=Long(12))


@function
def Noon() -> Time:
    return Time(hour=Long(12))


@function
def EndOfWorkDay() -> Time:
    return Time(hour=Long(17))


@function
def adjustByDuration(time: Time, duration: Duration) -> Time:
    raise NotImplementedError()
