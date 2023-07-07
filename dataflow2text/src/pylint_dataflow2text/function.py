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
