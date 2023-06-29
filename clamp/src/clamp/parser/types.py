from typing import Tuple

from clamp.parser.token import SCFGToken

Nonterminal = str
# An Alias is just another name for a nonterminal.
Alias = str


Expansion = Tuple[SCFGToken, ...]
