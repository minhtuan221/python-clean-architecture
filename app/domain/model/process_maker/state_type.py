from dataclasses import dataclass


@dataclass
class StateType:
    start: str = 'start'  # the first state, also mean it's draft
    normal: str = 'normal'   # normal state
    complete: str = 'complete'  # it's done, cannot change state anymore
    denied: str = 'denied'  # it's done, cannot change state anymore
