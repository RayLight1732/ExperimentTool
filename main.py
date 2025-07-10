from pathlib import Path
from network.tcp_server import TCPServer
from network.data.data_decoder import DecodedData
from network.data.image_data import IMAGE_DATA_TYPE, ImageDataDecoder
from step.initial_step import InitialStepFactory
from step.ssq_step import SSQStepFactory
from step.unity_step import UnityStepFactory
from PIL import ExifTags
import queue
import ctypes
import tkinter as tk
import argparse
import yaml
from gui import MainWindow, StepManager


def on_receive(queue: queue.Queue, decodedData: DecodedData):
    if decodedData.get_name() == IMAGE_DATA_TYPE:
        image = decodedData.get_data()

        exif = image._getexif()

        # Orientationタグを探す
        if exif is not None:
            for tag, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag)
                if tag_name == "Orientation":
                    orientation = value
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        queue.put(image)
    else:
        print(f"Recieve {decodedData.get_name()}")


# ---------------------
# main
# ---------------------
def main(working_dir: Path):
    decoder = ImageDataDecoder()
    q = queue.Queue(0)
    server = TCPServer(decoder, lambda data: on_receive(q, data), port=51234)
    server.start_server()

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        pass

    root = tk.Tk()
    root.geometry("800x600")
    root.title("実験フロー")

    data_container = {}

    name_step_factory = InitialStepFactory(data_container)
    before_ssq_factory = SSQStepFactory(working_dir, data_container, q, "before")
    unity_step_factory = UnityStepFactory(data_container)
    after_ssq_factory = SSQStepFactory(working_dir, data_container, q, "after")
    factories = [
        name_step_factory.create,
        before_ssq_factory.create,
        unity_step_factory.create,
        after_ssq_factory.create,
    ]

    manager = StepManager(factories)
    window = MainWindow(
        root,
        on_press_next=manager.next_step,
        on_press_return_first=lambda: manager.show_step(0),
    )
    manager.main_window = window
    manager.show_step(0)

    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YAMLからworking_dirを取得")
    parser.add_argument(
        "yaml_path",
        nargs="?",
        default="settings.yaml",
        help="設定ファイル (デフォルト: settings.yaml)",
    )

    args = parser.parse_args()
    try:
        with open(args.yaml_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print("config file does not exist.")
        exit(1)

    # working_dir を取得
    working_dir = config.get("working_dir")
    main(Path(working_dir))
