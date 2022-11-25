from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
DYNAMIC: StateVariableType
STATIC: StateVariableType

class Atom(_message.Message):
    __slots__ = ["boolean", "float", "int", "symbol"]
    BOOLEAN_FIELD_NUMBER: _ClassVar[int]
    FLOAT_FIELD_NUMBER: _ClassVar[int]
    INT_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    boolean: bool
    float: float
    int: int
    symbol: str
    def __init__(self, symbol: _Optional[str] = ..., int: _Optional[int] = ..., float: _Optional[float] = ..., boolean: bool = ...) -> None: ...

class CommandAccepted(_message.Message):
    __slots__ = ["command_id"]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    command_id: int
    def __init__(self, command_id: _Optional[int] = ...) -> None: ...

class CommandCancelRequest(_message.Message):
    __slots__ = ["command_id"]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    command_id: int
    def __init__(self, command_id: _Optional[int] = ...) -> None: ...

class CommandCancelled(_message.Message):
    __slots__ = ["command_id", "result"]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    command_id: int
    result: bool
    def __init__(self, command_id: _Optional[int] = ..., result: bool = ...) -> None: ...

class CommandExecutionRequest(_message.Message):
    __slots__ = ["arguments", "command_id"]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    arguments: _containers.RepeatedCompositeFieldContainer[Expression]
    command_id: int
    def __init__(self, arguments: _Optional[_Iterable[_Union[Expression, _Mapping]]] = ..., command_id: _Optional[int] = ...) -> None: ...

class CommandProgress(_message.Message):
    __slots__ = ["command_id", "progress"]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    command_id: int
    progress: float
    def __init__(self, command_id: _Optional[int] = ..., progress: _Optional[float] = ...) -> None: ...

class CommandRejected(_message.Message):
    __slots__ = ["command_id"]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    command_id: int
    def __init__(self, command_id: _Optional[int] = ...) -> None: ...

class CommandRequest(_message.Message):
    __slots__ = ["cancel", "execution"]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_FIELD_NUMBER: _ClassVar[int]
    cancel: CommandCancelRequest
    execution: CommandExecutionRequest
    def __init__(self, execution: _Optional[_Union[CommandExecutionRequest, _Mapping]] = ..., cancel: _Optional[_Union[CommandCancelRequest, _Mapping]] = ...) -> None: ...

class CommandResponse(_message.Message):
    __slots__ = ["accepted", "cancelled", "progress", "rejected", "result"]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    accepted: CommandAccepted
    cancelled: CommandCancelled
    progress: CommandProgress
    rejected: CommandRejected
    result: CommandResult
    def __init__(self, accepted: _Optional[_Union[CommandAccepted, _Mapping]] = ..., rejected: _Optional[_Union[CommandRejected, _Mapping]] = ..., progress: _Optional[_Union[CommandProgress, _Mapping]] = ..., result: _Optional[_Union[CommandResult, _Mapping]] = ..., cancelled: _Optional[_Union[CommandCancelled, _Mapping]] = ...) -> None: ...

class CommandResult(_message.Message):
    __slots__ = ["command_id", "result"]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    command_id: int
    result: bool
    def __init__(self, command_id: _Optional[int] = ..., result: bool = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ["instance"]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    instance: Instance
    def __init__(self, instance: _Optional[_Union[Instance, _Mapping]] = ...) -> None: ...

class Expression(_message.Message):
    __slots__ = ["atom", "list"]
    ATOM_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    atom: Atom
    list: _containers.RepeatedCompositeFieldContainer[Expression]
    def __init__(self, atom: _Optional[_Union[Atom, _Mapping]] = ..., list: _Optional[_Iterable[_Union[Expression, _Mapping]]] = ...) -> None: ...

class InitGetUpdate(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Instance(_message.Message):
    __slots__ = ["object", "type"]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    object: str
    type: str
    def __init__(self, type: _Optional[str] = ..., object: _Optional[str] = ...) -> None: ...

class PlatformUpdate(_message.Message):
    __slots__ = ["event", "state"]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    event: Event
    state: StateUpdate
    def __init__(self, state: _Optional[_Union[StateUpdate, _Mapping]] = ..., event: _Optional[_Union[Event, _Mapping]] = ...) -> None: ...

class StateUpdate(_message.Message):
    __slots__ = ["state_variables"]
    STATE_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    state_variables: _containers.RepeatedCompositeFieldContainer[StateVariable]
    def __init__(self, state_variables: _Optional[_Iterable[_Union[StateVariable, _Mapping]]] = ...) -> None: ...

class StateVariable(_message.Message):
    __slots__ = ["parameters", "state_function", "type", "value"]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    STATE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    parameters: _containers.RepeatedCompositeFieldContainer[Atom]
    state_function: str
    type: StateVariableType
    value: Expression
    def __init__(self, type: _Optional[_Union[StateVariableType, str]] = ..., state_function: _Optional[str] = ..., parameters: _Optional[_Iterable[_Union[Atom, _Mapping]]] = ..., value: _Optional[_Union[Expression, _Mapping]] = ...) -> None: ...

class StateVariableType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
