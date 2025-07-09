from pathlib import Path


def get_save_dir(working_dir: Path, data_container):
    return working_dir / str(data_container["condition"]) / data_container["name"]


def get_file_name(data_container):
    return data_container["timestamp"]
