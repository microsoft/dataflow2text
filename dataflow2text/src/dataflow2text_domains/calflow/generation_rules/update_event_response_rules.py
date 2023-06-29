from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.update import (
    UpdateCommitEventWrapper,
    UpdatePreflightEventWrapper,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_UPDATE_EVENT_RESPONSE,
    get_attendees_from_event,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_UPDATE_EVENT_RESPONSE,
    template=f"Here are some times when {{ {GenerationAct.NP.value} [attendees] }} are free.",
)
def handle_update_1(c: BaseFunction):
    match c:
        case UpdateCommitEventWrapper(
            UpdatePreflightEventWrapper(
                GetAttr(StructAttribute("id", _), event),
                _,
            )
        ):
            return {"attendees": get_attendees_from_event(event)}


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_UPDATE_EVENT_RESPONSE,
    template="Is this the change you want to make?",
)
def handle_update_2(c: BaseFunction):
    match c:
        case UpdateCommitEventWrapper(
            UpdatePreflightEventWrapper(
                GetAttr(StructAttribute("id", _), event),
                _,
            )
        ):
            return {"attendees": get_attendees_from_event(event)}
