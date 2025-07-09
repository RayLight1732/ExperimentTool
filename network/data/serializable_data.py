from abc import ABC, abstractmethod


class SerializableData(ABC):
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

    @abstractmethod
    def name(self) -> str:
        pass
