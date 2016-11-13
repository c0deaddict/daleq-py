from abc import ABC, abstractmethod


class Store(ABC):
    @abstractmethod
    def get(self, fqid: list, key: str):
        pass

    @abstractmethod
    def set(self, fqid: list, key: str, value) -> bool:
        pass
