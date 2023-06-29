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
