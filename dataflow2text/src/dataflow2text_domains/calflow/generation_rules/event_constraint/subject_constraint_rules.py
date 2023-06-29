from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.constraint_utils import negate
from dataflow2text_domains.calflow.functions.event_ext import EventExt
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_EVENT,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        "{{ event | events }} {{ matching | named | _ }} "
        f"{{ {GenerationAct.NP.value} [constraint] }}"
    ),
)
def np_handle_event_subject_constraint(c: BaseFunction):
    match c:
        case EventExt.subject_constraint(constraint):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=(
        "{{ event | events }} not {{ matching | named | _ }} "
        f"{{ {GenerationAct.NP.value} [constraint] }}"
    ),
)
def np_handle_event_subject_constraint_with_negate(c):
    match c:
        case EventExt.subject_constraint(negate(constraint)):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"{{{{ matching | named | _ }}}} {{ {GenerationAct.NP.value} [constraint] }}",
)
def pp_handle_event_subject_constraint(c: BaseFunction):
    match c:
        case EventExt.subject_constraint(constraint):
            return {"constraint": constraint}


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_EVENT,
    template=f"not {{{{ matching | named | _ }}}} {{ {GenerationAct.NP.value} [constraint] }}",
)
def pp_handle_event_subject_constraint_with_negate(c: BaseFunction):
    match c:
        case EventExt.subject_constraint(negate(constraint)):
            return {"constraint": constraint}
