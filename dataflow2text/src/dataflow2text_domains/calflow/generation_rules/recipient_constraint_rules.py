from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.person_utils import RecipientWithNameLike
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_CONSTRAINT_RECIPIENT,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_CONSTRAINT_RECIPIENT,
    template=f"{{ {GenerationAct.NP.value} [name] }}",
)
def np_handle_recipient_with_name_like(c: BaseFunction):
    match c:
        case RecipientWithNameLike(_, name):
            return {"name": name}
