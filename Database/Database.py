import sqlite3


class Database:
    def __init__(self, db_file):
        """Инициализация подключения к базе данных."""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        """Создание таблиц, если они еще не созданы."""
        create_interests_table = """
        CREATE TABLE IF NOT EXISTS user_interests (
            user_id INTEGER PRIMARY KEY,
            interests TEXT
        )"""
        create_channels_table = """
        CREATE TABLE IF NOT EXISTS user_channels (
            user_id INTEGER PRIMARY KEY,
            channels TEXT
        )"""
        self.cursor.execute(create_interests_table)
        self.cursor.execute(create_channels_table)
        self.conn.commit()

    def add_user_interests(self, user_id, interests):
        interests_str = ','.join(interests) if interests else None
        self.cursor.execute("INSERT OR REPLACE INTO user_interests (user_id, interests) VALUES (?, ?)",
                            (user_id, interests_str))
        self.conn.commit()

    def get_user_interests(self, user_id):
        """Получение интересов пользователя."""
        self.cursor.execute("SELECT interests FROM user_interests WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result and result[0]:  # Добавлено условие для проверки, что результат не None и не пустая строка
            return result[0].split(',')
        else:
            return []  # Возвращаем пустой список, если нет интересов

    def add_user_channels(self, user_id, channels):
        """Добавление каналов пользователя."""
        channels_string = ','.join(channels)  # Преобразуем список каналов в строку
        self.cursor.execute("INSERT OR REPLACE INTO user_channels (user_id, channels) VALUES (?, ?)",
                            (user_id, channels_string))
        self.conn.commit()

    def get_user_channels(self, user_id):
        """Получение каналов пользователя."""
        self.cursor.execute("SELECT channels FROM user_channels WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result and result[0]:  # Добавлено условие для проверки, что результат не None и не пустая строка
            return result[0].split(',')
        else:
            return []  # Возвращаем пустой список, если нет интересов

    def remove_user_channel(self, user_id, channel):
        """Удаление канала из списка подписок пользователя."""
        user_channels = self.get_user_channels(user_id)
        if channel in user_channels:
            user_channels.remove(channel)
            self.add_user_channels(user_id, user_channels)

    def remove_user_channels(self, user_id):
        """Удаление всех каналов пользователя из базы данных."""
        self.cursor.execute("DELETE FROM user_channels WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def clear_user_interests(self, user_id):
        """Очищение всех интересов пользователя."""
        self.cursor.execute("DELETE FROM user_interests WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def close(self):
        """Закрытие соединения с базой данных."""
        self.conn.close()

    def remove_user_interests(self, user_id):
        """Удаление всех интересов пользователя."""
        self.cursor.execute("DELETE FROM user_interests WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def update_user_interests(self, user_id, interests):
        """Обновление интересов пользователя."""
        self.cursor.execute("UPDATE user_interests SET interests = ? WHERE user_id = ?",
                            (','.join(interests), user_id))
        self.conn.commit()
