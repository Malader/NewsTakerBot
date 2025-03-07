from Abstract.AbstractNewsFetcher import AbstractNewsFetcher


class NewsFetcher(AbstractNewsFetcher):
    def __init__(self, user_client, text_processor_interface, subscription_manager_interface, message_handler_interface):
        self.user_client = user_client
        self.text_processor = text_processor_interface
        self.subscription_manager = subscription_manager_interface
        self.message_handler = message_handler_interface

    async def fetch_telegram_channel_messages(self, user_id):
        self.message_handler.ensure_user_subscriptions_initialized(user_id)
        user_added_channels = self.subscription_manager.get_user_subscriptions(user_id)

        all_messages = []
        for channel in user_added_channels:
            try:
                channel_entity = await self.user_client.get_entity(channel)
                async for message in self.user_client.iter_messages(channel_entity, limit=50):
                    all_messages.append(message)
            except Exception as e:
                print(f"Не удалось получить сообщения из канала {channel}: {e}")

        unique_messages = self.text_processor.remove_duplicates(all_messages)
        return unique_messages
