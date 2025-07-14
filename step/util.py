from pathlib import Path
from typing import Optional

def get_name(data_container):
    return data_container["name"]

def get_save_dir(working_dir: Path, data_container):
    condition = data_container["condition"]
    mode = get_mode(condition)
    position = get_position(condition)
    return working_dir / mode / position / get_name(data_container)


def get_timestamp(data_container):
    return data_container["timestamp"]

POSITIONS = ["なし","首筋", "頸動脈"]
def get_position_number(position:Optional[str])->int:
    """
    デフォルトは0を返す
    """
    if position is None:
        return POSITION_NONE
    try:
        return POSITIONS.index(position)
    except ValueError:
        return POSITION_NONE


MODE = ["なし","周期的","常時"]
def get_mode_number(mode:Optional[str])->int:
    """
    デフォルトは-1を返す
    """
    if mode is None:
        return -1
    try:
        return MODE.index(mode)
    except ValueError:
        return -1
POSITION_NONE = 0
MODE_NEVER = 0
def calc_condition(mode:int,position:int)->int:
    print(f"calc condition:{mode} {position}")
    return (position << 2 & 0b00001100) + (mode & 0b00000011)

def get_mode(condition:int) ->str:
    return MODE[condition  & 0b00000011]

def get_position(condition:int)->str:
    return POSITIONS[condition >> 2 & 0b00000011]