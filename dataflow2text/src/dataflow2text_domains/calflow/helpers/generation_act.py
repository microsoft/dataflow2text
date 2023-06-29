from enum import Enum


class GenerationAct(Enum):
    # noun phrase
    NP = "NP"
    # prepositional phrase
    PP = "PP"
    # subordinate clause
    SBAR = "SBAR"
    # verb (including all tenses}
    VB = "VB"
    # verb, past particle
    VBN = "VBN"
    # interjection
    UH = "UH"

    Copula = "Copula"
    Ordinal = "Ordinal"
