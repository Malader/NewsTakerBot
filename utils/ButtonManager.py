from telethon import Button


class ButtonManager:
    def __init__(self, interest_manager):
        self.interest_manager = interest_manager

    def create_subscription_buttons(self, user_id):
        all_interests = list(self.interest_manager.theme_emojis.keys())
        subscribed_interests = self.interest_manager.get_user_interests(user_id)
        buttons = []

        for interest in all_interests:
            if interest not in subscribed_interests:
                emoji = self.interest_manager.theme_emojis.get(interest, '')
                buttons.append([Button.inline(f"{emoji} {interest}", interest)])

        buttons.append([Button.inline("✅ Закончить выбор", "finish_subscription")])

        if len(subscribed_interests) < len(all_interests):
            buttons.append([Button.inline('🌐 Подписаться на все темы', 'subscribe_all')])

        return buttons
