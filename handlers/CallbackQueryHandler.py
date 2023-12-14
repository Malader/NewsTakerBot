import telethon
from telethon import Button


class CallbackQueryHandler:
    def __init__(self, bot_client, subscription_manager, button_manager, text_processor, news_fetcher, message_handler):
        self.bot_client = bot_client
        self.subscription_manager = subscription_manager
        self.button_manager = button_manager
        self.text_processor = text_processor
        self.news_fetcher = news_fetcher
        self.message_handler = message_handler

    async def handle_callback_query(self, event):
        user_id = event.sender_id
        data = event.data.decode('utf-8')

        # Убедимся, что у пользователя есть запись в словаре интересов
        self.subscription_manager.initialize_user_interests(user_id)
        try:
            if data.startswith('unsubscribe_'):
                # Обработка отписки от интереса
                interest_to_remove = data.split('_')[1]
                if self.subscription_manager.is_user_subscribed_to_interest(user_id, interest_to_remove):
                    # Сначала отправляем подтверждение обработки callback
                    await event.answer(f'Вы отписались от темы "{interest_to_remove}".', alert=True)

                    self.subscription_manager.remove_user_interest(user_id, interest_to_remove)
                    current_subscriptions = self.subscription_manager.get_user_interests(user_id)

                    if current_subscriptions:
                        buttons = [[Button.inline(
                            f"{self.subscription_manager.theme_emojis.get(interest, '')} Отписаться от {interest}",
                            f"unsubscribe_{interest}")]
                                   for interest in current_subscriptions]
                        buttons.append([Button.inline("❌ Отписаться от всех тем", "unsubscribe")])
                        buttons.append([Button.inline("➕ Добавить темы", "add_interests")])
                        message_text = 'Вы подписаны на следующие темы:'
                    else:
                        # Если нет текущих подписок, обновляем сообщение соответственно
                        buttons = [[Button.inline("➕ Добавить темы", "add_interests")]]
                        message_text = 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'

                    try:
                        await event.edit(message_text, buttons=buttons)
                    except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                        # Это исключение означает, что сообщение уже содержит актуальную информацию
                        pass  # Можно проигнорировать это исключение
                else:
                    # Если пользователь не был подписан, отправляем подтверждение обработки callback
                    await event.answer('Вы не были подписаны на эту тему.', alert=True)

            elif data.startswith('removechannel_'):
                # Обработка удаления канала
                channel_to_remove = '@' + data[len('removechannel_'):]
                user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)
                if channel_to_remove in user_subscriptions:
                    user_subscriptions.discard(channel_to_remove)
                    self.subscription_manager.set_user_subscriptions(user_id, user_subscriptions)
                    # Обновляем список каналов после удаления
                    if user_subscriptions:
                        buttons = [[Button.inline(f"Удалить {channel}", f"removechannel_{channel.replace('@', '')}")]
                                   for channel in sorted(user_subscriptions[user_id])]
                        message_text = f"Вы подписаны на следующие каналы:\n{', '.join(sorted(user_subscriptions[user_id]))}"
                        await event.edit(message_text, buttons=buttons)
                    else:
                        await event.edit("Вы не подписаны ни на один канал.")
                else:
                    await event.answer(f"Канал {channel_to_remove} не найден в вашем списке подписок.", alert=True)

            elif data == 'unsubscribe':
                # Обработка отписки от всех тем
                if self.subscription_manager.get_user_interests(user_id):
                    self.subscription_manager.clear_user_interests(user_id)
                    buttons = [[Button.inline("➕ Добавить темы", "add_interests")]]
                    message_text = 'Вы не подписаны ни на одну тему. Используйте /subscribe для добавления.'
                    await event.edit(message_text, buttons=buttons)
                    await event.answer('Вы успешно отписались от всех тем.', alert=True)
                else:
                    await event.answer('Вы не были подписаны на темы.', alert=True)

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
                try:
                    await event.edit('Выберите темы, на которые вы хотите подписаться:', buttons=buttons)
                except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                    pass

            elif event.data.decode('utf-8') == 'subscribe_all':
                await self.message_handler.subscribe_all(event)  # вызов функции подписки на все темы

            elif data == 'finish_subscription':
                # Отредактируем сообщение, показывая, что выбор тем завершен
                try:
                    await event.edit(
                        'Выбор тем завершен. Используйте /mysubscriptions для управления темами или команду /news чтобы посмотреть все новости по выбранной тематике.')
                except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                    # Если содержимое сообщения не изменилось, отправляем пользователю уведомление
                    await event.answer('Выбор тем уже завершен.', alert=True)

            elif data == 'show_all_news':
                # user_subscriptions = self.subscription_manager.get_user_subscriptions(user_id)
                # if user_id not in user_subscriptions or not user_subscriptions[user_id]:
                if not self.subscription_manager.get_user_subscriptions(user_id):
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
                if not self.subscription_manager.is_user_subscribed_to_interest(user_id, data):
                    self.subscription_manager.add_user_interest(user_id, data)
                    buttons = self.button_manager.create_subscription_buttons(user_id)
                    await event.edit('Вы подписались на тему. Вы можете выбрать остальные темы, на которые вы хотите подписаться:', buttons=buttons)
                    await event.answer(f'Вы подписались на тему "{data}".', alert=True)
                else:
                    await event.answer(f'Вы уже подписаны на тему "{data}".', alert=True)

            else:
                await event.answer('Неверная команда.', alert=True)

        except telethon.errors.rpcerrorlist.QueryIdInvalidError:
            # Игнорировать ошибку, если запрос уже обработан или недействителен
            print("QueryIdInvalidError caught, ignoring")
