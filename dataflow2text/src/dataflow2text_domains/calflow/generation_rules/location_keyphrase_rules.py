from dataflow2text.dataflow.function import BaseFunction, StringCtor
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import (
    DTYPE_LOCATION_KEYPHRASE,
)


@generation(
    act=GenerationAct.NP.value,
    typ=DTYPE_LOCATION_KEYPHRASE,
    template="[keyphrase]",
)
def np_say_location_keyphrase(c: BaseFunction):
    return {"keyphrase": StringCtor(c.__value__.inner)}
