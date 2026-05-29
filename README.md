# Как запустить локально через Docker Compose

Для локального запуска проекта нужен установленный Docker Desktop.

## 1. Создайте файл .env

В корне проекта создайте файл .env:

touch .env

Добавьте в него переменные окружения:

DEBUG=True
SECRET_KEY=your-secret-key
ROLLBAR_TOKEN=
ROLLBAR_ENVIRONMENT=development
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

Для локальной разработки ROLLBAR_TOKEN можно оставить пустым.

## 2. Соберите и запустите контейнеры
docker compose up --build

После запуска сайт будет доступен по адресу:

http://127.0.0.1:8000

Админка Django будет доступна по адресу:

http://127.0.0.1:8000/admin/
## 3. Примените миграции

В отдельной вкладке терминала выполните:

docker compose exec backend python manage.py migrate
## 4. Создайте администратора
docker compose exec backend python manage.py createsuperuser

## 5. Frontend

Frontend собирается в отдельном контейнере frontend с помощью Parcel.

Готовые frontend-файлы попадают в каталог:

bundles/

Django использует этот каталог для раздачи static-файлов.

## 6. Media-файлы

Загруженные через админку изображения сохраняются в каталоге:

media/

Каталог media подключён в Docker Compose как volume, поэтому файлы не теряются при обычном перезапуске контейнеров.

Не используйте команду:

docker compose down -v

если хотите сохранить загруженные media-файлы, потому что флаг -v удаляет Docker volumes.