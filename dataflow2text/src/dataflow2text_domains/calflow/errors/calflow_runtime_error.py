class CalflowRuntimeError(RuntimeError):
    pass


class EmptyListError(CalflowRuntimeError):
    pass


class NonSingletonListError(CalflowRuntimeError):
    pass


class ListIndexTooLargeError(CalflowRuntimeError):
    def __init__(self, index: int):
        message = f"Index {index} points to after the end of list."
        super().__init__(message)


class EventNotFoundError(CalflowRuntimeError):
    def __init__(self, event_id: str):
        message = f"Cannot find event {event_id}."
        super().__init__(message)


class UpdateEventOrganizedByOtherUserError(CalflowRuntimeError):
    pass
