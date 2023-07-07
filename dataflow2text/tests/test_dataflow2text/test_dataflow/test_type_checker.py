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

import pytest

from dataflow2text.dataflow.function import GetAttr, ValueCtor
from dataflow2text.dataflow.schema import List, Number, String, StructAttribute
from dataflow2text.dataflow.type_checker import TypeMismatchError, validate_type
from test_dataflow2text.test_dataflow.examples import (
    EXAMPLE_SCHEMA_LIBRARY,
    ExampleStruct,
    add,
    size,
)


def test_value_ctor():
    computation1 = ValueCtor(Number(1.0))
    validate_type(computation1, EXAMPLE_SCHEMA_LIBRARY)

    computation2 = ValueCtor(String("foo"))
    validate_type(computation2, EXAMPLE_SCHEMA_LIBRARY)

    computation3 = ValueCtor(List(Number.dtype_ctor(), [String("foo")]))
    validate_type(computation3, EXAMPLE_SCHEMA_LIBRARY)


def test_get_attr():
    computation1 = GetAttr(
        StructAttribute("x", String.dtype_ctor()),
        ValueCtor(ExampleStruct(String("foo"), Number(1.0))),
    )
    validate_type(computation1, EXAMPLE_SCHEMA_LIBRARY)

    computation2 = GetAttr(
        StructAttribute("x", Number.dtype_ctor()),
        ValueCtor(ExampleStruct(String("foo"), Number(1.0))),
    )
    with pytest.raises(TypeMismatchError):
        validate_type(computation2, EXAMPLE_SCHEMA_LIBRARY)

    computation3 = GetAttr(
        StructAttribute("x", List.dtype_ctor(String.dtype_ctor())),
        ValueCtor(
            ExampleStruct(List(String.dtype_ctor(), [String("foo")]), Number(1.0))
        ),
    )
    validate_type(computation3, EXAMPLE_SCHEMA_LIBRARY)


def test_simple_should_succeed():
    computation = add(ValueCtor(Number(1.0)), ValueCtor(Number(2.0)))
    validate_type(computation, EXAMPLE_SCHEMA_LIBRARY)


def test_simple_should_fail():
    computation = add(ValueCtor(Number(1.0)), ValueCtor(String("foo")))

    with pytest.raises(TypeMismatchError):
        validate_type(computation, EXAMPLE_SCHEMA_LIBRARY)


def test_with_type_arg():
    number_dtype = Number.dtype_ctor()
    computation1 = size(ValueCtor(List(number_dtype, [Number(1.0)])))
    validate_type(computation1, EXAMPLE_SCHEMA_LIBRARY)

    lnumber_dtype = List.dtype_ctor(number_dtype)
    computation2 = size(
        ValueCtor(List(lnumber_dtype, [List(number_dtype, [Number(1.0)])]))
    )

    validate_type(computation2, EXAMPLE_SCHEMA_LIBRARY)
