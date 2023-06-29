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
