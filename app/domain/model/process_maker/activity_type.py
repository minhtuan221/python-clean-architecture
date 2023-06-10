from dataclasses import dataclass


@dataclass
class ActivityType:
    """
    Add Note: Specifies that we should automatically add a note to a Request.
    Send Email: Specifies that we should email one or more recipients.
    Add Stakeholders: Specifies that we should add one or more persons as Stakeholders on this request.
    Remove Stakeholders: Specifies that we should remove one or more stakeholders from this request."""
    add_note: str = 'add_note'
    send_email: str = 'send_email'
    add_stakeholder: str = 'add_stakeholder'
    remove_stakeholder: str = 'remove_stakeholder'
