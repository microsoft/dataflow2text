from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.functions.fence import FenceConditional
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_UNIT


@generation(
    act=DEFAULT_ACT,
    typ=DTYPE_UNIT,
    template="I can only do one action at a time. If you separate your requests, I can help you.",
)
def handle_fence_conditional(c: BaseFunction):
    match c:
        case FenceConditional():
            return {}
