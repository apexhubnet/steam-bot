# Steam Player Monitoring Bot 📊

Python-бот для получения количества игроков в Steam играх. Бот периодически запрашивает данные через Steam API и сохраняет статистику в базу данных для последующего анализа.

## 📦 Структура проекта
```
├── docker-compose.yml       # Конфигурация Docker
├── bot/
│   ├── Dockerfile           # Образ контейнера
│   ├── steam_bot.py         # Основной код бота
│   ├── requirements.txt     # Зависимости Python
│   └── .env.example         # Шаблон конфигурации
```
## ⚙️ Основной функционал
* Автоматический запрос количества игроков через Steam Web API
* Поддержка любого AppID (по умолчанию Dota 2 - 570)
* Сохранение статистики в MySQL с обработкой ошибок
* Двойная система перезапуска при сбоях

## ⚠️ Требования к базе данных

Учетная запись БД должна иметь права:
```
GRANT INSERT, SELECT ON your_database.steam_stats TO 'your_user'@'%';
```
Структура таблицы bans:
```
CREATE TABLE steam_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    appid INT NOT NULL,
    player_count INT NULL,
    error_message VARCHAR(255) NULL
);
```
## 📝 Примеры логов
```
2023-10-15 12:00:00 - INFO - Starting Steam monitoring bot
2023-10-15 12:00:00 - INFO - Monitoring AppID: 570
2023-10-15 12:00:00 - INFO - Update interval: 5 minutes
2023-10-15 12:00:00 - INFO - Fetching player count...
2023-10-15 12:00:01 - INFO - Current players: 876543
2023-10-15 12:00:01 - INFO - Data saved to DB
2023-10-15 12:00:01 - INFO - Sleeping for 300 seconds
```