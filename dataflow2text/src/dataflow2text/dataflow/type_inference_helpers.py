import inspect
import typing
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Tuple, Type, Union

from dataflow2text.dataflow.schema import BaseSchema
from dataflow2text.dataflow.type_name import TypeName

TypeNameGetter = Callable[[TypeName], TypeName]
TypeNameGetterLookup = DefaultDict[Any, typing.List[Tuple[str, TypeNameGetter]]]
# pylint: disable=protected-access
TypeAnnotation = Union[Type[BaseSchema], typing._GenericAlias, typing.TypeVar]  # type: ignore


def type_annotation_contains_forward_ref(type_annotation) -> bool:
    if isinstance(type_annotation, str):
        return True

    if isinstance(type_annotation, typing.ForwardRef):
        return True

    # pylint: disable=protected-access
    if isinstance(type_annotation, typing._GenericAlias):  # type: ignore
        # TODO: Probably GenericAlias would never be ForwardRef?
        origin = typing.get_origin(type_annotation)
        return type_annotation_contains_forward_ref(origin) or any(
            (
                type_annotation_contains_forward_ref(arg)
                for arg in typing.get_args(type_annotation)
            )
        )
    if isinstance(type_annotation, typing.TypeVar):
        return False

    if inspect.isclass(type_annotation) and issubclass(type_annotation, BaseSchema):
        return False

    raise ValueError(
        f"Unexpected type annotation: {type_annotation} {type(type_annotation)}"
    )


def build_type_name_getters_lookup(
    signature: inspect.Signature,
) -> TypeNameGetterLookup:
    results: TypeNameGetterLookup = defaultdict(list)
    for _, param in signature.parameters.items():
        for type_annotation, getters in _build_type_name_getters_for_param(
            param
        ).items():
            results[type_annotation] += getters

    return results


def _build_type_name_getters_for_param(
    param: inspect.Parameter,
) -> TypeNameGetterLookup:
    results: TypeNameGetterLookup = defaultdict(list)
    results[param.annotation].append((param.name, lambda x: x))
    getters_lookup = _build_type_name_getters_for_type_annotation(
        param.annotation, lambda x: x
    )
    for type_arg, getters in getters_lookup.items():
        results[type_arg].append((param.name, getters[0]))
    return results


def _build_type_name_getters_for_type_annotation(
    type_annotation: TypeAnnotation, base_getter: TypeNameGetter
) -> DefaultDict[Any, typing.List[TypeNameGetter]]:
    results: DefaultDict[Any, typing.List[TypeNameGetter]] = defaultdict(list)
    if not hasattr(type_annotation, "__args__"):
        return results

    def build_getter_for_idx(idx_: int):
        def getter_(type_name: TypeName) -> TypeName:
            base_type_name = base_getter(type_name)
            type_args = base_type_name.type_args
            if idx_ >= len(type_args):
                # TODO: There is a bug when the type_name is a subclass of a generic schema.
                #  e.g., when `ActionIntensionConstraint[T]` is a subclass of `Constraint[CalflowIntension[T]]`,
                #  base_type_name is `Dynamic`, and type_args is empty.
                #  but type_annotation.__args__ is `T`.
                raise RuntimeError(
                    f"{type_annotation} {type_name} {base_type_name} {type_args} {idx_}"
                )
            return type_args[idx_]

        return getter_

    for idx, type_arg in enumerate(type_annotation.__args__):  # type: ignore
        getter = build_getter_for_idx(idx)

        # TODO: return if type_arg is not a TypeVar
        results[type_arg].append(getter)

        # recurse if type_arg has __args__
        for k, v in _build_type_name_getters_for_type_annotation(
            type_arg, getter
        ).items():
            results[k] += v

    return results
