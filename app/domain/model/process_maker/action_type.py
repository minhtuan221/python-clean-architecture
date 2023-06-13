from dataclasses import dataclass


@dataclass
class ActionType:
    """
    Approve: The actioner is suggesting that the request should move to the next state.
    Deny: The actioner is suggesting that the request should move to the previous state.
    Cancel: The actioner is suggesting that the request should move to the Cancelled state in the process.
    Restart: The actioner suggesting that the request be moved back to the Start state in the process.
    Resolve: The actioner is suggesting that the request be moved all the way to the Completed state."""
    start: str = 'start'  # the request is just sent to approval
    approve: str = 'approve'  # done by approval, the request cannot be change anymore
    cancel: str = 'cancel'  # done by requester, who send the request
    reject: str = 'reject'  # return to requester but can be change and re-submit
    deny: str = 'deny'  # done by approval, the request cannot be change anymore
    restart: str = 'restart'  # done by approval, the request is sent back to make change
    resolve: str = 'resolve'  # done by approval or requester, request is no longer needed
