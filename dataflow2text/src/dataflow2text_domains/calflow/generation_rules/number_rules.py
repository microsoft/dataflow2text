from dataflow2text.dataflow.function import BaseFunction, LongCtor
from dataflow2text.generation.constants import TOSTRING_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_NUMBER


@generation(act=TOSTRING_ACT, typ=DTYPE_NUMBER, template="[num]")
def number_to_long(c: BaseFunction):
    value = c.__value__.inner
    if int(value) == value:
        return {"num": LongCtor(int(value))}
    return None
