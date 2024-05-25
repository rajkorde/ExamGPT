from dataclasses import dataclass
from enum import Enum
from typing import Callable

# simple pub sub event system


@dataclass
class EventParameters:
    exam_id: str
    source_id: str


class EventName(Enum):
    SOURCE_ADDED = (1,)
    CHUNKING_COMPLETE = 2


EventHandler = Callable[[EventParameters], None]

subscribers: dict[EventName, list[EventHandler]] = {}


def subscribe(event_name: EventName, handler: EventHandler) -> None:
    if event_name not in subscribers:
        subscribers[event_name] = []
    subscribers[event_name].append(handler)


def post_event(event_name: EventName, parameters: EventParameters) -> None:
    if event_name not in subscribers:
        return
    for handler in subscribers[event_name]:
        handler(parameters)
