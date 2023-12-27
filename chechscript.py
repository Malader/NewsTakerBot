import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('tgbotdatabase.sqlite')
cursor = conn.cursor()

# Выполнение запроса
cursor.execute("SELECT * FROM user_channels")
rows = cursor.fetchall()

# Вывод результатов
for row in rows:
    print(row)

# Закрытие соединения
conn.close()
