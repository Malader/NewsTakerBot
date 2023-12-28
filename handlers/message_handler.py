from collections import defaultdict

import telethon
from telethon import events

from handlers.AddChannelHandler import AddChannelHandler
from handlers.MyChannelsHandler import MyChannelsHandler
from handlers.MySubscriptionsHandler import MySubscriptionsHandler
from handlers.NewsHandler import NewsHandler
from handlers.RemoveChannelHandler import RemoveChannelHandler
from handlers.StartHandler import StartHandler
from handlers.SubscriptionHandler import SubscriptionHandler
from services.NewsFetcher import NewsFetcher
from handlers.HelpHandler import HelpHandler


class MessageHandler:
    def __init__(self, user_client, bot_client, user_subscription_manager, user_interest_manager, button_manager_instance, text_processor):
        self.user_client = user_client
        self.bot_client = bot_client
        self.user_subscription_manager = user_subscription_manager
        self.user_interest_manager = user_interest_manager
        self.button_manager = button_manager_instance
        self.text_processor = text_processor
        self.news_fetcher = NewsFetcher(user_client, text_processor, user_subscription_manager, self)
        self.start_handler = StartHandler(user_subscription_manager)
        self.news_handler = NewsHandler(user_subscription_manager, user_interest_manager, self.news_fetcher, text_processor)
        self.subscription_handler = SubscriptionHandler(user_interest_manager, button_manager_instance)
        self.help_handler = HelpHandler(self.bot_client)
        self.add_channel_handler = AddChannelHandler(self.user_subscription_manager, self.bot_client)
        self.my_channels_handler = MyChannelsHandler(self.user_subscription_manager, self.bot_client)
        self.remove_channel_handler = RemoveChannelHandler(self.user_subscription_manager, self.bot_client)
        self.my_subscriptions_handler = MySubscriptionsHandler(user_interest_manager, bot_client)

    async def subscribe_all(self, event):
        user_id = event.sender_id
        all_interests = ['Спорт', 'Политика', 'СВО', 'Экономика', 'Наука', 'Технологии', 'Культура', 'Здоровье',
                         'Образование']

        # Добавляем все интересы
        for interest in all_interests:
            self.user_interest_manager.add_user_interest(user_id, interest)

        # Обновляем сообщение
        try:
            await event.edit('Вы успешно подписались на все темы. Используйте /mysubscriptions для управления темами.')
        except telethon.errors.rpcerrorlist.MessageNotModifiedError:
            # Если содержимое сообщения не изменилось, игнорируем ошибку
            pass

    def ensure_user_subscriptions_initialized(self, user_id):
        # Получаем подписки пользователя с помощью метода класса UserSubscriptionManager
        user_subscriptions = self.user_subscription_manager.get_user_subscriptions(user_id)

        if not user_subscriptions:
            # Если у пользователя нет подписок, инициализируем их
            self.user_subscription_manager.initialize_user_subscriptions(user_id)

    def register_handlers(self):
        @self.bot_client.on(events.NewMessage(pattern='/start'))
        async def handle_start(event):
            await self.start_handler.handle(event, self.bot_client)

        @self.bot_client.on(events.NewMessage(pattern='/news'))
        async def handle_news(event):
            await self.news_handler.handle(event, self.bot_client)

        @self.bot_client.on(events.NewMessage(pattern='/subscribe'))
        async def handle_subscribe(event):
            await self.subscription_handler.handle(event)

        @self.bot_client.on(events.CallbackQuery(data=b'subscribe_all'))
        async def handle_subscribe_all(event):
            await self.subscribe_all(event)
            pass

        @self.bot_client.on(events.NewMessage(pattern='/mysubscriptions'))
        async def handle_my_subscriptions(event):
            await self.my_subscriptions_handler.handle(event)

        @self.bot_client.on(events.NewMessage(pattern='/help'))
        async def handle_help(event):
            await self.help_handler.handle(event)

        @self.bot_client.on(events.CallbackQuery(data=b'add_interests'))
        async def add_interests(event):
            user_id = event.sender_id
            # Предоставляем пользователю возможность подписаться на новые темы
            buttons = self.button_manager.create_subscription_buttons(user_id)

            try:
                # Попытка обновить сообщение
                await event.edit('Выберите темы, на которые вы хотите подписаться:', buttons=buttons)
            except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                # Если сообщение не изменилось, игнорируем ошибку или уведомляем пользователя
                await event.answer('Список тем для подписки не изменился.', alert=True)

            pass

        # Место для хранения каналов пользователей
        # В примере используется словарь, где ключ - ID пользователя, а значение - список каналов
        user_channels = defaultdict(list)

        @self.bot_client.on(events.NewMessage(pattern='/addchannel(?: (.*))?'))
        async def handle_add_channel(event):
            await self.add_channel_handler.handle(event)

        @self.bot_client.on(events.NewMessage(pattern='/mychannels'))
        async def handle_my_channels(event):
            await self.my_channels_handler.handle(event)

        @self.bot_client.on(events.CallbackQuery(pattern=r'^removechannel_(.+)$'))
        async def handle_remove_channel(event):
            await self.remove_channel_handler.handle(event)

        @self.bot_client.on(events.CallbackQuery(pattern='^obsolete_button$'))
        async def obsolete_button_handler(event):
            # Посылаем пустой ответ, чтобы избежать сообщения "неверная команда".
            await event.answer()

        # Этот обработчик должен быть последним в вашем списке обработчиков CallbackQuery
        @self.bot_client.on(events.CallbackQuery())
        async def catch_all_callback_queries(event):
            callback_data = event.data.decode('utf-8')
            print(f"Получен callback запрос: {callback_data}")

            # Список известных callback data, которые обрабатываются другими handlers
            known_callbacks = [
                'unsubscribe_',
                'show_all_news',
                'finish_subscription',
                'subscribe_all',
                'removechannel_',
                'subscribe',
                'add_interests',
                'unsubscribe'
            ]

            if any(callback_data.startswith(known) for known in known_callbacks):
                print("Этот callback уже обработан другим handler.")
            else:
                # Отправляем сообщение пользователю, что команда не распознана
                await event.answer()

