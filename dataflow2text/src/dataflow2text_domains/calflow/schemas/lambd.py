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

# The filename is `lambd.py` since `lambda.py` is not allowed.
from dataclasses import dataclass
from typing import Callable, Generic, Tuple, TypeVar

from dataflow2text.dataflow.schema import BaseSchema
from dataflow2text.dataflow.type_name import TypeName

_TInput = TypeVar("_TInput", bound=BaseSchema)
_TOutput = TypeVar("_TOutput", bound=BaseSchema)


@dataclass
class Lambda(Generic[_TInput, _TOutput], BaseSchema):
    """The schema for single-arg lambdas.

    Cannot use `@dataclass(frozen=True)` because the type of `underlying` is Callable.
    See https://github.com/python/mypy/issues/5485#issuecomment-512168565
    """

    type_args: Tuple[TypeName, TypeName]
    underlying: Callable[[_TInput], _TOutput]

    def apply(self, value: _TInput) -> _TOutput:
        return self.underlying(value)

    @property
    def dtype(self) -> TypeName:
        return self.dtype_ctor(*self.type_args)
