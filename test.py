from network.tcp_server import TCPServer
from network.data.image_data import ImageDataDecoder, IMAGE_DATA_TYPE
import time
from network.data.data_decoder import DecodedData
import cv2
from mark_seat_reader import CorrectionProcessor, Margin, MarkseatReader
import numpy as np

image = None


def on_receive(decodedData: DecodedData):
    global image
    if decodedData.get_name() == IMAGE_DATA_TYPE:
        image = decodedData.get_data()
    else:
        print(f"Recieve {decodedData.get_name()}")


if __name__ == "__main__":
    # decoder = MultiTypeDataDecoder({STRING_DATA_TYPE: StringDataDecoder()})
    decoder = ImageDataDecoder()
    server = TCPServer(decoder, on_receive, port=51234)
    server.start_server()
    try:
        while True:
            if image is not None:
                image.show(title=f"Image")
                processor = CorrectionProcessor(1000, 900)
                numpy_image = np.array(image)

                # RGB → BGR（OpenCV形式）
                opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

                corrected = processor.correct(opencv_image)
                if corrected is not None:
                    gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
                    rect_margin = Margin(230, 1110, 0, 10)
                    margin = Margin(15, 75, 75, 15)
                    reader = MarkseatReader(
                        rect_margin=rect_margin,
                        row=16,
                        col=4,
                        width=120,
                        height=60,
                        cell_margin=margin,
                    )

                    result = reader.read(gray)
                    for r in result:
                        print(r)
                else:
                    print("cannot find rect")
                image = None
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        server.stop_server()
