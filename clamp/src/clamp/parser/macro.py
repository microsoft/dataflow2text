# Copyright (c) 2023 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from clamp.parser.token import MacroToken, NonterminalToken, SCFGToken
from clamp.parser.types import Expansion


@dataclass(frozen=True)
class Macro:
    name: str
    args: Tuple[str, ...]
    expansion: Expansion

    def apply_expression(
        self, macro_rules: Dict[str, "Macro"], args_to_bind: List[Expansion]
    ) -> Expansion:
        """
        Apply this macro to the argument. Because all macros cannot use any variables outside of its definition,
        we do not need to pass in an environment.
        """
        result: List[SCFGToken] = []
        for token in self.expansion:
            result += eval_expression(
                macro_rules, token, dict(zip(self.args, args_to_bind))
            )
        return tuple(result)


def eval_expression(
    macros: Dict[str, Macro],
    token: SCFGToken,
    env: Optional[Dict[str, Expansion]] = None,
) -> Expansion:
    """
    Given a token, eval it.

    e.g. for macros defined as
    f(a) 2> "(" g(a) ")"
    g(b) 2> "(" b ")"
    h(c) 2> "(" c ")"

    given a macro call f(z),
    return "(" "(" z ")" ")"

    or a macro call g(h(z)),
    return "(" "(" z ")" ")"

    """
    env = env if env else {}
    if isinstance(token, MacroToken):
        args_to_bind = [eval_expression(macros, arg, env) for arg in token.args]
        macro = macros[token.name]
        return macro.apply_expression(macros, args_to_bind)
    elif isinstance(token, NonterminalToken) and token.value in env:
        return env[token.value]

    return (token,)


def expand_macros(macros: Dict[str, Macro], expansion: Expansion) -> Expansion:
    """
    Return a new rule where the plan_rhs has been rewritten with all macros expanded.
    """
    new_tokens: List[SCFGToken] = []
    for token in expansion:
        if isinstance(token, MacroToken):
            new_tokens += eval_expression(macros, token)
        else:
            new_tokens.append(cast(SCFGToken, token))

    return tuple(new_tokens)
