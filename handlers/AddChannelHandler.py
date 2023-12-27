from telethon.tl.types import Channel


class AddChannelHandler:
    def __init__(self, subscription_manager, bot_client):
        self.subscription_manager = subscription_manager
        self.bot_client = bot_client

    async def handle(self, event):
        user_id = event.sender_id
        channel_to_add = event.pattern_match.group(1)

        if not channel_to_add:
            await self.bot_client.send_message(event.chat_id, "Пожалуйста, укажите канал после команды. Например: /addchannel @channelname")
            return

        try:
            channel_entity = await self.bot_client.get_entity(channel_to_add)
            if isinstance(channel_entity, Channel):
                user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)

                if channel_to_add in user_subscriptions:
                    await self.bot_client.send_message(event.chat_id, f"Вы уже подписаны на канал {channel_to_add}.")
                    return

                user_subscriptions.add(channel_to_add)
                self.subscription_manager.add_subscription(user_id, channel_to_add)
                await self.bot_client.send_message(event.chat_id, f"Канал {channel_to_add} успешно добавлен в ваш список подписок.")
            else:
                await self.bot_client.send_message(event.chat_id, f"{channel_to_add} не является каналом.")
        except Exception as e:
            await self.bot_client.send_message(event.chat_id, f"Не удалось добавить канал {channel_to_add}. Убедитесь, что имя канала правильное и попробуйте снова.")
