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
