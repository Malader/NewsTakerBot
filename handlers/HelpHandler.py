class HelpHandler:
    def __init__(self, bot_client):
        self.bot_client = bot_client

    async def handle(self, event):
        user_id = event.sender_id
        help_message = (
            "🆘 Команда помощи 🆘\n\n"
            "Если у вас возникли вопросы или нужна помощь, пожалуйста, свяжитесь с @Malader или с @adamishhe.\n\n"
            "Для получения информации о других командах бота используйте команду /start."
        )

        # Отправляем сообщение с информацией о помощи
        await event.respond(help_message)
