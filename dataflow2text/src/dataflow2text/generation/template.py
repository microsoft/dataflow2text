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

import typing
from dataclasses import dataclass
from typing import List

from more_itertools import before_and_after

from dataflow2text.generation.template_part import TemplatePart


@dataclass(frozen=True)
class Template:
    """A template in the generation grammar."""

    parts: List[TemplatePart]


@dataclass(frozen=True)
class LexicalVariants(TemplatePart):
    variants: List[Template]


def expand_lexical_variants(
    suffix: Template, prefix: List[TemplatePart]
) -> List[Template]:
    it_before_parts, it_after_parts = before_and_after(
        lambda part: not isinstance(part, LexicalVariants),
        suffix.parts,
    )

    # It is important to consume the `it_before_parts` before `it_after_parts`. See docstring in `before_and_after`.
    before_parts: List[TemplatePart] = list(it_before_parts)
    after_parts: List[TemplatePart] = list(it_after_parts)

    if not after_parts:
        return [Template(prefix + suffix.parts)]

    expanded_templates = []

    new_prefix = prefix + before_parts
    current_part: LexicalVariants = typing.cast(LexicalVariants, after_parts[0])
    for variant in current_part.variants:
        new_suffix = Template(variant.parts + after_parts[1:])
        new_templates = expand_lexical_variants(new_suffix, new_prefix)
        expanded_templates.extend(new_templates)

    return expanded_templates
