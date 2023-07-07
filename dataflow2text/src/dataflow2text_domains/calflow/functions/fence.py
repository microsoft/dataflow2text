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
from dataflow2text.dataflow.schema import Unit


@function
def FenceAggregation() -> Unit:
    return Unit()


@function
def FenceAttendee() -> Unit:
    return Unit()


@function
def FenceComparison() -> Unit:
    return Unit()


@function
def FenceConditional() -> Unit:
    return Unit()


@function
def FenceConferenceRoom() -> Unit:
    return Unit()


@function
def FenceDateTime() -> Unit:
    return Unit()


@function
def FenceGibberish() -> Unit:
    return Unit()


@function
def FenceMultiAction() -> Unit:
    return Unit()


@function
def FenceNavigation() -> Unit:
    return Unit()


@function
def FenceOther() -> Unit:
    return Unit()


@function
def FencePeopleQa() -> Unit:
    return Unit()


@function
def FencePlaces() -> Unit:
    return Unit()


@function
def FenceRecurring() -> Unit:
    return Unit()


@function
def FenceReminder() -> Unit:
    return Unit()


@function
def FenceScope() -> Unit:
    return Unit()


@function
def FenceSpecify() -> Unit:
    return Unit()


@function
def FenceSwitchTabs() -> Unit:
    return Unit()


@function
def FenceTeams() -> Unit:
    return Unit()


@function
def FenceTriviaQa() -> Unit:
    return Unit()


@function
def FenceWeather() -> Unit:
    return Unit()
