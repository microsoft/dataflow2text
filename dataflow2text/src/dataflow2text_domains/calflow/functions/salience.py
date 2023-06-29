from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import TSchema, Unit
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension


@function
def makeSalient(intension: CalflowIntension[TSchema]) -> Unit:
    """Marks the `intension` as salient."""
    return Unit()
