from dataflow2text.dataflow.function import GetAttr
from dataflow2text.dataflow.schema import StructAttribute
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_OPTION_LOCATION_KEYPHRASE,
    get_inner_from_option,
    get_start_from_event,
)


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_OPTION_LOCATION_KEYPHRASE,
    template=(
        "{{ The | the }} event "
        f"{{ {GenerationAct.PP.value} [event] }} "
        f"{{ {GenerationAct.Copula.value} [start] }} "
        f"{{{{ located {{ {GenerationAct.PP.value} [location] }} | a {{ {GenerationAct.NP.value} [location] }} }}}}."
    ),
)
def say_event_location(c):
    match c:
        case GetAttr(
            StructAttribute("location", _),
            event,
        ) as location:
            return {
                "event": event,
                "start": get_start_from_event(event),
                "location": get_inner_from_option(location),
            }
