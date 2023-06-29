from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_DAY_OF_WEEK
from dataflow2text_domains.calflow.schemas.day_of_week import DayOfWeek


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Monday")
def np_monday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Monday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Tuesday")
def np_tuesday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Tuesday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Wednesday")
def np_wednesday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Wednesday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Thursday")
def np_thursday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Thursday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Friday")
def np_friday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Friday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Saturday")
def np_saturday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Saturday():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_DAY_OF_WEEK, template="Sunday")
def np_sunday(c: BaseFunction):
    if c.__value__ == DayOfWeek.Sunday():
        return {}
    return None
