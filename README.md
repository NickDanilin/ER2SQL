# ER→SQL & Validator

Простой веб-сервис для конвертации ER-диаграмм (XML, GraphML, .erd) в SQL-DDL и последующей валидации скрипта.

---

## Функциональность

- Загрузка схемы базы данных в формате `.xml`, `.graphml` или `.erd`  
- Генерация SQL-DDL (CREATE TABLE + FOREIGN KEY)  
- Статическая проверка через SQLFluff (lint)  
- Динамическая проверка в SQLite in-memory  
- AST-валидация через SQLGlot (наличие PRIMARY KEY, дублирование колонок и т. п.)  
- Семантический анализ через CodeT5 (LLM-отчёт)  

---

## Структура проекта
```
er2sql-web/
├─ backend/ # FastAPI + Python-валидации
│ ├─ app/
│ │ ├─ converters/ # парсеры ER-диаграмм → SQL ← часть выполнена Белявской Ариной
│ │ ├─ validator/ # SQLFluff, SQLite, AST, LLM
│ │ ├─ schemas.py # Pydantic-модели
│ │ └─ main.py # точка входа FastAPI
│ ├─ requirements.txt
│ └─ venv/ # виртуальное окружение (необязательно)
└─ frontend/ # React + Vite
├─ index.html
├─ package.json
├─ vite.config.js
└─ src/
├─ App.jsx
└─ App.css
```

Конвертер ERD/GraphML/XML → SQL разработан **Белявской Ариной**.

---

## Руководство и консультации

- **Руководитель практики:**  
  Туральчук Константин Анатольевич  
- **Консультант практики:**  
  Андрианова Екатерина Евгеньевна  

---

## Требования

- Python 3.10+  
- Node.js 16+ и npm  
- (опционально) Git для контроля версий  

---

## Установка и запуск

### Backend

```
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger-UI будет доступен по адресу
http://127.0.0.1:8000/docs

### Frontend

```
cd frontend
npm install
npm run dev
```

React-приложение откроется по адресу
http://localhost:5173

## Использование
1. Откройте http://localhost:5173

2. Нажмите «Выберите файл», загрузите схему (.xml/.erd/.graphml)

3. Нажмите «Конвертировать» — появится SQL-скрипт

4. Нажмите «Проверить на валидность» — увидите подробный отчёт

5. Скачайте SQL (schema.sql) и JSON-отчёт по кнопкам

## Тесты
```
cd backend
# Windows:
venv\Scripts\activate.bat

pytest -v
```

## Деплой (опционально)

1. Собрать фронтенд:
```
cd frontend
npm run build
```
2. Отдавать статичные файлы через Nginx или FastAPI (StaticFiles)
3. Запуск бэкенда в продакшене (Gunicorn + Uvicorn workers):
```
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
