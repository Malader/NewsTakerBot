from telethon import Button


class MySubscriptionsHandler:
    def __init__(self, interest_manager, bot_client):
        self.interest_manager = interest_manager
        self.bot_client = bot_client

    async def handle(self, event):
        user_id = event.sender_id
        user_interests = self.interest_manager.get_user_interests(user_id)
        all_interests = list(self.interest_manager.theme_emojis.keys())

        if user_interests:
            buttons = [
                [Button.inline(f"{self.interest_manager.theme_emojis.get(interest, '')} Отписаться от {interest}", f"unsubscribe_{interest}")]
                for interest in user_interests
            ]
            buttons.append([Button.inline("❌ Отписаться от всех тем", "unsubscribe")])

            if len(user_interests) < len(all_interests):
                buttons.append([Button.inline("➕ Добавить темы", "add_interests")])

            await event.respond('Вы подписаны на следующие темы:', buttons=buttons)
        else:
            await self.bot_client.send_message(event.chat_id, "Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.")



