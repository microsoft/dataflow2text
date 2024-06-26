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

# pylint: disable=no-self-use
from typing import Any, List, Tuple, Union, cast

import importlib_resources
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedEOF  # type: ignore[attr-defined]

from clamp.parser.macro import Macro
from clamp.parser.rule import PlanRule, Rule, SyncRule, UtteranceRule, mirrored_rule
from clamp.parser.token import (
    EmptyToken,
    MacroToken,
    NonterminalToken,
    OptionableSCFGToken,
    RegexToken,
    SCFGToken,
    TerminalToken,
)
from clamp.parser.types import Expansion


def parse_string(parser: Lark, string: str) -> Any:  # -> Union[Rule, Macro]:
    """
    Parse a string into a Rule or an Expansion.

    We annotate the return type as Any because this can return a Rule, Macro, or Expansion, and
    it seems silly to do a cast at each call site.
    """
    try:
        return TreeToRule().transform(parser.parse(string))
    except UnexpectedEOF as e:
        raise Exception(f"Line could not be parsed: {string}") from e


class TreeToRule(Transformer):
    @v_args(inline=True)
    def start(self, arg) -> Union[Macro, Rule]:
        return arg

    @v_args(inline=True)
    def start_for_test(self, arg) -> Union[Macro, Expansion, Rule]:
        return arg

    @v_args(inline=True)
    def terminal(self, underlying) -> TerminalToken:
        return TerminalToken(underlying.value, optional=False)

    @v_args(inline=True)
    def optional_terminal(self, underlying) -> TerminalToken:
        return TerminalToken(underlying.value, optional=True)

    @v_args(inline=True)
    def nonterminal(self, name_token) -> NonterminalToken:
        return NonterminalToken(name_token.value, optional=False)

    @v_args(inline=True)
    def optional_nonterminal(self, name_token) -> NonterminalToken:
        return NonterminalToken(name_token.value, optional=True)

    @v_args(inline=True)
    def empty(self) -> EmptyToken:
        return EmptyToken()

    @v_args(inline=True)
    def regex(self, arg) -> RegexToken:
        return RegexToken(arg.value, optional=False, prefix="")

    def plan_expansion(self, args) -> Expansion:
        return tuple(args)

    def utterance_expansion(self, args) -> Expansion:
        return tuple(args)

    def utterance_expansions(self, no_macro_expansions) -> Tuple[Expansion, ...]:
        return tuple(no_macro_expansions)

    @v_args(inline=True)
    def token(self, arg: SCFGToken) -> SCFGToken:
        return arg

    @v_args(inline=True)
    def rule(self, name_token) -> str:
        return name_token.value

    @v_args(inline=True)
    def sync_rule(
        self, lhs: str, expansions: List[Expansion], expansion: Expansion
    ) -> SyncRule:
        return SyncRule(lhs=lhs, utterance_rhss=tuple(expansions), plan_rhs=expansion)

    @v_args(inline=True)
    def mirrored_rule(self, lhs: str, rhs: Expansion) -> SyncRule:
        return mirrored_rule(lhs, rhs)

    @v_args(inline=True)
    def utterance_rule(self, rule, expansions) -> UtteranceRule:
        return UtteranceRule(rule, tuple(expansions))

    @v_args(inline=True)
    def macro_rule(self, macro_def, expansion) -> Macro:
        return Macro(macro_def[0], macro_def[1], expansion)

    def macro_def(self, args) -> Tuple[str, Tuple[str, ...]]:
        return cast(str, args[0].value), tuple(cast(str, a.value) for a in args[1:])

    def macro_apply(self, args) -> MacroToken:
        return MacroToken(args[0].value, tuple(args[1:]))


def get_scfg_parser(start_symbol: str = "start") -> Lark:
    """
    Get a parser based on the SCFG grammar. The start rule that gets appended to the grammar
    at the end depends on whether we are testing or not. If we are testing, then we want to be
    able to parse expansions outside of rules so that in our tests, we don't have to write
    lists of tokens.
    """
    with importlib_resources.files(__package__).joinpath(
        "scfg_grammar.lark"
    ).open() as cf_grammar_file:
        scfg_grammar = cf_grammar_file.read()

    # Type ignoring because mypy doesn't play well with Lark.
    return Lark(scfg_grammar, ambiguity="explicit", start=start_symbol)  # type: ignore


# RENDERING


def render_token(token: SCFGToken) -> str:
    if isinstance(token, EmptyToken):
        return "#e"
    elif isinstance(token, OptionableSCFGToken):
        optional_str = "?" if token.optional else ""
        value = token.lark_value if isinstance(token, RegexToken) else token.value
        return value + optional_str
    else:
        assert isinstance(token, MacroToken)
        return token.value


def render_expansion(rhs: Expansion) -> str:
    return " ".join(render_token(t) for t in rhs)


def render_expansions(expansions: Tuple[Expansion, ...]):
    return " | ".join(render_expansion(rhs) for rhs in expansions)


def render_rule(rule: Union[Rule, Macro]) -> str:
    if isinstance(rule, Macro):
        arg_str = f"({', '.join(rule.args)})" if rule.args else ""
        return f"{rule.name}{arg_str} 2> {render_expansion(rule.expansion)}"
    elif isinstance(rule, PlanRule):
        return f"{rule.lhs} 2> {render_expansion(rule.rhs)}"
    elif isinstance(rule, UtteranceRule):
        return f"{rule.lhs} 1> {render_expansions(rule.utterance_rhss)}"
    else:
        assert isinstance(rule, SyncRule)
        return f"{rule.lhs} -> {render_expansions(rule.utterance_rhss)} , {render_expansion(rule.plan_rhs)}"
