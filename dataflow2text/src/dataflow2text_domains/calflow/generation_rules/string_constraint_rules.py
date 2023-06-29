from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.single_arg_constraints import (
    EqualConstraint,
    FuzzyEqualConstraint,
)
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_STRING,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_STRING,
    template='"{toString [name]}"',
)
def handle_fuzzy_equal_constraint(c: BaseFunction):
    match c:
        case FuzzyEqualConstraint(name):
            return {"name": name}


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_STRING,
    template='"{toString [name]}"',
)
def handle_equal_constraint(c: BaseFunction):
    match c:
        case EqualConstraint(name):
            return {"name": name}
