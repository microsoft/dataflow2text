from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.generation.generation_rule import generation
from dataflow2text_domains.calflow.helpers.generation_act import GenerationAct
from dataflow2text_domains.calflow.helpers.generation_helpers import DTYPE_MONTH
from dataflow2text_domains.calflow.schemas.month import Month


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="January")
def np_january(c: BaseFunction):
    if c.__value__ == Month.January():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="February")
def np_feburary(c: BaseFunction):
    if c.__value__ == Month.February():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="March")
def np_march(c: BaseFunction):
    if c.__value__ == Month.March():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="April")
def np_april(c: BaseFunction):
    if c.__value__ == Month.April():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="May")
def np_may(c: BaseFunction):
    if c.__value__ == Month.May():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="June")
def np_june(c: BaseFunction):
    if c.__value__ == Month.June():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="July")
def np_july(c: BaseFunction):
    if c.__value__ == Month.July():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="August")
def np_august(c: BaseFunction):
    if c.__value__ == Month.August():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="September")
def np_september(c: BaseFunction):
    if c.__value__ == Month.September():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="October")
def np_october(c: BaseFunction):
    if c.__value__ == Month.October():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="November")
def np_november(c: BaseFunction):
    if c.__value__ == Month.November():
        return {}
    return None


@generation(act=GenerationAct.NP.value, typ=DTYPE_MONTH, template="December")
def np_december(c: BaseFunction):
    if c.__value__ == Month.December():
        return {}
    return None
