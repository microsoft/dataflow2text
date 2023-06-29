from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [constraint] }}",
)
def pp_handle_event_location_constraint(c):
    match c:
        case EventExt.location_constraint(constraint):
            return {"constraint": constraint}
