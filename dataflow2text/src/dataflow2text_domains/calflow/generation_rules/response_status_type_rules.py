from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.attendee_utils import (
    AttendeeFromEvent,
    AttendeeResponseStatus,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_RESPONSE_STATUS_TYPE,
)
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template=(
        "{{ You | you }} have "
        f"{{ {GenerationAct.VBN.value} [response] }} "
        f"the {{ {GenerationAct.NP.value} [event] }} invitation."
    ),
)
def say_you_have_responded_to_event(c):
    match c:
        case GetAttr(
            StructAttribute("response", _),
            GetAttr(
                StructAttribute("responseStatus", _),
                event,
            ),
        ) as response:
            return {
                "response": response,
                "event": event,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template=(
        f"{{ {GenerationAct.NP.value} [recipient] }} "
        "{{ have | has }} "
        f"{{ {GenerationAct.VBN.value} [response] }} "
        f"the {{ {GenerationAct.NP.value} [event] }} invitation."
    ),
)
def say_recipient_have_responded_to_event(c):
    match c:
        case GetAttr(
            StructAttribute("response", _),
            AttendeeResponseStatus(AttendeeFromEvent(event, recipient)),
        ) as response:
            return {
                "recipient": recipient,
                "response": response,
                "event": event,
            }


@generation(
    act=GenerationAct.VBN.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="accepted",
)
def vbn_say_accepted(c: BaseFunction):
    if c.__value__ == ResponseStatusType.Accepted():
        return {}
    return None


@generation(
    act=GenerationAct.VBN.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="declined",
)
def vbn_say_declined(c: BaseFunction):
    if c.__value__ == ResponseStatusType.Declined():
        return {}
    return None


@generation(
    # The POS tag of the head word "accepted" is `VBN`, hence we use it as the act.
    act=GenerationAct.VBN.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="tentatively accepted",
)
def vbn_say_tentatively_accepted(c: BaseFunction):
    if c.__value__ == ResponseStatusType.TentativelyAccepted():
        return {}
    return None


@generation(
    act=GenerationAct.VBN.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="not responded to",
)
def vb_say_not_responded_to(c: BaseFunction):
    if c.__value__ == ResponseStatusType.NotResponded():
        return {}
    return None


@generation(
    act=GenerationAct.VB.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="accept",
)
def vb_say_accept(c: BaseFunction):
    if c.__value__ == ResponseStatusType.Accepted():
        return {}
    return None


@generation(
    act=GenerationAct.VB.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="decline",
)
def vb_say_decline(c: BaseFunction):
    if c.__value__ == ResponseStatusType.Declined():
        return {}
    return None


@generation(
    act=GenerationAct.VB.value,
    typ=DTYPE_RESPONSE_STATUS_TYPE,
    template="tentatively accept",
)
def vb_say_tentatively_accept(c: BaseFunction):
    if c.__value__ == ResponseStatusType.TentativelyAccepted():
        return {}
    return None
