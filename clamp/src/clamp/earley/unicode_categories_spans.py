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

"""Provides data about which Unicode characters belong to which general category.

The concept is explained here:
- https://www.unicode.org/reports/tr44/#General_Category_Values
- https://en.wikipedia.org/wiki/Unicode_character_property#General_Category

unicode_categories.json was created by translating
https://raw.githubusercontent.com/rust-lang/regex/258bdf798a14f50529c1665e84cc8a3a9e2c90fc/regex-syntax/src/unicode_tables/general_category.rs
"""
import functools
import json
from typing import Dict, List

import importlib_resources

from clamp.util.span import Span, SpanSet


@functools.lru_cache(maxsize=None)
def raw_data() -> Dict[str, List[List[int]]]:
    with importlib_resources.files(__package__).joinpath(
        "unicode_categories.json"
    ).open() as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def category_to_span_set(name: str) -> SpanSet:
    """Returns the SpanSet for the category name.

    The SpanSet contains the Unicode code points for the corresponding general category.
    Only long names with underscores (e.g. "Letter", "Cased_Letter") are accepted."""

    return SpanSet(Span(x, y) for x, y in raw_data()[name])
