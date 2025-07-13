import cv2

aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)


def arGenerator(id: int, size: int):
    fileName = f"aruco_{id}.png"
    generator = aruco.generateImageMarker(dictionary, id, size)
    cv2.imwrite(fileName, generator)


if __name__ == "__main__":
    for i in range(8):
        arGenerator(i, 150)
