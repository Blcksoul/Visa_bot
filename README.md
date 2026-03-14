# Visa BOY

Telegram-бот на Python для автоматического отслеживания свободных слотов записи в визовые центры и автоматического бронирования.

Бот проверяет наличие свободных дат на сайтах VFS Global и TLScontact и может автоматически записать заявителя на ближайшую доступную дату.

---

Возможности

* Автоматический мониторинг свободных слотов
* Проверка сайта каждые 1–2 минуты
* Автоматическая запись на появившийся слот
* Поддержка нескольких заявителей
* Автоматическое заполнение формы записи
* Уведомления в Telegram после успешной записи
* Возможность отмены записи
* Ручная проверка слотов
* Работа 24/7


* Python 3.11
* aiogram 
* APScheduler 
* Playwright / HTTP scraping
* SQLite 
* Docker 


 
visa-bot/
│
├── bot.py
├── config.py
├── database.py
├── scheduler.py
│
├── handlers/
│   ├── start.py
│   ├── applicants.py
│   ├── bookings.py
│
├── services/
│   ├── slot_checker.py
│   ├── booking_service.py
│
├── utils/
│   ├── helpers.py
│
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
