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
ER2SQL-WEB/
├── backend/
│   ├── app/
│   │   ├── converters/
│   │   │   ├── __init__.py
│   │   │   ├── erd_converter.py
│   │   │   ├── graphml_converter.py
│   │   │   └── xml_converter.py
│   │   ├── validator/
│   │   │   ├── __init__.py
│   │   │   ├── ast_checks.py
│   │   │   ├── download_model.py
│   │   │   └── validator.py
│   │   ├── config.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── models/
│   ├── tests/
│   │   ├── test_erd_converter.py
│   │   ├── test_graphml_converter.py
│   │   ├── test_xml_converter.py
│   │   └── run_tests.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── node_modules/
│   ├── src/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
└── └── vite.config.js

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
