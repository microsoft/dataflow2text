from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{ {GenerationAct.PP.value} [constraint] }}",
)
def pp_handle_event_start_constraint(c: BaseFunction[Constraint[Event]]):
    match c:
        case EventExt.start_constraint(constraint):
            return {"constraint": constraint}
