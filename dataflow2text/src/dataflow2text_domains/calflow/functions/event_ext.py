from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Boolean, List, String
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.date_time import DateTime
from dataflow2text_domains.calflow.schemas.duration import Duration
from dataflow2text_domains.calflow.schemas.event import Event
from dataflow2text_domains.calflow.schemas.event_id import EventId
from dataflow2text_domains.calflow.schemas.location_keyphrase import LocationKeyphrase
from dataflow2text_domains.calflow.schemas.recipient import Recipient
from dataflow2text_domains.calflow.schemas.response_status import ResponseStatus
from dataflow2text_domains.calflow.schemas.sensitivity import Sensitivity
from dataflow2text_domains.calflow.schemas.show_as_status import ShowAsStatus


class EventExt:
    @staticmethod
    @function
    def id_constraint(
        # pylint: disable=redefined-builtin
        id: Constraint[EventId],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return id.allows(ev.id)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def subject_constraint(subject: Constraint[String]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return subject.allows(ev.subject)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    def created_constraint(created: Constraint[DateTime]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return created.allows(ev.created)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    def lastModified_constraint(
        lastModified: Constraint[DateTime],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return lastModified.allows(ev.lastModified)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def start_constraint(start: Constraint[DateTime]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return start.allows(ev.start)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def end_constraint(end: Constraint[DateTime]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return end.allows(ev.end)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def location_constraint(
        location: Constraint[LocationKeyphrase],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            if ev.location.inner is None:
                return False
            return location.allows(ev.location.inner)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def isAllDay_constraint(isAllDay: Constraint[Boolean]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return isAllDay.allows(ev.isAllDay)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def isCancelled_constraint(isCancelled: Constraint[Boolean]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return isCancelled.allows(ev.isCancelled)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def allowNewTimeProposals_constraint(
        allowNewTimeProposals: Constraint[Boolean],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return allowNewTimeProposals.allows(ev.allowNewTimeProposals)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def isOrganizer_constraint(isOrganizer: Constraint[Boolean]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return isOrganizer.allows(ev.isOrganizer)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def showAs_constraint(showAs: Constraint[ShowAsStatus]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return showAs.allows(ev.showAs)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def responseRequested_constraint(
        responseRequested: Constraint[Boolean],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return responseRequested.allows(ev.responseRequested)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def responseStatus_constraint(
        responseStatus: Constraint[ResponseStatus],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return responseStatus.allows(ev.responseStatus)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def organizer_constraint(organizer: Constraint[Recipient]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return organizer.allows(ev.organizer)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def attendees_constraint(
        attendee: Constraint[List[Attendee]],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return attendee.allows(ev.attendees)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def sensitivity_constraint(
        sensitivity: Constraint[Sensitivity],
    ) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return sensitivity.allows(ev.sensitivity)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def duration_constraint(duration: Constraint[Duration]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return duration.allows(ev.duration)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)

    @staticmethod
    @function
    def isOneOnOne_constraint(isOneOnOne: Constraint[Boolean]) -> Constraint[Event]:
        def predicate(ev: Event) -> bool:
            return isOneOnOne.allows(ev.isOneOnOne)

        return Constraint(type_arg=Event.dtype_ctor(), underlying=predicate)
