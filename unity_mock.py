from network.tcp_server import TCPServer
from network.data.multi_type_data_decoder import MultiTypeDataDecoder
from network.data.string_data import StringDataDecoder,STRING_DATA_TYPE,StringData
from network.data.data_decoder import DecodedData

def on_receive(data:DecodedData):
    if data.get_name() == STRING_DATA_TYPE:
        print(data.get_data())

if __name__ == "__main__":
    decoder = MultiTypeDataDecoder({STRING_DATA_TYPE: StringDataDecoder()})
    server = TCPServer(decoder,on_receive,port=51234)
    server.start_server()
    try:
        while True:
            text = input("input text:")
            server.send_all(StringData(text))
    finally:
        server.stop_server()