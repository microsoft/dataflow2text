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
