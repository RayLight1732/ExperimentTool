from network.data.serializable_data import SerializableData
from network.data.data_decoder import DataDecoder, DecodedData
import socket
from PIL import Image
import io

IMAGE_DATA_TYPE = "ImageData"


class ImageDataDecoder(DataDecoder):
    def accept(self, sock: socket.socket) -> DecodedData:
        size_header = self._recv_all(sock, 4)
        size = int.from_bytes(size_header, byteorder="little")
        print(size)
        data = self._recv_all(sock, size)
        image = Image.open(io.BytesIO(data))
        print("decoded")
        return DecodedData(IMAGE_DATA_TYPE, image)
