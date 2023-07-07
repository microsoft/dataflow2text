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

# pylint: disable=used-before-assignment
from typing import cast

import pytest

from dataflow2text.dataflow.function import BaseFunction, ExecutionError, ValueCtor
from dataflow2text.dataflow.schema import List, Long, Number, PrimitiveSchema, String
from dataflow2text.dataflow.type_name import TypeName
from test_dataflow2text.test_dataflow import examples
from test_dataflow2text.test_dataflow.examples import (
    ExampleColor,
    ExampleStruct,
    add,
    identity,
    singleton,
)


def unreachable():
    raise RuntimeError("Should not be reached!")


def test_match_simple():
    plan = add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0)))

    match plan:
        case add(x, y):  # type: ignore
            assert x.__value__ == Number(1.0)
            assert y.__value__ == Number(2.0)
        case _:
            unreachable()


def test_match_with_reentrancy():
    def assert_matches(c: BaseFunction):
        match c:
            case add(x, y) if x is y:  # type: ignore
                assert x is one
                assert y is one
            case _:
                unreachable()

    one = ValueCtor(Number(1.0))
    another_one = ValueCtor(Number(1.0))
    assert_matches(add(one, one))

    with pytest.raises(RuntimeError, match="Should not be reached!"):
        assert_matches(add(one, another_one))


def test_match_via_type_simple():
    plan = add(
        add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0))), ValueCtor(Number(3.0))
    )

    match plan:
        case add(x, y) if x.return_type == Number.dtype_ctor():  # type: ignore
            assert x == add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0)))
            assert y.__value__ == Number(3.0)
        case _:
            unreachable()


def test_match_via_type_with_type_arg():
    number_dtype = Number.dtype_ctor()
    lnumber_dtype = List.dtype_ctor(number_dtype)
    plan = singleton(
        singleton(ValueCtor(List(lnumber_dtype, [List(number_dtype, [Number(1.0)])])))
    )

    match plan:
        case singleton(singleton(_) as z) if z.return_type == lnumber_dtype:  # type: ignore
            assert isinstance(z.__value__, List)
            assert z.__value__.type_arg == number_dtype
            assert z.__value__.inner == [Number(1.0)]
        case _:
            unreachable()


def test_match_via_type_struct():
    plan = ValueCtor(ExampleStruct(Long(1), String("foo")))

    match plan:
        case ValueCtor(ExampleStruct(Long(1), y)):  # type: ignore
            assert y == String("foo")
        case _:
            unreachable()


def test_match_via_value():
    plan = add(
        add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0))), ValueCtor(Number(3.0))
    )

    match plan:
        case add(x, y) if x.__value__ == Number(3.0):  # type: ignore
            assert x == add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0)))
            assert y.__value__ == Number(3.0)
        case _:
            unreachable()


def test_match_with_enum():
    plan = identity(ValueCtor(ExampleColor.Blue()))
    match plan:
        case identity(x) if x.return_type == TypeName("ExampleColor"):  # type: ignore
            x = cast(BaseFunction, x)
            value = cast(PrimitiveSchema, x.__value__)
            assert examples.ExampleColor(value.inner) == examples.ExampleColor.Blue()
        case _:
            unreachable()


def test_match_via_error():
    plan = add(
        singleton(ValueCtor(List(Number.dtype_ctor(), []))), ValueCtor(Number(2.0))
    )

    match (plan, plan.__value__):
        case (add(singleton(_), y), ExecutionError(inner, provenance)) if (
            isinstance(inner, examples.EmptyListError)
        ):
            assert provenance == [
                singleton(ValueCtor(List(Number.dtype_ctor(), []))),
                plan,
            ]
            assert y.__value__ == Number(2.0)
        case _:
            unreachable()
