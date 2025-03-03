from telethon import Button


class RemoveChannelHandler:
    def __init__(self, subscription_manager, bot_client):
        self.subscription_manager = subscription_manager
        self.bot_client = bot_client

    async def handle(self, event):
        user_id = event.sender_id
        channel_to_remove = '@' + event.pattern_match.group(1).decode('utf-8')

        user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)
        if channel_to_remove in user_subscriptions:
            self.subscription_manager.remove_subscription(user_id, channel_to_remove)
            user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)

            if user_subscriptions:
                buttons = [[Button.inline(f"Удалить {channel}", f"removechannel_{channel.replace('@', '')}")]
                           for channel in sorted(user_subscriptions)]
                message_text = f"Вы подписаны на следующие каналы:\n{', '.join(sorted(user_subscriptions))}"
                await self.bot_client.edit_message(event.chat_id, event.message_id, message_text, buttons=buttons)
            else:
                # Если нет подписок, сообщаем пользователю, что все каналы были удалены
                await self.bot_client.edit_message(event.chat_id, event.message_id, "Вы не подписаны ни на один канал.")
        else:
            # Сообщаем пользователю, что такого канала нет в его подписках
            await event.answer(f"Канал {channel_to_remove} не найден в вашем списке подписок.", alert=True)


