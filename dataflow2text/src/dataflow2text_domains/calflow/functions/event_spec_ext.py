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
from dataflow2text.dataflow.schema import List, String
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.event_spec import EventSpec
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase


class EventSpecExt:
    @staticmethod
    @function
    def subject_constraint(obj: Constraint[String]) -> Constraint[EventSpec]:
        def predicate(ev: EventSpec) -> bool:
            return obj.allows(ev.subject)

        return Constraint(type_arg=EventSpec.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def start_constraint(obj: Constraint[DateTime]) -> Constraint[EventSpec]:
        def predicate(ev: EventSpec) -> bool:
            return obj.allows(ev.start)

        return Constraint(type_arg=EventSpec.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def end_constraint(obj: Constraint[DateTime]) -> Constraint[EventSpec]:
        def predicate(ev: EventSpec) -> bool:
            return obj.allows(ev.end)

        return Constraint(type_arg=EventSpec.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def location_constraint(
        obj: Constraint[LocationKeyphrase],
    ) -> Constraint[EventSpec]:
        def predicate(ev: EventSpec) -> bool:
            return obj.allows(ev.location)

        return Constraint(type_arg=EventSpec.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def attendees_constraint(
        obj: Constraint[List[Attendee]],
    ) -> Constraint[EventSpec]:
        def predicate(ev: EventSpec) -> bool:
            return obj.allows(ev.attendees)

        return Constraint(type_arg=EventSpec.dtype_ctor(), underlying=predicate)
