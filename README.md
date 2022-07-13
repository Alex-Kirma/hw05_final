# Социальная сеть Yatube
## Технологии
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/p?color=brightgreen)
![PyPI - Python Version](https://img.shields.io/badge/Django-3.2-brightgreen)
+ Ргистрация пользователй
  > Реализована регистрация и верификация пользователей, восстановление и смена пароля при помощи почты.

+ Система комментирования записей
+ > На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи.

+ Клонировать репозиторий.
```bash
git clone git@github.com:Alex-Kirma/hw05_final.git
```
+ Установить и активировать виртуальное окружение(версия python 3.7).
```bash
python3 -3.7 -m venv venv
. venv/scripts/activate
```
+ Обновить инсталятор pip.
```bash
python -m pip install --upgrade pip.
```
+ Установить зависимости из файла requirements.txt.
```bash
pip install -r requirements.txt
```
+ Сделать миграции.
```bash
python manage.py migrate
```
+ Создать супер пользователя.
```bash
python manage.py createsuperuser
```
+ Запустить проект:
```bash
python manage.py runserver
```
# Автор: Кырма Алексей.
