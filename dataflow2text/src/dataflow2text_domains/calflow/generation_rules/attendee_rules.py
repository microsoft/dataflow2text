from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_ATTENDEE,
    get_recipient_from_attendee,
)
from dataflow2text_domains.calflow.schemas.attendee import Attendee
from dataflow2text_domains.calflow.schemas.response_status_type import (
    ResponseStatusType,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_ATTENDEE,
    template=f"Unfortunately, {{ {GenerationAct.NP.value} [attendee] }} declined.",
)
def say_unfortunately_attendee_declined(c: BaseFunction[Attendee]):
    if c.__value__.status.response != ResponseStatusType.Declined():
        return None

    return {"attendee": c}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_ATTENDEE,
    template=f"{{ {GenerationAct.NP.value} [recipient] }}",
)
def np_say_recipient(c: BaseFunction[Attendee]):
    return {"recipient": get_recipient_from_attendee(c)}
