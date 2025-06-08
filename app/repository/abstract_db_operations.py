from abc import ABC, abstractmethod
from typing import Any


class AbstractDBOperations(ABC):
    @abstractmethod
    def create(self, data: Any) -> Any:
        """Create a new record in the database."""
        pass

    @abstractmethod
    def get(self, query: Any) -> Any:
        """Read or retrieve records from the database."""
        pass

    @abstractmethod
    def delete(self, identifier: Any) -> Any:
        """Delete a record from the database."""
        pass
