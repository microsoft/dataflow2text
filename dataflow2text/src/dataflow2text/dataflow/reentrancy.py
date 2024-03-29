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

import operator
from collections import defaultdict
from typing import DefaultDict, List, Tuple

from dataflow2text.dataflow.function import BaseFunction


def collect_maximum_spanning_reentrant_computations(
    computation: BaseFunction,
) -> List[BaseFunction]:
    """Returns all maximum-spanning reentrant sub-computations in the `computation`.

    Note if a computation is a maximum-spanning reentrant computation, none of its sub-computations would be a
    maximum-spanning reentrant computation.
    """
    counter: DefaultDict[int, int] = defaultdict(int)
    reentrant_computations = []

    def rec(c: BaseFunction):
        cid = id(c)
        counter[cid] += 1

        count = counter[cid]
        if count > 2:
            return

        if count == 2:
            reentrant_computations.append(c)
            return

        for _, arg_computation in c.args():
            rec(arg_computation)

    rec(computation)
    return reentrant_computations


def collect_reentrant_paths(
    computation: BaseFunction,
) -> DefaultDict[int, List[List[str]]]:
    """Returns the lookup of reentrant paths for each path in the `computation`."""
    reentrant_paths: DefaultDict[int, List[List[str]]] = defaultdict(list)

    def rec(prefix: List[str], c: BaseFunction):
        for arg_name, arg_computation in c.args():
            cid = id(arg_computation)
            path = prefix + [arg_name]
            reentrant_paths[cid].append(path)
            rec(path, arg_computation)

    rec([], computation)
    return reentrant_paths


def split_path_at_maximum_spanning_reentrant_point(
    old_computation: BaseFunction,
    path: List[str],
    reentrant_computations: List[BaseFunction],
) -> Tuple[BaseFunction, List[str], List[str]]:
    prefix = path[:]
    suffix: List[str] = []
    while prefix:
        c = operator.attrgetter(".".join(prefix))(old_computation)
        if c in reentrant_computations:
            return c, prefix, suffix[::-1]
        curr = prefix.pop()
        suffix.append(curr)
    # If reached here, it means that none of the super-computations is a reentrant computation.
    return old_computation, prefix, suffix[::-1]
