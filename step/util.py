from pathlib import Path
from typing import Optional


def get_name(data_container):
    return data_container["name"]


def get_save_dir_from_container(working_dir: Path, data_container: dict):
    condition = data_container["condition"]
    name = get_name(data_container)
    return get_save_dir(working_dir, condition, name)


def get_save_dir(working_dir: Path, condition: int, name: str):
    mode = get_mode(condition)
    position = get_position(condition)
    return working_dir / mode / position / name


def get_timestamp(data_container):
    return data_container["timestamp"]


def list_condition() -> list[int]:
    result = []
    result.append(0)
    for mode in range(len(MODE)):
        if mode != MODE_NEVER:
            for position in range(len(POSITIONS)):
                if position != POSITION_NONE:
                    result.append(calc_condition(mode, position))
    return result


POSITIONS = ["なし", "首筋", "頸動脈"]


def get_position_number(position: Optional[str]) -> int:
    """
    デフォルトは0を返す
    """
    if position is None:
        return POSITION_NONE
    try:
        return POSITIONS.index(position)
    except ValueError:
        return POSITION_NONE


MODE = ["なし", "酔いやすい場面のみ", "常時", "周期的", "常時_強"]


def get_mode_number(mode: Optional[str]) -> int:
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


def calc_condition(mode: int, position: int) -> int:
    return (position << 4 & 0b00110000) + (mode & 0b00001111)


def get_mode(condition: int) -> str:
    return MODE[condition & 0b00001111]


def get_position(condition: int) -> str:
    return POSITIONS[condition >> 4 & 0b00000011]
