from telethon import TelegramClient, events

from utils.ButtonManager import ButtonManager
from services.NewsFetcher import NewsFetcher
from handlers.message_handler import MessageHandler
from models.subscription_manager import SubscriptionManager
from handlers.CallbackQueryHandler import CallbackQueryHandler
from services.text_processor import TextProcessor


class BotClient:
    def __init__(self, api_id, api_hash, bot_token):
        self.news_fetcher = None
        self.user_client = TelegramClient('user_session', api_id, api_hash)
        self.bot_client = TelegramClient('bot_session', api_id, api_hash)
        # Создание экземпляров менеджеров
        self.bot_token = bot_token
        self.subscription_manager_instance = SubscriptionManager()
        self.button_manager_instance = ButtonManager(self.subscription_manager_instance)
        self.text_processor = TextProcessor()
        # Создание экземпляра MessageHandler с передачей необходимых экземпляров менеджеров
        self.message_handler = None
        self.text_processor_instance = TextProcessor()

    async def start(self):
        await self.user_client.start()
        await self.bot_client.start(bot_token=self.bot_token)

        self.text_processor = TextProcessor()

        self.message_handler = MessageHandler(
            self.user_client, self.bot_client,
            self.subscription_manager_instance,
            self.button_manager_instance, self.text_processor_instance
        )

        self.message_handler.register_handlers()

        self.news_fetcher = NewsFetcher(
            self.user_client, self.text_processor,
            self.subscription_manager_instance, self.message_handler
        )

        callback_query_handler = CallbackQueryHandler(
            self.bot_client, self.subscription_manager_instance,
            self.button_manager_instance, self.text_processor_instance,
            self.news_fetcher, self.message_handler
        )

        @self.bot_client.on(events.CallbackQuery())
        async def handle_callback_query(event):
            await callback_query_handler.handle_callback_query(event)

        await self.bot_client.run_until_disconnected()
