from collections import defaultdict

import telethon
from telethon import events, Button
from telethon.tl.types import Channel

# import subscription_manager
from NewsFetcher import NewsFetcher
# from text_processor import TextProcessor
# from subscription_manager import SubscriptionManager


class MessageHandler:
    def __init__(self, user_client, bot_client, subscription_manager_instance, button_manager_instance, text_processor):
        self.user_client = user_client
        self.bot_client = bot_client
        self.subscription_manager = subscription_manager_instance
        self.button_manager = button_manager_instance
        self.text_processor = text_processor
        self.news_fetcher = NewsFetcher(user_client, text_processor, subscription_manager_instance, self)

    async def subscribe_all(self, event):
        user_id = event.sender_id
        all_interests = ['Спорт', 'Политика', 'СВО', 'Экономика', 'Наука', 'Технологии', 'Культура', 'Здоровье',
                         'Образование']

        self.subscription_manager.initialize_user_interests(user_id)

        # Подписываем пользователя на все темы
        self.subscription_manager.add_interests(user_id, all_interests)

        # Обновляем сообщение
        try:
            await event.edit('Вы успешно подписались на все темы. Используйте /mysubscriptions для управления темами.')
        except telethon.errors.rpcerrorlist.MessageNotModifiedError:
            # Если содержимое сообщения не изменилось, отправляем пользователю уведомление
            await event.answer('Вы уже подписаны на все темы.', alert=True)

    def ensure_user_subscriptions_initialized(self, user_id):
        if user_id not in self.subscription_manager.user_subscriptions:
            # Пользователь новый, еще не выполнял действий с подписками
            self.subscription_manager.user_subscriptions[user_id] = self.subscription_manager.default_channels.copy()
        elif not self.subscription_manager.user_subscriptions[user_id]:
            # Пользователь есть в системе, но подписки отсутствуют, что может быть результатом их удаления
            # В зависимости от желаемого поведения, можно ничего не делать
            pass

    def register_handlers(self):
        @self.bot_client.on(events.NewMessage(pattern='/start'))
        async def start(event):
            user_id = event.sender_id
            self.subscription_manager.initialize_user_subscriptions(user_id)
            # Сообщение, которое будет отправлено пользователю
            welcome_message = (
                "Привет! Я ваш новостной бот. Вот что я умею:\n\n"
                "📰 Получение новостей из базового набора каналов.\n"
                "🔍 Фильтрация новостей по темам интереса.\n"
                "📢 Добавление и удаление новостных каналов.\n"
                "🔔 Управление подписками на темы.\n\n"
                "Чтобы начать, вы можете использовать следующие команды:\n"
                "/news - получить последние новости\n"
                "/subscribe - подписаться на темы новостей\n"
                "/mysubscriptions - просмотреть текущие подписки\n"
                "/addchannel - добавить новостной канал\n"
                "/removechannel - удалить новостной канал\n"
                "/mychannels - посмотреть список текущих каналов\n\n"
                "У вас уже есть доступ к базовому набору новостных каналов. Вы можете управлять своими каналами и темами, чтобы получать новости, которые вас интересуют!\n\n"
                "Чтобы посмотреть список базовых каналов, на которые подписан бот, воспользуйтесь командой /mychannels\n"
            )

            # Отправляем приветственное сообщение пользователю
            await event.respond(welcome_message)
            pass

        @self.bot_client.on(events.NewMessage(pattern='/news'))
        async def news(event):
            user_id = event.sender_id
            self.ensure_user_subscriptions_initialized(user_id)
            self.subscription_manager.initialize_user_subscriptions(user_id)
            user_added_channels = self.subscription_manager.get_user_subscriptions(user_id)
            # Объединяем пользовательские каналы с базовыми
            all_subscribed_channels = user_added_channels

            if not all_subscribed_channels:
                await event.respond(
                    "Вы не подписаны ни на один канал. Используйте /addchannel для подписки на интересные вам каналы.")
                return

            interests = self.subscription_manager.get_user_interests(user_id)
            if not interests:
                buttons = [
                    [Button.inline("Показать все новости без фильтрации по темам", "show_all_news")],
                    [Button.inline("Выбрать темы для фильтрации", "subscribe")]
                ]
                await event.respond("Вы не выбрали ни одной темы. Что вы хотите сделать?", buttons=buttons)
                return

            unique_messages = await self.news_fetcher.fetch_telegram_channel_messages(user_id)
            print(f"Fetched {len(unique_messages)} unique messages")  # Логируем количество уникальных сообщений

            filtered_messages = self.text_processor.filter_messages_by_interest(unique_messages, interests)
            print(f"Filtered down to {len(filtered_messages)} messages after applying user interests")  # Логируем результаты фильтрации

            # Отправка отфильтрованных сообщений
            if len(filtered_messages) == 0:
                await event.respond('К сожалению, новостей по вашим интересам сейчас нет.')
                return

            for message in filtered_messages:
                try:
                    if message.media:
                        await self.bot_client.forward_messages(entity=user_id, messages=message.id, from_peer=message.chat_id)
                    else:
                        await self.bot_client.send_message(user_id, message.text)
                except Exception as e:
                    print(f"Error sending message: {e}")

            pass

        @self.bot_client.on(events.NewMessage(pattern='/subscribe'))
        async def subscribe(event):
            user_id = event.sender_id
            buttons = self.button_manager.create_subscription_buttons(user_id)

            if not buttons:
                await event.respond(
                    'Доступных для подписки тем нет, вы уже подписались на все темы. Используйте /mysubscriptions для управления темами.')
            else:
                # Добавляем кнопку "Закончить выбор" в конец списка кнопок
                # buttons.append([Button.inline("✅ Закончить выбор", "finish_subscription")])
                await event.respond('Выберите темы, на которые вы хотите подписаться:', buttons=buttons)

            pass

        @self.bot_client.on(events.CallbackQuery(data=b'subscribe_all'))
        async def handle_subscribe_all(event):
            await self.subscribe_all(event)
            pass

        @self.bot_client.on(events.NewMessage(pattern='/mysubscriptions'))
        async def my_subscriptions(event):
            user_id = event.sender_id
            subscriptions = self.subscription_manager.get_user_interests(user_id)
            all_interests = ['Спорт', 'Политика', 'СВО', 'Экономика', 'Наука', 'Технологии', 'Культура', 'Здоровье',
                             'Образование']

            if subscriptions:
                buttons = [
                    [Button.inline(f"{self.subscription_manager.theme_emojis.get(interest, '')} Отписаться от {interest}",
                                   f"unsubscribe_{interest}")] for
                    interest in subscriptions]

                # Всегда добавляем кнопку "Отписаться от всех тем"
                buttons.append([Button.inline("❌ Отписаться от всех тем", "unsubscribe")])

                # Если пользователь подписан не на все темы, добавляем кнопку "Добавить темы"
                if len(subscriptions) < len(all_interests):
                    buttons.append([Button.inline("➕ Добавить темы", "add_interests")])

                await event.respond('Вы подписаны на следующие темы:', buttons=buttons)
            else:
                await event.respond('Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.')
            pass

        @self.bot_client.on(events.NewMessage(pattern='/help'))
        async def help_command(event):
            user_id = event.sender_id
            help_message = (
                "🆘 Команда помощи 🆘\n\n"
                "Если у вас возникли вопросы или нужна помощь, пожалуйста, свяжитесь с @Malader или с @adamishhe.\n\n"
                "Для получения информации о других командах бота используйте команду /start."
            )

            # Отправляем сообщение с информацией о помощи
            await event.respond(help_message)
            pass

        @self.bot_client.on(events.CallbackQuery(pattern=r'^unsubscribe_(.+)$'))
        async def unsubscribe_interest(event):
            user_id = event.sender_id
            interest_to_unsubscribe = event.pattern_match.group(1)

            # Формируем новый список подписок и соответствующие кнопки
            current_subscriptions = self.subscription_manager.get_user_interests(user_id)
            buttons = [
                [Button.inline(f"{self.subscription_manager.theme_emojis.get(interest, '')} Отписаться от {interest}", f"unsubscribe_{interest}")]
                for interest in current_subscriptions]

            # Всегда добавляем кнопку "Отписаться от всех тем"
            buttons.append([Button.inline("❌ Отписаться от всех тем", "unsubscribe")])

            if current_subscriptions:
                buttons.append([Button.inline("➕ Добавить темы", "add_interests")])



            # Обновляем текст сообщения
            message_text = 'Вы подписаны на следующие темы:' if current_subscriptions else 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'

            try:
                await event.edit(message_text, buttons=buttons)
            except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                # Если содержимое сообщения не изменилось, отправляем пользователю уведомление
                await event.answer('Список подписок не изменился.', alert=True)
            await event.answer(f'Вы отписались от темы "{interest_to_unsubscribe}".', alert=True)

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
        async def add_channel(event):
            user_id = event.sender_id
            channel_to_add = event.pattern_match.group(1)

            if not channel_to_add:
                await event.respond("Пожалуйста, укажите канал после команды. Например: /addchannel @channelname")
                return

            try:
                channel_entity = await self.bot_client.get_entity(channel_to_add)
                if isinstance(channel_entity, Channel):
                    user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)

                    # Добавляем базовые каналы в подписки пользователя, если они еще не добавлены
                    for base_channel in self.subscription_manager.default_channels:
                        user_subscriptions.add(base_channel)

                    if channel_to_add in user_subscriptions:
                        # Пользователь уже подписан на этот канал
                        await event.respond(f"Вы уже подписаны на канал {channel_to_add}.")
                        return

                    user_subscriptions.add(channel_to_add)
                    self.subscription_manager.set_user_subscriptions(user_id, user_subscriptions)
                    await event.respond(f"Канал {channel_to_add} успешно добавлен в ваш список подписок.")
                else:
                    await event.respond(f"{channel_to_add} не является каналом.")
            except Exception as e:
                await event.respond(
                    f"Не удалось добавить канал {channel_to_add}. Убедитесь, что имя канала правильное и попробуйте снова.")

        @self.bot_client.on(events.NewMessage(pattern='/mychannels'))
        async def my_channels(event):
            user_id = event.sender_id
            if user_id not in self.subscription_manager.user_subscriptions:
                self.subscription_manager.user_subscriptions[user_id] = self.subscription_manager.default_channels.copy()

            # Получаем список каналов, на которые подписан пользователь
            subscribed_channels = self.subscription_manager.user_subscriptions[user_id]

            if subscribed_channels:
                buttons = [[Button.inline(f"Удалить {channel}", f"removechannel_{channel.replace('@', '')}")] for
                           channel in
                           sorted(subscribed_channels)]
                channels_list = '\n'.join(sorted(subscribed_channels))
                await event.respond(f"Вы подписаны на следующие каналы:\n{channels_list}", buttons=buttons)
            else:
                await event.respond("Вы не подписаны ни на один канал.")
            pass

        @self.bot_client.on(events.CallbackQuery(pattern=r'^removechannel_(.+)$'))
        async def remove_channel_callback(event):
            user_id = event.sender_id
            channel_to_remove = '@' + event.pattern_match.group(1).decode('utf-8') if isinstance(
                event.pattern_match.group(1), bytes) else event.pattern_match.group(1)

            # Получаем текущие подписки пользователя
            user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)

            if channel_to_remove in user_subscriptions:
                # Удаляем канал из подписок
                user_subscriptions.discard(channel_to_remove)

                # Обновляем подписки пользователя
                self.subscription_manager.set_user_subscriptions(user_id, user_subscriptions)
                if user_subscriptions:
                    # Создаем кнопки для обновленного списка каналов
                    buttons = [[Button.inline(f"Удалить {channel}", f"removechannel_{channel.replace('@', '')}")] for
                            channel in sorted(user_subscriptions)]
                    # await event.answer(f"Канал {channel_to_remove} удален из списка.", alert=True)

                    message_text = f"Вы подписаны на следующие каналы:\n{', '.join(sorted(user_subscriptions))}" if user_subscriptions else "Вы не подписаны ни на один канал."
                    await event.edit(message_text, buttons=buttons)
                else:
                    await event.edit("Вы не подписаны ни на один канал.")
            else:
                await event.answer(f"Канал {channel_to_remove} не найден в вашем списке подписок.", alert=True)

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

