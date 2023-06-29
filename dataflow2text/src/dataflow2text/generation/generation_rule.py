import typing
from dataclasses import dataclass
from importlib import import_module
from inspect import getmembers
from pkgutil import walk_packages
from typing import Callable, Dict, Iterator, List, Optional, Set

from dataflow2text.dataflow.function import BaseFunction
from dataflow2text.dataflow.type_name import TypeName
from dataflow2text.generation.generation_symbol import GenerationNonterminal
from dataflow2text.generation.name_transformer import NameTransformer, parse_expression
from dataflow2text.generation.template import (
    LexicalVariants,
    Template,
    expand_lexical_variants,
)
from dataflow2text.generation.template_factory import TemplateFactory
from dataflow2text.generation.template_part import (
    TemplateNonterminal,
    TemplatePart,
    TemplateTerminal,
)


@dataclass(frozen=True)
class ComputationMatcher:
    # The type matcher. None means `Any`.
    typ: Optional[TypeName]
    # The body of the matcher.
    body: Callable[[BaseFunction], Optional[Dict[str, BaseFunction]]]

    def match(self, computation: BaseFunction) -> Optional[Dict[str, BaseFunction]]:
        # Need to use `return_type` instead of `reveal_type` so that the body can safely assume that the value of the
        # computation is not an `ExecutionError`.
        if self.typ is not None and computation.return_type != self.typ:
            return None

        return self.body(computation)  # type: ignore


@dataclass(frozen=True)
class GenerationRule:
    # The name of the rule.
    name: str
    # The act of the rule.
    act: str
    # The computation matcher of the rule.
    matcher: ComputationMatcher
    # The template associated with the rule.
    template: Template

    def match(self, nt: GenerationNonterminal) -> Optional[Dict[str, BaseFunction]]:
        if nt.act != self.act:
            return None

        # Currently, we do not check whether the returned bindings are consistent with
        # the `self.template`.
        return self.matcher.match(nt.computation)

    def expand(self, nt: GenerationNonterminal) -> Optional[Template]:
        bindings = self.match(nt)
        if bindings is None:
            return None

        new_bindings = {}
        if bindings is not None:
            new_bindings = {
                key: parse_expression(computation.__repr__())
                for key, computation in bindings.items()
            }
        transformer = NameTransformer(new_bindings)

        parts: List[TemplatePart] = [
            _expand_template_part(part, transformer) for part in self.template.parts
        ]
        return Template(parts)


def _expand_template_part(
    part: TemplatePart, transformer: NameTransformer
) -> TemplatePart:
    if isinstance(part, TemplateTerminal):
        return part

    if isinstance(part, TemplateNonterminal):
        return part.expand(transformer)

    if isinstance(part, LexicalVariants):
        variant: Template
        new_variants = []
        for variant in part.variants:
            new_variant = Template(
                [_expand_template_part(p, transformer) for p in variant.parts]
            )
            new_variants.append(new_variant)
        return LexicalVariants(new_variants)

    raise ValueError(f"Unexpected TemplatePart: {part}")


def generation(act, typ=None, template=None):
    """A decorator to convert a function to a GenerationRule."""

    assert template is not None

    template_ = TemplateFactory.parse(template)

    def wrapper(func):
        return GenerationRule(
            name=f"{func.__module__}.{func.__qualname__}",
            act=act,
            matcher=ComputationMatcher(
                typ=typ,
                body=func,
            ),
            template=template_,
        )

    return wrapper


def get_generation_rules(package) -> List[GenerationRule]:
    return sum(
        [_expand_lexical_variants(rule) for rule in _get_raw_generation_rules(package)],
        [],
    )


def _get_raw_generation_rules(package) -> Iterator[GenerationRule]:
    seen_rule_names: Set[str] = set()
    for _, module_name, _ in walk_packages(
        package.__path__, prefix=package.__name__ + "."
    ):
        module = import_module(module_name)
        for _, member in getmembers(module):
            if isinstance(member, GenerationRule):
                if member.name in seen_rule_names:
                    continue
                seen_rule_names.add(member.name)
                yield member


def _expand_lexical_variants(root_rule: GenerationRule) -> typing.List[GenerationRule]:
    if not any(isinstance(p, LexicalVariants) for p in root_rule.template.parts):
        return [root_rule]

    templates = expand_lexical_variants(root_rule.template, [])
    return [
        GenerationRule(
            name=f"{root_rule.name}.{idx}",
            act=root_rule.act,
            matcher=root_rule.matcher,
            template=template,
        )
        for idx, template in enumerate(templates)
    ]
