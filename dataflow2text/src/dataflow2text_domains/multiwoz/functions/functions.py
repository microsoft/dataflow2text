from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import List, String, Unit
from dataflow2text_domains.calflow.schemas.path import Path
from dataflow2text_domains.multiwoz.schemas.schemas import MultiwozResult


@function
def Inform(result: MultiwozResult) -> Unit:
    return Unit()


@function
def General(action: String) -> Unit:
    return Unit()


@function
def Request(paths: List[Path]) -> Unit:
    return Unit()


@function
def OfferBooked(domain: String, paths: List[Path]) -> Unit:
    return Unit()
