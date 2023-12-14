from collections import defaultdict


class SubscriptionManager:
    def __init__(self):
        self.user_subscriptions = {}  # Словарь для хранения подписок пользователей
        self.default_channels = {"@vestiru24", "@rian_ru", "@SVO_ZOV_22", "@tsargradtv"}  # Набор каналов по умолчанию
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
        self.user_interests = {}

    def add_subscription(self, user_id, channel):
        """Добавление канала в подписки пользователя."""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = self.default_channels.copy()
        self.user_subscriptions[user_id].add(channel)

    def remove_subscription(self, user_id, channel):
        """Удаление канала из подписок пользователя."""
        self.user_subscriptions.get(user_id, set()).discard(channel)

    def get_user_subscriptions(self, user_id):
        """Получение списка подписок пользователя."""
        return self.user_subscriptions.get(user_id, self.default_channels.copy())

    def initialize_user_subscriptions(self, user_id):
        """Инициализация подписок для нового пользователя."""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = self.default_channels.copy()
        elif not self.user_subscriptions[user_id]:
            # Здесь можно добавить логику для случаев, когда у пользователя нет подписок
            pass

    def add_interests(self, user_id, interests):
        self.user_interests[user_id] = interests

    def get_user_interests(self, user_id):
        # Инициализация интересов пользователя, если они еще не были инициализированы
        if user_id not in self.user_interests:
            self.user_interests[user_id] = set()  # или другое начальное значение
        return self.user_interests[user_id]

    def initialize_user_interests(self, user_id):
        if user_id not in self.user_interests:
            self.user_interests[user_id] = set()

    def is_user_subscribed_to_interest(self, user_id, interest):
        return interest in self.user_interests.get(user_id, [])

    def add_user_interest(self, user_id, interest):
        if user_id not in self.user_interests:
            self.user_interests[user_id] = set()  # Инициализация как множество

        # Добавляем интерес в множество
        self.user_interests[user_id].add(interest)

    def remove_user_interest(self, user_id, interest):
        # Здесь логика удаления интереса из подписок пользователя
        if interest in self.user_interests.get(user_id, []):
            self.user_interests[user_id].remove(interest)
            print(f"Интерес {interest} удален для пользователя {user_id}")
        else:
            print(f"Интерес {interest} не найден для пользователя {user_id}")

    def clear_user_interests(self, user_id):
        # Очищаем все интересы пользователя
        if user_id in self.user_interests:
            self.user_interests[user_id].clear()

    def get_user_subscriptions(self, user_id):
        # Возвращаем множество подписок для данного пользователя, если оно существует
        return self.user_subscriptions.get(user_id, set())

    def set_user_subscriptions(self, user_id, new_subscriptions):
        # Устанавливаем новое множество подписок для данного пользователя
        self.user_subscriptions[user_id] = new_subscriptions