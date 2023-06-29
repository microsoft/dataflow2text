from dataflow2text.dataflow.function import StringCtor
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    EqualConstraint,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_LOCATION_KEYPHRASE,
)


@generation(
    act=GenerationAct.PP.value,
    typ=DTYPE_CONSTRAINT_LOCATION_KEYPHRASE,
    template="{{ in | at | _ }} {{ the | _ }} [name]",
)
def handle_equal_constraint(c):
    match c:
        case EqualConstraint(reference):
            return {
                "reference": reference,
                "name": StringCtor(reference.__value__.inner),
            }
