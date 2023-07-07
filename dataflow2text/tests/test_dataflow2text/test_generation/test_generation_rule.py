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

from dataflow2text.dataflow.function import ValueCtor
from dataflow2text.dataflow.schema import List, Number, String
from dataflow2text.generation.constants import DEFAULT_ACT, TOSTRING_ACT
from dataflow2text.generation.generation_symbol import GenerationNonterminal
from dataflow2text.generation.template import LexicalVariants, Template
from dataflow2text.generation.template_part import TemplateNonterminal, TemplateTerminal
from test_dataflow2text.test_dataflow.examples import ExampleStruct, add, head
from test_dataflow2text.test_generation.example_rules import (
    say_add,
    say_first_string,
    say_hello_or_hi,
    say_struct_y,
)


def test_match_say_add():
    rule = say_add
    assert rule.act == DEFAULT_ACT
    assert rule.matcher.typ is None

    x = ValueCtor(Number(1.0))
    y = ValueCtor(Number(2.0))
    plan = add(x, y)

    result = rule.match(GenerationNonterminal(DEFAULT_ACT, plan))
    assert result == {
        "x": x,
        "y": y,
        "z": plan,
    }

    # should not match when act is different
    assert rule.match(GenerationNonterminal("NP", plan)) is None


def test_match_say_first_string():
    rule = say_first_string
    assert rule.act == DEFAULT_ACT
    assert rule.matcher.typ == String.dtype_ctor()

    plan = head(ValueCtor(List(String.dtype_ctor(), [String("foo")])))
    result = rule.match(GenerationNonterminal(DEFAULT_ACT, plan))
    assert result == {"x": plan}

    # should not match when type is different
    assert (
        rule.match(
            GenerationNonterminal(
                DEFAULT_ACT, head(ValueCtor(List(Number.dtype_ctor(), [Number(1.0)])))
            ),
        )
        is None
    )


def test_expand_say_add():
    plan = add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0)))
    result = say_add.expand(GenerationNonterminal(DEFAULT_ACT, plan))
    assert result == Template(
        [
            TemplateTerminal("The result of "),
            TemplateNonterminal(TOSTRING_ACT, "ValueCtor(inner=Number(inner=1.0))"),
            TemplateTerminal(" plus "),
            TemplateNonterminal(TOSTRING_ACT, "ValueCtor(inner=Number(inner=2.0))"),
            TemplateTerminal(" is "),
            TemplateNonterminal(
                TOSTRING_ACT,
                "add(x=ValueCtor(inner=Number(inner=1.0)), y=ValueCtor(inner=Number(inner=2.0)))",
            ),
            TemplateTerminal("."),
        ]
    )


def test_expand_say_struct_y():
    result = say_struct_y.expand(
        GenerationNonterminal(
            DEFAULT_ACT,
            ValueCtor(ExampleStruct(String("foo"), Number(1.0))),
        ),
    )
    assert result == Template(
        [
            TemplateTerminal("The field y is "),
            TemplateNonterminal(TOSTRING_ACT, "ValueCtor(inner=Number(inner=1.0))"),
            TemplateTerminal("."),
        ]
    )


def test_expand_say_hello_or_hi():
    result = say_hello_or_hi.expand(
        GenerationNonterminal(DEFAULT_ACT, ValueCtor(String("foo")))
    )
    assert result == Template(
        [
            LexicalVariants(
                [
                    Template(
                        [
                            TemplateTerminal("Hello "),
                            TemplateNonterminal(
                                TOSTRING_ACT, "ValueCtor(inner=String(inner='foo'))"
                            ),
                        ]
                    ),
                    Template(
                        [
                            TemplateTerminal("Hi "),
                            TemplateNonterminal(
                                TOSTRING_ACT, "ValueCtor(inner=String(inner='foo'))"
                            ),
                        ]
                    ),
                ]
            )
        ]
    )
