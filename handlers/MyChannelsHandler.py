from telethon import Button


class MyChannelsHandler:
    def __init__(self, subscription_manager, bot_client):
        self.subscription_manager = subscription_manager
        self.bot_client = bot_client

    async def handle(self, event):
        user_id = event.sender_id
        # Получаем список каналов, на которые подписан пользователь
        subscribed_channels = self.subscription_manager.get_user_subscriptions(user_id)

        if subscribed_channels:
            # Создаем кнопки для удаления каналов
            buttons = [[Button.inline(f"Удалить {channel}", f"removechannel_{channel.replace('@', '')}")]
                       for channel in sorted(subscribed_channels)]
            channels_list = '\n'.join(sorted(subscribed_channels))
            await self.bot_client.send_message(event.chat_id,
                                               f"Вы подписаны на следующие каналы:\n{channels_list}",
                                               buttons=buttons)
        else:
            # Если нет подписанных каналов, сообщаем об этом
            await self.bot_client.send_message(event.chat_id,
                                               "Вы не подписаны ни на один канал. Используйте команду /addchannel для добавления каналов.")
