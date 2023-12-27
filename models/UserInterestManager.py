from Repositories.IUserSubscriptionRepository import IUserSubscriptionRepository


class UserInterestManager:
    def __init__(self, interest_repository: IUserSubscriptionRepository, theme_emojis):
        self.interest_repository = interest_repository
        self.default_channels = {"@vestiru24", "@rian_ru", "@SVO_ZOV_22", "@tsargradtv"}  # Набор каналов по умолчанию
        self.theme_emojis = theme_emojis

    def add_user_interest(self, user_id, interest):
        """Добавление интереса пользователя."""
        current_interests = self.interest_repository.get_user_interests(user_id)
        if interest not in current_interests:
            current_interests.append(interest)
            self.interest_repository.add_user_interests(user_id, current_interests)

    def remove_user_interest(self, user_id, interest):
        """Удаление интереса пользователя."""
        current_interests = self.interest_repository.get_user_interests(user_id)
        if interest in current_interests:
            current_interests.remove(interest)
            if current_interests:
                self.interest_repository.update_user_interests(user_id, current_interests)
            else:
                self.interest_repository.remove_user_interests(user_id)

    def get_user_interests(self, user_id):
        """Получение списка интересов пользователя."""
        return self.interest_repository.get_user_interests(user_id)

    def clear_user_interests(self, user_id):
        """Очищение всех интересов пользователя."""
        self.interest_repository.remove_user_interests(user_id)

    def initialize_user_interests(self, user_id):
        """Инициализация интересов пользователя."""
        current_interests = self.interest_repository.get_user_interests(user_id)
        if not current_interests:
            # Установка начальных интересов, если они отсутствуют
            self.interest_repository.add_user_interests(user_id, [])

    def is_user_subscribed_to_interest(self, user_id, interest):
        """Проверка, подписан ли пользователь на интерес."""
        current_interests = self.interest_repository.get_user_interests(user_id)
        return interest in current_interests



