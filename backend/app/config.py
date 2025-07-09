import os

# Модель для семантического анализа
CODET5_MODEL = os.getenv("CODET5_MODEL", "Salesforce/codet5-base")

# Настройки сервера
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
