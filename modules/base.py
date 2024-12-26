from abc import ABC, abstractmethod

class BaseNotificationModule(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Отправить уведомление. Возвращает True, если отправка успешна, иначе False."""
        pass
