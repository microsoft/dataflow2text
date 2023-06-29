from dataflow2text.dataflow.function import BaseFunction, StringCtor
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.event_utils import EventAttendance
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_ATTENDANCE_RESPONSE,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_ATTENDANCE_RESPONSE,
    template=(
        f"I will {{ {GenerationAct.VB.value} [response] }} {{ {GenerationAct.NP.value} [event] }} "
        'and send a response to the organizer with the following comment: "[comment]". '
        "Is that ok?"
    ),
)
def handle_event_attendance_with_comment(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case EventAttendance(
            event,
            response,
            comment,
            _,
        ) if comment.__value__.inner != "":
            return {
                "event": event,
                "comment": StringCtor(comment.__value__.inner),
                "response": response,
            }


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_ATTENDANCE_RESPONSE,
    template=(
        f"I will {{ {GenerationAct.VB.value} [response] }} {{ {GenerationAct.NP.value} [event] }}. "
        "Is that ok?"
    ),
)
def handle_event_attendance_without_comment(c: BaseFunction):
    match c:
        # pylint: disable=used-before-assignment
        case EventAttendance(
            event,
            response,
            comment,
            _,
        ) if comment.__value__.inner == "":
            return {
                "event": event,
                "comment": StringCtor(comment.__value__.inner),
                "response": response,
            }
