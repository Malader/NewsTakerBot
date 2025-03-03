from telethon import TelegramClient, events

from Database.Database import Database
from models.UserInterestManager import UserInterestManager
from models.UserSubscriptionManager import UserSubscriptionManager
from utils.ButtonManager import ButtonManager
from services.NewsFetcher import NewsFetcher
from handlers.message_handler import MessageHandler
from handlers.CallbackQueryHandler import CallbackQueryHandler
from services.text_processor import TextProcessor


class BotClient:
    def __init__(self, api_id, api_hash, bot_token, db_path):
        self.user_client = TelegramClient('user_session', api_id, api_hash)
        self.bot_client = TelegramClient('bot_session', api_id, api_hash)
        self.bot_token = bot_token

        db_instance = Database(db_path)

        self.subscription_manager_instance = UserSubscriptionManager(db_instance)
        self.interest_manager_instance = UserInterestManager(db_instance, self.subscription_manager_instance.theme_emojis)
        self.button_manager_instance = ButtonManager(self.interest_manager_instance)
        self.text_processor_instance = TextProcessor()

    async def start(self):
        await self.user_client.start()
        await self.bot_client.start(bot_token=self.bot_token)

        self.text_processor = TextProcessor()

        self.message_handler = MessageHandler(
            self.user_client, self.bot_client,
            self.subscription_manager_instance, self.interest_manager_instance,
            self.button_manager_instance, self.text_processor_instance
        )

        self.message_handler.register_handlers()

        self.news_fetcher = NewsFetcher(
            self.user_client, self.text_processor,
            self.subscription_manager_instance, self.message_handler
        )

        callback_query_handler = CallbackQueryHandler(
            self.bot_client, self.subscription_manager_instance, self.interest_manager_instance,
            self.button_manager_instance, self.text_processor_instance,
            self.news_fetcher, self.message_handler
        )

        @self.bot_client.on(events.CallbackQuery())
        async def handle_callback_query(event):
            await callback_query_handler.handle_callback_query(event)

        await self.bot_client.run_until_disconnected()
