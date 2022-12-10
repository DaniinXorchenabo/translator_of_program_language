from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class BufferItem(ABC):
    result: Any

    @abstractmethod
    def done(self):
        return True

    def __repr__(self):
        if isinstance(self.result, (list, tuple)):
            return f"{self.__class__.__name__}({''.join(str(i.name) for i in self.result)})"
        return f"{self.__class__.__name__}({self.result.name})"
