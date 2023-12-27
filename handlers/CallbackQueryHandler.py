import telethon
from telethon import Button
from datetime import datetime


class CallbackQueryHandler:
    def __init__(self, bot_client, user_subscription_manager, user_interest_manager, button_manager, text_processor, news_fetcher, message_handler):
        self.bot_client = bot_client
        self.user_subscription_manager = user_subscription_manager
        self.user_interest_manager = user_interest_manager
        self.button_manager = button_manager
        self.text_processor = text_processor
        self.news_fetcher = news_fetcher
        self.message_handler = message_handler

    async def handle_callback_query(self, event):
        user_id = event.sender_id
        data = event.data.decode('utf-8')

        # Убедимся, что у пользователя есть запись в словаре интересов
        self.user_interest_manager.initialize_user_interests(user_id)
        try:
            if data.startswith('unsubscribe_'):
                interest_to_remove = data.split('_')[1]
                if interest_to_remove:
                    # Обработка отписки от конкретной темы
                    if self.user_interest_manager.is_user_subscribed_to_interest(user_id, interest_to_remove):
                        self.user_interest_manager.remove_user_interest(user_id, interest_to_remove)
                        updated_subscriptions = self.user_interest_manager.get_user_interests(user_id)

                        buttons, new_message_text = self.create_buttons_and_message_text(updated_subscriptions)
                        try:
                            await event.edit(new_message_text, buttons=buttons)
                            await event.answer(f'Вы отписались от темы "{interest_to_remove}".', alert=True)
                        except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                            pass
                else:
                    # Обработка отписки от всех тем, если запрос пустой
                    self.user_interest_manager.clear_user_interests(user_id)
                    message_text = 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'
                    buttons = [[Button.inline("➕ Добавить темы", "add_interests")]]
                    await event.edit(message_text, buttons=buttons)
                    await event.answer('Вы успешно отписались от всех тем.', alert=True)
                    # Проверка и обновление кнопок после удаления интереса
                updated_subscriptions = self.user_interest_manager.get_user_interests(user_id)
                if not updated_subscriptions:
                    # Если у пользователя не осталось подписок
                    buttons = [[Button.inline("➕ Добавить темы", "add_interests")]]
                    message_text = 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'
                    await event.edit(message_text, buttons=buttons)

            elif data.startswith('removechannel_'):
                # Обработка удаления канала
                channel_to_remove = '@' + data[len('removechannel_'):]
                user_subscriptions = self.user_subscription_manager.get_user_subscriptions(user_id)
                if channel_to_remove in user_subscriptions:
                    user_subscriptions.discard(channel_to_remove)
                    self.user_subscription_manager.set_user_subscriptions(user_id, user_subscriptions)
                    # Обновляем список каналов после удаления
                    if user_subscriptions:
                        buttons = [[Button.inline(f"Удалить {channel}", f"removechannel_{channel.replace('@', '')}")]
                                   for channel in sorted(user_subscriptions)]
                        message_text = f"Вы подписаны на следующие каналы:\n{', '.join(sorted(user_subscriptions))}"
                        await event.edit(message_text, buttons=buttons)
                    else:
                        # Каналы отсутствуют, обновляем сообщение и убираем кнопки
                        await event.edit("Вы не подписаны ни на один канал.",
                                         buttons=None)  # buttons=None убирает все кнопки

            elif data == 'unsubscribe':
                # Обработка отписки от всех тем
                self.user_interest_manager.clear_user_interests(user_id)
                current_subscriptions = self.user_interest_manager.get_user_interests(user_id)
                if not current_subscriptions:
                    # Если у пользователя не осталось подписок
                    buttons = [[Button.inline("➕ Добавить темы", "add_interests")]]
                    message_text = 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'
                    await event.edit(message_text, buttons=buttons)
                    await event.answer('Вы успешно отписались от всех тем.', alert=True)
                else:
                    # Если у пользователя остались подписки (для обработки непредвиденных сценариев)
                    buttons = self.create_buttons_for_subscriptions(current_subscriptions)
                    message_text = 'Вы подписаны на следующие темы:'
                    await event.edit(message_text, buttons=buttons)

            elif data == 'add_interests':
                # Показываем кнопки для добавления новых интересов
                buttons = self.button_manager.create_subscription_buttons(user_id)
                try:
                    await event.edit('Выберите темы, на которые вы хотите подписаться:', buttons=buttons)
                except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                    pass

            elif data == 'subscribe':
                # Обработка запроса на выбор тем для фильтрации
                buttons = self.button_manager.create_subscription_buttons(user_id)
                # Добавляем временную метку к сообщению
                timestamp = datetime.now().strftime("%H:%M:%S")
                message_text = f'Выберите темы, на которые вы хотите подписаться: (обновлено {timestamp})'

                try:
                    await event.edit(message_text, buttons=buttons)
                except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                    pass  # Игнорируем ошибку, если текст сообщения не был изменен

            elif event.data.decode('utf-8') == 'subscribe_all':
                await self.message_handler.subscribe_all(event)  # вызов функции подписки на все темы

            elif data == 'finish_subscription':
                # Проверка, изменилось ли сообщение перед его редактированием
                new_message_text = 'Выбор тем завершен. Используйте /mysubscriptions для управления темами.'
                current_message_text = (await event.get_message()).message
                if new_message_text != current_message_text:
                    await event.edit(new_message_text)
                else:
                    await event.answer('Выбор тем уже завершен.', alert=True)

            elif data == 'show_all_news':
                # user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)
                # if user_id not in user_subscriptions or not user_subscriptions[user_id]:
                if not self.user_subscription_manager .get_user_subscriptions(user_id):
                    await event.respond("Вы не подписаны ни на один канал. Используйте /addchannel для добавления.")
                    return
                # Обработка запроса на показ всех новостей без фильтрации
                unique_messages = await self.news_fetcher.fetch_telegram_channel_messages(user_id)
                if unique_messages:
                    for message in unique_messages:
                        try:
                            if message.media:
                                await self.bot_client.forward_messages(entity=user_id, messages=message.id,
                                                                       from_peer=message.chat_id)
                            else:
                                await self.bot_client.send_message(user_id, message.text)
                        except Exception as e:
                            print(f"Error sending message: {e}")
                    await event.answer('Показаны все последние новости.', alert=True)
                else:
                    await event.respond("Нет новостей для показа.")

            elif data in self.text_processor.get_interest_keywords():
                # Добавляем интерес в список подписок пользователя
                if not self.user_interest_manager.is_user_subscribed_to_interest(user_id, data):
                    self.user_interest_manager.add_user_interest(user_id, data)
                    buttons = self.button_manager.create_subscription_buttons(user_id)

                    # Добавляем временную метку к сообщению
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message_text = f'Вы подписались на тему "{data}". Вы можете выбрать остальные темы, на которые вы хотите подписаться:'

                    try:
                        await event.edit(message_text, buttons=buttons)
                    except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                        pass  # Игнорируем ошибку, если текст сообщения не был изменен
                else:
                    await event.answer(f'Вы уже подписаны на тему "{data}".', alert=True)

            else:
                await event.answer('Неверная команда.', alert=True)

        except telethon.errors.rpcerrorlist.QueryIdInvalidError:
            # Игнорировать ошибку, если запрос уже обработан или недействителен
            print("QueryIdInvalidError caught, ignoring")

    def create_buttons_and_message_text(self, subscriptions):
        buttons = [[Button.inline(
            f"{self.user_interest_manager.theme_emojis.get(interest, '')} Отписаться от {interest}",
            f"unsubscribe_{interest}")]
                   for interest in subscriptions]
        buttons.append([Button.inline("❌ Отписаться от всех тем", "unsubscribe")])
        buttons.append([Button.inline("➕ Добавить темы", "add_interests")])

        if subscriptions:
            message_text = 'Вы подписаны на следующие темы:'
        else:
            message_text = 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'

        return buttons, message_text
