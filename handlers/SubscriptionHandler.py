class SubscriptionHandler:
    def __init__(self, interest_manager, button_manager):
        self.interest_manager = interest_manager
        self.button_manager = button_manager

    async def handle(self, event, bot_client):
        user_id = event.sender_id

        all_interests = list(self.interest_manager.theme_emojis.keys())
        subscribed_interests = self.interest_manager.get_user_interests(user_id)

        # Проверяем, подписан ли пользователь на все темы
        if len(subscribed_interests) == len(all_interests):
            # Если подписан на все темы, отправляем сообщение об этом
            await event.respond(
                'Вы уже подписаны на все доступные темы. Используйте /mysubscriptions для управления темами.')
        else:
            # Если не подписан на все темы, показываем кнопки для подписки
            buttons = self.button_manager.create_subscription_buttons(user_id)
            await event.respond('Выберите темы, на которые вы хотите подписаться:', buttons=buttons)
