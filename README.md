# Wallet API

## Описание проекта
<!-- Кратко о проекте, его назначении и основных функциях -->

## Стек технологий
- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker / Docker Compose

## Установка
Клонирование проекта: https://github.com/VladimirKBG/WalletService

## Локальный запуск
<!-- Инструкции по установке зависимостей, запуску сервера без Docker -->

## Запуск через Docker compose
### Запуск в тестовом режиме
При помощи команды из корня проекта:

docker compose -f docker-compose.common.yml -f docker-compose.test.yml up --build

При тестовом запуске прогоняются тесты из папки тест на тестовой бд.

### Запуск в рабочем режиме:
При помощи команды из корня проекта:

docker compose -f docker-compose.common.yml -f docker-compose.prod.yml up --build

При первом запуске необходимо установить флаг RUN_MIGRATIONS: True 
в файле docker-compose.prod.yml для создания таблиц в бд. 
При запуске приложение слушает http://localhost:8000

## Описание ендпоинтов

### GET /
**Описание:** Статус работы приложения

**Пример запроса:**
```bash
curl -X GET http://localhost:8000/
```

### GET /wallets
**Описание:** Список всех имеющихся кошельков (для демо).

**Пример запроса:**
```bash
curl -v -X GET http://localhost:8000/wallets
```

### POST /wallets/
**Описание:** Создание кошелька с указанным id (для демо).

**Пример запроса:**
```bash
curl -v -X POST http://localhost:8000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{"id": "00000000-0000-0000-0000-000000000001", "balance": 0}'
```

### GET /wallets/{wallet-id}
**Описание:** Баланс и метадата указанного кошелька.

**Пример запроса:**
```bash
curl -v -X GET http://localhost:8000/wallets/00000000-0000-0000-0000-000000000001
```

### POST /wallets/{wallet-id}/operation
**Описание:** Изменение баланса кошелька.

**Примеры запроса:**
```bash
curl -v -X POST http://localhost:8000/api/v1/wallets/00000000-0000-0000-0000-000000000001/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "DEPOSIT", "amount": 1000}'
```
```bash
curl -v -X POST http://localhost:8000/api/v1/wallets/00000000-0000-0000-0000-000000000001/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "WITHDRAW", "amount": 700}'
```

### GET /wallets/{wallet-id}/operation
**Описание:** Получить список последних операций над данным кошельком.

**Пример запроса:**
```bash
curl -v -X GET http://localhost:8000/api/v1/wallets/00000000-0000-0000-0000-000000000001
```
