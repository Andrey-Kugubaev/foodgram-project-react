## Продуктовый помощник foodgram-project

**foodgram** — онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Перед началом работы предоставляется репозиторий `foodgram-project-react`; в нём подготовлен фронтенд (**HTML**-шаблоны и **JS**-код) и структура приложения студентами веб-факультета Яндекс.Практикума

### Инструкция по запуску:
- Склонируйте проект `git clone https://github.com/Andrey-Kugubaev/foodgram-project-react.git` 
- установите и активируйте виртуальное окружение
`python -m venv venv (или python3 -m venv venv) / source venv/Scripts/activate (или source venv/bin/activate)`
- установите зависимости `pip install -r requirements.txt`
- создайте файл `.env`, где пропишите ключ для _settings.py_
- создать базу данных и выполнить миграции `python manage.py makemigrations`
`python manage.py migrate`
- запустите сервер `python manage.py runserver`
