class StartHandler:
    def __init__(self, subscription_manager_instance):
        self.subscription_manager = subscription_manager_instance

    async def handle(self, event, bot_client):
        user_id = event.sender_id
        self.subscription_manager.initialize_user_subscriptions(user_id)
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
        await bot_client.send_message(user_id, welcome_message)