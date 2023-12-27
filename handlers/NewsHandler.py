from telethon import Button


class NewsHandler:
    def __init__(self, subscription_manager, news_fetcher, text_processor):
        self.subscription_manager = subscription_manager
        self.news_fetcher = news_fetcher
        self.text_processor = text_processor

    async def handle(self, event, bot_client):
        user_id = event.sender_id
        user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)

        # Если у пользователя нет подписок на каналы
        if not user_subscriptions:
            await bot_client.send_message(user_id, "Вы не подписаны ни на один канал. Используйте /addchannel для подписки на интересные вам каналы.")
            return

        # Если у пользователя нет интересов для фильтрации новостей
        interests = self.subscription_manager.get_user_interests(user_id)
        if not interests:
            buttons = [
                [Button.inline("Показать все новости без фильтрации по темам", "show_all_news")],
                [Button.inline("Выбрать темы для фильтрации", "subscribe")]
            ]
            await bot_client.send_message(user_id, "Вы не выбрали ни одной темы. Что вы хотите сделать?", buttons=buttons)
            return

        # Продолжаем получать и фильтровать новости, если есть подписки и интересы
        unique_messages = await self.news_fetcher.fetch_telegram_channel_messages(user_id)
        filtered_messages = self.text_processor.filter_messages_by_interest(unique_messages, interests)

        if filtered_messages:
            for message in filtered_messages:
                try:
                    if message.media:
                        await bot_client.forward_messages(entity=user_id, messages=message.id, from_peer=message.chat_id)
                    else:
                        await bot_client.send_message(user_id, message.text)
                except Exception as e:
                    print(f"Error sending message: {e}")
        else:
            await bot_client.send_message(user_id, 'К сожалению, новостей по вашим интересам сейчас нет.')
