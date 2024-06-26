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

from collections import defaultdict
from typing import DefaultDict, Iterator, List, Tuple

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.dataflow.library import Library
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text.generation.constants import DEFAULT_ACT
from dataflow2text.generation.dataflow_transducer import get_applicable_productions
from dataflow2text.generation.generation_rule import GenerationRule
from dataflow2text.generation.generation_symbol import GenerationNonterminal
from dataflow2text.generation.generation_tree import GenerationTree
from dataflow2text.generation.generation_tree_builder import GenerationTreeBuilder
from dataflow2text.generation.template import LexicalVariants


class SimpleGenerationParser:
    """A simple parser for the generation grammar.

    It is a top-down parser similar to nltk.parse.recursivedescent.RecursiveDescentParser.
    """

    def __init__(self, library: Library, rules: List[GenerationRule]):
        self._library = library

        self._rules_lookup: DefaultDict[
            Tuple[str, TypeName], List[GenerationRule]
        ] = defaultdict(list)

        rule: GenerationRule
        for rule in rules:
            # All LexicalVariants should have been expanded already.
            if any(isinstance(part, LexicalVariants) for part in rule.template.parts):
                raise ValueError(f"{rule.name} contains LexicalVariants.")
            self._rules_lookup[(rule.act, rule.matcher.typ)].append(rule)

    def parse(
        self,
        plan: BaseFunction,
        response: str,
    ) -> Iterator[GenerationTree]:
        builder = GenerationTreeBuilder(
            GenerationNonterminal(act=DEFAULT_ACT, computation=plan)
        )

        return self._expand_builder(
            builder=builder,
            plan=plan,
            response=response,
        )

    def _expand_builder(
        self,
        builder: GenerationTreeBuilder,
        plan: BaseFunction,
        response: str,
    ) -> Iterator[GenerationTree]:
        nt = builder.next_nonterminal()
        output = builder.get_output_string()

        if nt is None:
            if output == response:
                yield builder.tree

            else:
                # output does not match expected response
                pass

        elif not response.startswith(output):
            # prefix does not match expected response
            pass

        elif not response.endswith(builder.get_suffix_string()):
            # suffix does not match expected response
            pass

        else:
            yield from self._expand_nonterminal(
                nt,
                builder,
                plan,
                response,
            )

    def _expand_nonterminal(
        self,
        nt: GenerationNonterminal,
        builder: GenerationTreeBuilder,
        plan: BaseFunction,
        response: str,
    ) -> Iterator[GenerationTree]:
        for production in get_applicable_productions(
            nt, self._rules_lookup, self._library
        ):
            new_builder = builder.copy()
            new_builder.extend(production)
            yield from self._expand_builder(
                new_builder,
                plan,
                response,
            )
