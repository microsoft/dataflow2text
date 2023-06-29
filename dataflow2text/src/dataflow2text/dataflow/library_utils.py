from typing import Callable, Dict, Iterable, TypeVar

_T = TypeVar("_T")


def safe_build_dict(
    items: Iterable[_T], key_getter: Callable[[_T], str]
) -> Dict[str, _T]:
    results: Dict[str, _T] = {}

    for item in items:
        key = key_getter(item)
        maybe_conflicted_item = results.get(key)
        if maybe_conflicted_item is not None and maybe_conflicted_item is not item:
            raise ValueError(f"Conflicted key for {item} and {maybe_conflicted_item}")
        results[key] = item

    return results
