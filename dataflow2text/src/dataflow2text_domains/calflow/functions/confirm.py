from dataflow2text.dataflow.function import function
from dataflow2text.dataflow.schema import Dynamic, Unit
from dataflow2text_domains.calflow.schemas.calflow_intension import CalflowIntension
from dataflow2text_domains.calflow.schemas.constraint import Constraint
from dataflow2text_domains.calflow.schemas.event import Event


@function
def ConfirmAndReturnAction() -> CalflowIntension[Dynamic]:
    """Confirms an action that needs confirmation and then returns the root computation from salience."""

    # TODO: Currently holding a dummy `Unit`.
    return CalflowIntension(
        underlying=Dynamic(type_arg=Unit.dtype_ctor(), inner=Unit())
    )


@function
def ConfirmUpdateAndReturnActionIntension(
    constraint: Constraint[Event],
) -> CalflowIntension[Dynamic]:
    """Like `ConfirmAndReturnAction`, but for an update with `constraint`."""

    # TODO: Currently holding a dummy `Unit`.
    return CalflowIntension(
        underlying=Dynamic(type_arg=Unit.dtype_ctor(), inner=Unit())
    )
