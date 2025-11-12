from enum import Enum, auto
from dataclasses import dataclass


class CoolingMethod(Enum):
    NONE = auto()
    PERIODIC = auto()
    CONSTANT = auto()


class CoolingRegion(Enum):
    CAROTID = auto()
    OCCIPITAL = auto()


@dataclass
class CoolingCondition:
    method: CoolingMethod
    region: CoolingRegion
