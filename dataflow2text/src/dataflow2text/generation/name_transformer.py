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

import ast
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class NameTransformer(ast.NodeTransformer):
    """An AST transformer that replaces all Name nodes whose ID matches a given name with a
    different AST expression.

    This is used when expanding nonterminals in generation templates: e.g. if a nonterminal has an expression like `x +
    y`, where `x` and `y` are names bound to AST expressions in the plan, this transformer will replace `x` and `y` by
    the replacement expressions provided to it.
    """

    replacements: Dict[str, ast.expr]

    def visit_Name(self, node: ast.Name):
        if node.id in self.replacements:
            return self.replacements[node.id]
        else:
            return node


def parse_expression(expression: str) -> ast.expr:
    return ast.parse(expression, mode="eval").body  # type: ignore
