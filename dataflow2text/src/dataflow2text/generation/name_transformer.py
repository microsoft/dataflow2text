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
