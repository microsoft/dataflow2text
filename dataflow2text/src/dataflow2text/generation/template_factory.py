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

from typing import List, Union, cast

from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node

from dataflow2text.generation.constants import TOSTRING_ACT
from dataflow2text.generation.template import LexicalVariants, Template
from dataflow2text.generation.template_part import (
    TemplateNonterminal,
    TemplatePart,
    TemplateTerminal,
)


class TemplateFactory:
    @staticmethod
    def parse(text: str) -> Template:
        tree = _TEMPLATE_GRAMMAR.parse(text)
        return TemplateVisitor().visit(tree)


# A simple PEG parser for generation templates. Supported syntax:
# - Nonterminals: {act [comp]}
# - toString nonterminals: [comp]
# - Lexical variants: {{ a | b | c }}
#
# where `comp` is some dataflow computation.
#
# Other syntax yet to be supported:
# - Force capitalization marker: ^
_TEMPLATE_GRAMMAR = Grammar(
    r"""
    template = (terminal / nonterminal / toString_nonterminal / variation)+ / ""
    variation =  "{{" ( variation_template "|" )+ variation_template "}}"
    variation_template = ( template / "_" )
    nonterminal = curly_open ws* act ws* square_open terminal square_close ws* curly_close
    toString_nonterminal = square_open terminal square_close
    terminal = ~"[^\[\]\{\}\|]+"
    act = ~"[A-Za-z_]+"
    curly_open = "{"
    curly_close = "}"
    square_open = "["
    square_close = "]"
    ws = ~"\s"
    """
)


class TemplateVisitor(NodeVisitor):
    """A NodeVisitor implementation that can traverse a tree parsed using the generation grammar and return the
    corresponding Template object.
    """

    @staticmethod
    def visit_template(node: Node, visited_children: List[List[TemplatePart]]):
        if len(node.text) == 0:
            return Template([TemplateTerminal("")])
        else:
            children: List[TemplatePart] = []
            for visited in visited_children:
                children.extend(visited)

            return Template(children)

    @staticmethod
    def visit_terminal(node: Node, visited_children):
        return TemplateTerminal(node.text)

    @staticmethod
    def visit_act(node: Node, visited_children):
        return node.text

    @staticmethod
    def visit_nonterminal(node: Node, visited_children):
        act = next(v for v in visited_children if isinstance(v, str))
        expression: TemplateTerminal = next(
            v for v in visited_children if isinstance(v, TemplateTerminal)
        )
        return TemplateNonterminal(act, expression.inner.strip())

    @staticmethod
    def visit_toString_nonterminal(node: Node, visited_children):
        _, expression, _ = visited_children
        return TemplateNonterminal(TOSTRING_ACT, expression.inner.strip())

    @staticmethod
    def visit_variation(node: Node, visited_children):
        variant_nodes: List[Union[Template, Node]]
        last_variant: Template
        _, variant_nodes, last_variant, _ = visited_children
        variants = [cast(Template, c) for c in variant_nodes if isinstance(c, Template)]
        variants.append(last_variant)
        return LexicalVariants(variants)

    @staticmethod
    def visit_variation_template(node: Node, visited_children):
        def _strip_start_terminal_whitespace(t: TemplatePart) -> TemplatePart:
            if isinstance(t, TemplateTerminal):
                return TemplateTerminal(cast(TemplateTerminal, t).inner.lstrip())
            else:
                return t

        def _strip_end_terminal_whitespace(t: TemplatePart) -> TemplatePart:
            if isinstance(t, TemplateTerminal):
                return TemplateTerminal(cast(TemplateTerminal, t).inner.rstrip())
            else:
                return t

        def _strip_trailing_variant_whitespace(template: Template):
            if (
                len(template.parts) > 0
                and isinstance(template.parts[0], TemplateTerminal)
                and len(cast(TemplateTerminal, template.parts[0]).inner) == 0
            ):
                template.parts.pop(0)
            if (
                len(template.parts) > 0
                and isinstance(template.parts[-1], TemplateTerminal)
                and len(cast(TemplateTerminal, template.parts[-1]).inner) == 0
            ):
                template.parts.pop(-1)

        def _strip_variant_whitespace(template: Template) -> Template:
            if len(template.parts) > 0:
                template.parts[0] = _strip_start_terminal_whitespace(template.parts[0])
                template.parts[-1] = _strip_end_terminal_whitespace(template.parts[-1])

            _strip_trailing_variant_whitespace(template)
            return template

        def _transform_empty_variant(template: Template) -> Template:
            if len(template.parts) == 1 and isinstance(
                template.parts[0], TemplateTerminal
            ):
                if cast(TemplateTerminal, template.parts[0]).inner == "_":
                    return Template([TemplateTerminal("")])
            return template

        return _transform_empty_variant(_strip_variant_whitespace(visited_children[0]))

    @staticmethod
    def generic_visit(node: Node, visited_children):
        if len(visited_children) > 0 and isinstance(visited_children[0], list):
            children = []
            for child in visited_children:
                children.extend(child)
            return children or node
        return visited_children or node
