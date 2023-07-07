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

from dataflow2text.dataflow.schema import Dynamic, Long, String
from dataflow2text.dataflow.type_name import TypeName
from test_dataflow2text.test_dataflow.examples import ExampleColor, ExampleStruct


def test_dtype_ctor():
    assert String.dtype_ctor() == TypeName("String")
    with pytest.raises(ValueError):
        String.dtype_ctor(TypeName("String"))


def test_dynamic():
    expected_dtype = TypeName("Dynamic")
    assert Dynamic.dtype_ctor() == expected_dtype

    x = Dynamic(String.dtype_ctor(), String("foo"))
    assert x.dtype == expected_dtype
    assert x.inner.dtype == String.dtype_ctor()


def test_enum_value():
    expected_dtype = TypeName("ExampleColor")
    assert ExampleColor.dtype_ctor() == expected_dtype

    red = ExampleColor.Red()
    assert isinstance(red, ExampleColor)
    assert red.dtype == expected_dtype
    assert red.inner == "Red"

    blue = ExampleColor.Blue()
    assert isinstance(blue, ExampleColor)
    assert blue.dtype == expected_dtype
    assert blue.inner == "Blue"


def test_list_of_struct():
    one_foo = ExampleStruct(Long(1), String("foo"))
    assert one_foo.dtype == TypeName(
        "ExampleStruct", (TypeName("Long"), TypeName("String"))
    )
