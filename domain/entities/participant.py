from dataclasses import dataclass, field
from domain.entities.session import Session


@dataclass
class Participant:
    id: str
    name: str
    sessions: list[Session] = field(default_factory=list)
