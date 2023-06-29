from dataflow2text.dataflow.function import BaseFunction, GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_RECIPIENT
from dataflow2text_domains.calflow.schemas.recipient import Recipient


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_RECIPIENT,
    # A more precise rule should choose between "is" and "are" based on the organizer.
    # We leave such decision to the model instead of hard-coded in the generation rules.
    template=(
        f"{{ {GenerationAct.NP.value} [organizer] }} "
        "{{ is | are }} the organizer of "
        f"{{ {GenerationAct.NP.value} [event] }}."
    ),
)
def say_event_organizer(c: BaseFunction[Recipient]):
    match c:
        case GetAttr(
            StructAttribute("organizer", _),
            event,
        ) as organizer:
            return {
                "event": event,
                "organizer": organizer,
            }
