from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class BufferItem(ABC):
    result: Any

    @abstractmethod
    def done(self):
        return True
