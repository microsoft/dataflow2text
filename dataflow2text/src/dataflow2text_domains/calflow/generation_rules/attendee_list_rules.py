from dataflow2text.dataflow.function import BaseFunction, GetAttr, ListCtor
from dataflow2text.dataflow.schema import List, StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.attendees_utils import (
    AttendeesWithNotResponse,
    AttendeesWithResponse,
)
from dataflow2text_domains.calflow.functions.list_utils import head, last, tail
from dataflow2text_domains.calflow.functions.person_utils import CurrentUser
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_ATTENDEE,
    DTYPE_LIST_ATTENDEE,
)
from dataflow2text_domains.calflow.schemas.attendee import Attendee


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_LIST_ATTENDEE,
    template=f"There are no attendees {{ {GenerationAct.SBAR.value} [attendees] }}.",
)
def say_no_attendees(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case AttendeesWithResponse(
            GetAttr(
                StructAttribute("attendees", _),
                _event,
            ),
            _response,
        ) as attendees if len(attendees.__value__) == 0:
            return {"attendees": attendees}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_LIST_ATTENDEE,
    template=(
        f"Here is the list of attendees {{ {GenerationAct.SBAR.value} [attendees] }}: "
        f"{{ {GenerationAct.NP.value} [attendees] }}. "
        f"{{{{ {{ {DEFAULT_ACT} [lastAttendee] }} | _ }}}}"
    ),
)
def say_here_is_the_list_of_attendees_and_last_attendee(
    c: BaseFunction,
):
    match c:
        # pylint: disable=used-before-assignment
        case AttendeesWithResponse(
            GetAttr(
                StructAttribute("attendees", _),
                _event,
            ) as all_attendees,
            _response,
        ) as attendees if len(attendees.__value__) > 0:
            last_attendee: BaseFunction[Attendee] = last(all_attendees)
            return {
                "attendees": attendees,
                "lastAttendee": last_attendee,
            }

        case AttendeesWithNotResponse(
            GetAttr(
                StructAttribute("attendees", _),
                _event,
            ) as all_attendees,
            _response,
        ) as attendees if len(attendees.__value__) > 0:
            last_attendee: BaseFunction[Attendee] = last(all_attendees)
            return {"attendees": attendees, "lastAttendee": last_attendee}


@generation(
    act=GenerationAct.SBAR.value,
    typ=DTYPE_LIST_ATTENDEE,
    template=f"who {{{{ has | have }}}} {{ {GenerationAct.VBN.value} [response] }} {{ {GenerationAct.NP.value} [event] }}",
)
def say_attendees_with_response_to_event(c: BaseFunction):
    match c:
        case AttendeesWithResponse(
            GetAttr(
                StructAttribute("attendees", _),
                event,
            ),
            response,
        ):
            return {
                "response": response,
                "event": event,
            }


@generation(
    act=GenerationAct.SBAR.value,
    typ=DTYPE_LIST_ATTENDEE,
    template=(
        f"who {{{{ has | have }}}} "
        f"{{{{ responded to | not {{ {GenerationAct.VBN.value} [response] }} }}}} "
        f"{{ {GenerationAct.NP.value} [event] }}"
    ),
)
def say_attendees_with_not_response_to_event(c: BaseFunction):
    match c:
        case AttendeesWithNotResponse(
            GetAttr(
                StructAttribute("attendees", _),
                event,
            ),
            response,
        ):
            return {
                "response": response,
                "event": event,
            }


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_LIST_ATTENDEE,
    template=f"{{ {GenerationAct.NP.value} [remainingAttendees] }}",
)
def np_say_attendees_filter_current_user(attendees: BaseFunction[List[Attendee]]):
    value = [
        item
        for item in attendees.__value__.inner
        # TODO: We should not use displayName as the UID of person.
        if item.recipient.name != CurrentUser().__value__.displayName
    ]
    if len(value) == len(attendees.__value__.inner):
        return None
    remaining_attendees = ListCtor(DTYPE_ATTENDEE, value)
    return {"remainingAttendees": remaining_attendees}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_LIST_ATTENDEE,
    template=f"{{ {GenerationAct.NP.value} [firstAttendee] }}, {{ {GenerationAct.NP.value} [remainingAttendees] }}",
)
def np_say_multiple_attendees(attendees: BaseFunction[List[Attendee]]):
    if len(attendees.__value__) >= 3:
        return {
            "firstAttendee": head(attendees),
            "remainingAttendees": tail(attendees),
        }
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_LIST_ATTENDEE,
    template=(
        f"{{{{ {{ {GenerationAct.NP.value} [firstAttendee] }} | {{ {GenerationAct.NP.value} [firstAttendee] }}, }}}} "
        f"and {{ {GenerationAct.NP.value} [secondAttendee] }}"
    ),
)
def np_say_two_attendees(attendees: BaseFunction):
    if len(attendees.__value__) == 2:
        return {
            "firstAttendee": head(attendees),
            "secondAttendee": head(tail(attendees)),
        }
    return None


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_LIST_ATTENDEE,
    template=f"{{ {GenerationAct.NP.value} [firstAttendee] }}",
)
def np_say_single_attendee(attendees: BaseFunction):
    if len(attendees.__value__) == 1:
        return {
            "firstAttendee": head(attendees),
        }
    return None
