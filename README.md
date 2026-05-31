## Как запустить на сервере через Docker Compose

Проект на сервере запускается через Docker Compose.

Используются три сервиса:

* `frontend` — собирает frontend через Parcel и завершает работу;
* `backend` — запускает Django через Gunicorn;
* `nginx` — раздаёт static/media-файлы и проксирует запросы в backend.

### 1. Подготовьте сервер

На сервере должен быть установлен Docker и Docker Compose plugin.

Проверьте установку:

```bash
docker --version
docker compose version
```

### 2. Склонируйте проект

```bash
git clone https://github.com/MaksimOboznyi/star-burger.git
cd star-burger
```

Если нужно использовать отдельную ветку:

```bash
git checkout имя_ветки
```

### 3. Создайте `.env`

В корне проекта создайте файл `.env`:

```bash
nano .env
```

Пример содержимого:

```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0,server_ip_or_domain

ROLLBAR_TOKEN=your-rollbar-token
ROLLBAR_ENVIRONMENT=production

DATABASE_URL=sqlite:///db.sqlite3
```

`ROLLBAR_TOKEN` — это Project Access Token из Rollbar со scope `post_server_item`.

### 4. Запустите проект

```bash
docker compose up --build -d
```

После запуска проверьте контейнеры:

```bash
docker compose ps -a
```

Ожидаемый результат:

```text
frontend   Exited (0)
backend    Up
nginx      Up
```

`frontend` завершается после успешной сборки frontend-файлов. Это нормальное поведение.

### 5. Примените миграции

```bash
docker compose exec backend python manage.py migrate
```

### 6. Соберите static-файлы

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

Static-файлы собираются в каталог:

```text
staticfiles/
```

Nginx раздаёт их по адресу:

```text
/static/
```

### 7. Media-файлы

Загруженные через админку файлы хранятся в каталоге:

```text
media/
```

В `docker-compose.yml` каталог `media` подключён к backend и nginx как папка проекта, поэтому файлы не теряются при пересоздании контейнеров.

### 8. Проверка сайта

Проверьте сайт локально на сервере:

```bash
curl -I http://127.0.0.1:8010
```

Или откройте в браузере:

```text
http://server_ip_or_domain:8010
```

## Автоматический деплой

Для обновления проекта на сервере используется скрипт:

```bash
./deploy_star_burger.sh
```

Скрипт выполняет следующие действия:

1. Подтягивает свежий код из GitHub.
2. Пересобирает и запускает Docker Compose контейнеры.
3. Применяет миграции Django.
4. Собирает static-файлы.
5. Перезапускает nginx-контейнер.
6. Отправляет событие о деплое в Rollbar, если указан `ROLLBAR_TOKEN`.

Перед запуском убедитесь, что у скрипта есть права на выполнение:

```bash
chmod +x deploy_star_burger.sh
```

Запуск деплоя:

```bash
./deploy_star_burger.sh
```

После деплоя проверьте контейнеры:

```bash
docker compose ps -a
```

Ожидаемый результат:

```text
frontend   Exited (0)
backend    Up
nginx      Up
```

