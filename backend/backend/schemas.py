from enum import Enum
from typing import Optional

from ninja import Schema


class UserRole(str, Enum):
    ADMIN = 'admin'
    TEAM = 'team'
    JURY = 'jury'
    ORGANIZER = 'organizer'


class StaffRole(str, Enum):
    JURY = 'jury'
    ORGANIZER = 'organizer'
    ADMIN = 'admin'


class TournamentStatus(str, Enum):
    DRAFT = 'draft'
    REGISTRATION = 'registration'
    RUNNING = 'running'
    FINISHED = 'finished'


class RoundStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    SUBMISSION_CLOSED = 'submission_closed'
    EVALUATED = 'evaluated'


class CalendarEventType(str, Enum):
    MEET = 'meet'
    EVENT = 'event'

class ErrorResponse(Schema):
    code: str
    message: str
    details: dict[str, list[str]] | None  = None
