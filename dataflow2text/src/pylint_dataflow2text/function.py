from typing import TYPE_CHECKING

import astroid

if TYPE_CHECKING:
    from pylint.lint import PyLinter


def register(linter: "PyLinter") -> None:
    pass


COMPUTATION_TEMPLATE = """
from dataflow2text.dataflow.function import _BaseFunction
"""


def _decorated_by_computation(node: astroid.FunctionDef) -> bool:
    if not node.decorators:
        return False
    for decorator in node.decorators.nodes:
        if isinstance(decorator, (astroid.Call, astroid.Attribute)):
            continue
        if decorator.name == "function":
            return True
    return False


def _infer_computation(function_node: astroid.FunctionDef, context=None):
    klass = astroid.builder.extract_node(COMPUTATION_TEMPLATE)
    return klass.infer(context)


astroid.MANAGER.register_transform(
    astroid.FunctionDef,
    astroid.inference_tip(_infer_computation),
    _decorated_by_computation,
)
