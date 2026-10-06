# Умный город — экосистема микросервисов

Учебный проект: распределённая система управления городской инфраструктурой.
Сервисы независимы, у каждого своя БД, общаются только по HTTP.

**Участники команды:** _Фамилия1, Фамилия2, Фамилия3_ <!-- TODO: вписать -->

## Стек
Python 3.11, FastAPI, PostgreSQL 16, SQLAlchemy 2 (async, asyncpg), httpx, Vue 3, Docker Compose, Nginx.

## Запуск

```bash
cp services/auth-service/config.env.example services/auth-service/config.env   # и поменять SECRET_KEY
docker compose up --build
```

Всё доступно через Nginx на `http://localhost:8088`:

| Сервис | Префикс | Swagger |
|---|---|---|
| Identity & Auth | `/api/auth/` | http://localhost:8088/api/auth/docs |
| Transport | `/api/transport/` | http://localhost:8088/api/transport/docs |
| Utility (ЖКХ) | `/api/utility/` | http://localhost:8088/api/utility/docs |

Nginx срезает префикс, поэтому внутри сервисов роуты как в ТЗ (`/vehicles`, `/issues`, …).

## Договорённости между сервисами

- Внутренний порт любого сервиса — `8000`, обращение по имени из compose (`http://auth_service:8000`).
- **Аутентификация.** Клиент получает JWT в `POST /api/auth/auth/login` и передаёт его заголовком
  `Authorization: Bearer <token>`. Остальные сервисы проверяют токен запросом
  `GET http://auth_service:8000/users/me` и берут оттуда `id` пользователя.
- **Уведомления.** Сервисы шлют `POST {NOTIFICATION_SERVICE_URL}/notifications`:
  ```json
  {"user_id": 1, "title": "Заголовок", "message": "Текст", "source": "transport"}
  ```
  Если Notification Service недоступен (или `NOTIFICATION_SERVICE_URL` не задан), основная операция
  всё равно выполняется, в лог пишется предупреждение.
- **Ошибки** — стандартный формат FastAPI `{"detail": "..."}`:
  `400` неверные данные, `401` нет или плохой токен, `403` чужой объект, `404` не найдено,
  `409` конфликт (нет мест, заявка закрыта), `422` валидация, `503` недоступна БД или auth-сервис.
- Каждый сервис отвечает на `GET /health`.

---

## 2. Transport Service

### Endpoints
| Метод | Путь | JWT | Описание |
|---|---|---|---|
| GET | `/vehicles?type=&route=&status=` | — | Список транспорта с координатами |
| GET | `/vehicles/{id}` | — | Одна единица транспорта |
| GET | `/parking` | — | Парковки и число свободных мест сейчас |
| GET | `/parking/{id}` | — | Одна парковка |
| POST | `/parking/{id}/reserve` | ✔ | Бронирование места |
| GET | `/reservations/my` | ✔ | Мои брони |
| POST | `/reservations/{id}/cancel` | ✔ | Отмена своей брони |

Пример брони:
```json
POST /api/transport/parking/1/reserve
{"car_number": "А123ВС38", "hours": 2, "start_time": "2026-10-05T10:00:00+08:00"}
```
`start_time` можно не указывать, тогда бронь начинается сейчас. Время без часового пояса считается UTC.
Строка парковки блокируется через `SELECT ... FOR UPDATE`, поэтому два параллельных запроса не займут одно место.

### База данных `transport`
```
vehicles                       parkings                      parking_reservations
-----------------------        ------------------------      ---------------------------------
id            PK               id             PK      1 ──< id            PK
vehicle_type  varchar(20)      name           varchar(100)   parking_id    FK -> parkings.id
route_number  varchar(10)      address        varchar(255)   user_id       int  (id из Auth)
plate_number  varchar(20) UQ   latitude       float          car_number    varchar(20)
latitude      float            longitude      float          start_time    timestamptz
longitude     float            total_spots    int  (>0)      end_time      timestamptz (> start)
status        varchar(20)      price_per_hour numeric(10,2)  total_price   numeric(10,2)
updated_at    timestamptz                                    status        active|cancelled
                                                             created_at    timestamptz
```
При первом запуске таблицы заполняются тестовыми данными: 8 единиц транспорта и 4 парковки (Иркутск).

---

## 3. Utility Service (ЖКХ)

### Endpoints
| Метод | Путь | JWT | Описание |
|---|---|---|---|
| POST | `/issues` | ✔ | Создание заявки |
| GET | `/issues?status=&category=&mine=` | ✔ | Список заявок (`mine=true` — только мои) |
| GET | `/issues/{id}` | ✔ | Заявка с историей статусов |
| PUT | `/issues/{id}` | ✔ | Обновление статуса |

Категории: `water`, `heating`, `electricity`, `gas`, `garbage`, `roads`, `other`.
Статусы: `new` → `in_progress` → `resolved` / `rejected`. Из `resolved` и `rejected` статус не меняется (409).

```json
POST /api/utility/issues
{"title": "Нет горячей воды", "description": "Со вчерашнего вечера", "address": "ул. Ленина, 5", "category": "water"}

PUT /api/utility/issues/1
{"status": "in_progress", "comment": "Бригада выехала"}
```
При создании заявки и смене статуса автору отправляется уведомление.

### База данных `utility`
```
issues                              issue_status_history
-------------------------------     ------------------------------------
id           PK              1 ──<  id          PK
user_id      int (id из Auth)       issue_id    FK -> issues.id (CASCADE)
title        varchar(200)           old_status  varchar(20) NULL
description  text                   new_status  varchar(20)
address      varchar(255)           changed_by  int (user_id)
category     varchar(30)            comment     text NULL
status       varchar(20)            changed_at  timestamptz
created_at   timestamptz
updated_at   timestamptz
```

`user_id` хранится без внешнего ключа: пользователи живут в БД другого сервиса,
а прямые связи между БД сервисов запрещены.
