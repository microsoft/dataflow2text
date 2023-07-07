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

# TODO: This file can be renamed to a better name.

import typing

from dataflow2text.dataflow.function_library import (
    BUILTIN_FUNCTION_LIBRARY,
    FunctionLibrary,
    get_functions,
)
from dataflow2text.dataflow.library import Library
from dataflow2text.dataflow.schema_library import (
    BUILTIN_SCHEMA_LIBRARY,
    SchemaLibrary,
    get_schemas,
)
from dataflow2text.generation.generation_rule import (
    GenerationRule,
    get_generation_rules,
)
from dataflow2text_domains.calflow import functions, generation_rules, schemas

CALFLOW_SCHEMA_LIBRARY = BUILTIN_SCHEMA_LIBRARY + SchemaLibrary(get_schemas(schemas))

# TODO: Class static methods are not be stored in the function library. We need to have a mechanism to deal with name
#  conflicts.
CALFLOW_FUNCTION_LIBRARY = BUILTIN_FUNCTION_LIBRARY + FunctionLibrary(
    get_functions(functions, schemas)
)

CALFLOW_LIBRARY = Library(CALFLOW_SCHEMA_LIBRARY, CALFLOW_FUNCTION_LIBRARY)

CALFLOW_GENERATION_RULES: typing.List[GenerationRule] = get_generation_rules(
    generation_rules
)
