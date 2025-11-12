from dataclasses import dataclass
from domain.entities.participant import Participant
from domain.entities.cooling_condition import CoolingCondition
from typing import Optional
from datetime import datetime


@dataclass
class Session:
    cooling_condition: CoolingCondition
    started_at: Optional[datetime] = None
