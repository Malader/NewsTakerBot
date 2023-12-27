from abc import ABC, abstractmethod


class AbstractNewsFetcher(ABC):
    @abstractmethod
    def fetch_telegram_channel_messages(self, user_id):
        pass
