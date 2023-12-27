from abc import ABC, abstractmethod


class IUserSubscriptionRepository(ABC):

    @abstractmethod
    def get_user_channels(self, user_id):
        """
        Получение списка каналов, на которые подписан пользователь.

        :param user_id: Идентификатор пользователя.
        :return: Список каналов пользователя.
        """
        pass

    @abstractmethod
    def add_user_channels(self, user_id, channels):
        """
        Добавление каналов в список подписок пользователя.

        :param user_id: Идентификатор пользователя.
        :param channels: Список каналов для добавления.
        """
        pass

    @abstractmethod
    def remove_user_channel(self, user_id, channel):
        """
        Удаление канала из списка подписок пользователя.

        :param user_id: Идентификатор пользователя.
        :param channel: Канал для удаления.
        """
        pass

    @abstractmethod
    def get_user_interests(self, user_id):
        """
        Получение списка интересов пользователя.

        :param user_id: Идентификатор пользователя.
        :return: Список интересов пользователя.
        """
        pass

    @abstractmethod
    def add_user_interests(self, user_id, interests):
        """
        Добавление интересов в список интересов пользователя.

        :param user_id: Идентификатор пользователя.
        :param interests: Список интересов для добавления.
        """
        pass

    @abstractmethod
    def remove_user_interest(self, user_id, interest):
        """
        Удаление интереса из списка интересов пользователя.

        :param user_id: Идентификатор пользователя.
        :param interest: Интерес для удаления.
        """
        pass

    @abstractmethod
    def clear_user_interests(self, user_id):
        """
        Очистка всех интересов пользователя.

        :param user_id: Идентификатор пользователя.
        """
        pass

    @abstractmethod
    def remove_user_channels(self, user_id):
        """Удаление всех каналов пользователя."""
        pass
