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

from dataflow2text.dataflow.function import StringCtor
from dataflow2text.generation.generation_production import GenerationProduction
from dataflow2text.generation.generation_symbol import (
    GenerationNonterminal,
    GenerationTerminal,
)
from dataflow2text.generation.generation_tree import GenerationTree


def test_productions():
    dummy_computation = StringCtor("")

    # S
    #   NP
    #     TOSTRING "yes"
    #   SBAR
    #     PP
    #       TOSTRING "foo bar"
    #     NP
    #       TOSTRING "baz"
    production_root = GenerationProduction(
        name="r1",
        lhs=GenerationNonterminal(act="S", computation=dummy_computation),
        rhs=[
            GenerationNonterminal(act="NP", computation=dummy_computation),
            GenerationNonterminal(act="SBAR", computation=dummy_computation),
        ],
    )
    production_0 = GenerationProduction(
        name="r2",
        lhs=GenerationNonterminal(act="NP", computation=dummy_computation),
        rhs=[GenerationNonterminal(act="TOSTRING", computation=dummy_computation)],
    )
    production_0_0 = GenerationProduction(
        name="r3",
        lhs=GenerationNonterminal(act="TOSTRING", computation=dummy_computation),
        rhs=[GenerationTerminal(inner="yes")],
    )
    production_1 = GenerationProduction(
        name="r4",
        lhs=GenerationNonterminal(act="SBAR", computation=dummy_computation),
        rhs=[
            GenerationNonterminal(act="PP", computation=dummy_computation),
            GenerationNonterminal(act="NP", computation=dummy_computation),
        ],
    )
    production_1_0 = GenerationProduction(
        name="r5",
        lhs=GenerationNonterminal(act="PP", computation=dummy_computation),
        rhs=[GenerationNonterminal(act="TOSTRING", computation=dummy_computation)],
    )
    production_1_0_0 = GenerationProduction(
        name="r6",
        lhs=GenerationNonterminal(act="TOSTRING", computation=dummy_computation),
        rhs=[GenerationTerminal(inner="foo bar")],
    )
    production_1_1 = GenerationProduction(
        name="r7",
        lhs=GenerationNonterminal(act="NP", computation=dummy_computation),
        rhs=[GenerationNonterminal(act="TOSTRING", computation=dummy_computation)],
    )
    production_1_1_0 = GenerationProduction(
        name="r8",
        lhs=GenerationNonterminal(act="TOSTRING", computation=dummy_computation),
        rhs=[GenerationTerminal(inner="baz")],
    )
    tree = GenerationTree(
        label=production_root,
        children=[
            GenerationTree(
                label=production_0,
                children=[
                    GenerationTree(
                        label=production_0_0,
                        children=[],
                    )
                ],
            ),
            GenerationTree(
                label=production_1,
                children=[
                    GenerationTree(
                        label=production_1_0,
                        children=[
                            GenerationTree(
                                label=production_1_0_0,
                                children=[],
                            )
                        ],
                    ),
                    GenerationTree(
                        label=production_1_1,
                        children=[
                            GenerationTree(
                                label=production_1_1_0,
                                children=[],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )

    productions = tree.productions()

    expected_productions = [
        production_root,
        production_0,
        production_0_0,
        production_1,
        production_1_0,
        production_1_0_0,
        production_1_1,
        production_1_1_0,
    ]
    assert productions == expected_productions
