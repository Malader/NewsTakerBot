from Database.Database import Database

from Repositories.IUserSubscriptionRepository import IUserSubscriptionRepository


class UserSubscriptionManager:
    def __init__(self, subscription_repository: IUserSubscriptionRepository):
        self.subscription_repository = subscription_repository
        self.default_channels = {"@vestiru24", "@rian_ru", "@SVO_ZOV_22", "@tsargradtv"}
        self.theme_emojis = {
            'Спорт': '🏀',
            'Политика': '🏛️',
            'СВО': '⚔️',
            'Экономика': '💹',
            'Наука': '🔬',
            'Технологии': '💻',
            'Культура': '🎨',
            'Здоровье': '💊',
            'Образование': '🎓'
        }

    def add_subscription(self, user_id, channel):
        """Добавление канала в подписки пользователя."""
        user_subscriptions = set(self.subscription_repository.get_user_channels(user_id))
        if channel not in user_subscriptions:
            user_subscriptions.add(channel)
            self.subscription_repository.add_user_channels(user_id, list(user_subscriptions))

    def remove_subscription(self, user_id, channel):
        """Удаление канала из подписок пользователя."""
        user_subscriptions = set(self.subscription_repository.get_user_channels(user_id))
        if channel in user_subscriptions:
            user_subscriptions.discard(channel)
            if user_subscriptions:
                # Если после удаления канала у пользователя ещё остались подписки, сохраняем изменения.
                self.subscription_repository.add_user_channels(user_id, list(user_subscriptions))
            else:
                # Если это был последний канал, удаляем запись пользователя из базы данных.
                self.subscription_repository.remove_user_channels(user_id)

    def get_user_subscriptions(self, user_id):
        """Получение списка подписок пользователя."""
        return set(self.subscription_repository.get_user_channels(user_id))

    def initialize_user_subscriptions(self, user_id):
        """Инициализация подписок для пользователя."""
        existing_subscriptions = set(self.subscription_repository.get_user_channels(user_id))
        if not existing_subscriptions:
            self.subscription_repository.add_user_channels(user_id, list(self.default_channels))
        return set(self.subscription_repository.get_user_channels(user_id))

    def add_user_interest(self, user_id, interest):
        """Добавление интереса пользователя."""
        current_interests = self.subscription_repository.get_user_interests(user_id)
        if interest not in current_interests:
            current_interests.append(interest)
            self.subscription_repository.add_user_interests(user_id, current_interests)

    def remove_user_interest(self, user_id, interest):
        """Удаление интереса пользователя."""
        current_interests = self.subscription_repository.get_user_interests(user_id)
        if interest in current_interests:
            current_interests.remove(interest)
            self.subscription_repository.add_user_interests(user_id, current_interests)

    def clear_user_interests(self, user_id):
        """Очищение всех интересов пользователя."""
        self.subscription_repository.clear_user_interests(user_id)

    def get_user_interests(self, user_id):
        """Получение списка интересов пользователя."""
        return self.subscription_repository.get_user_interests(user_id)

    def set_user_subscriptions(self, user_id, new_subscriptions):
        """Установка новых подписок для пользователя."""
        self.subscription_repository.add_user_channels(user_id, list(new_subscriptions))


# Использование UserInterestManager с Database
db_file = 'tgbotdatabase.sqlite'
database = Database(db_file)
user_subscription_manager = UserSubscriptionManager(database)
