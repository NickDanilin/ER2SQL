# backend/app/validator/ast_checks.py
from typing import List
from sqlglot import expressions, parse_one

def run_ast_checks(tree: expressions.Expression) -> List[str]:
    """
    AST-проверки на:
      1) наличие PRIMARY KEY (inline или table-level),
      2) дубли имён столбцов,
      3) отсутствие столбцов (пустая таблица).
    """
    messages: List[str] = []

    # Сначала собираем карту таблица → список её столбцов
    table_columns = {}
    for create in tree.find_all(expressions.Create):
        # Получаем имя таблицы
        tbl_node = create.this
        table = getattr(tbl_node, "name", None) or getattr(tbl_node, "this", str(tbl_node))

        # Сбор всех ColumnDef внутри этого CREATE
        cols = []
        for col in create.find_all(expressions.ColumnDef):
            # Имя столбца может быть в col.this.name или col.this.this
            name = getattr(col.this, "name", None) or getattr(col.this, "this", None)
            if name:
                cols.append(name)
        table_columns[table] = cols

    # Далее пробегаем каждую CREATE и выполняем проверки
    for create in tree.find_all(expressions.Create):
        tbl_node = create.this
        table = getattr(tbl_node, "name", None) or getattr(tbl_node, "this", str(tbl_node))
        cols = table_columns.get(table, [])

        # 1) Проверка на PRIMARY KEY
        has_pk = False
        # — ищем любой узел PrimaryKey
        for node in create.walk():
            if isinstance(node, expressions.PrimaryKey):
                has_pk = True
                break
        # — fallback: смотрим есть ли “PRIMARY KEY” в исходном SQL этого CREATE
        if not has_pk:
            raw_sql = create.sql(dialect="sqlite")  # или просто create.sql()
            if "PRIMARY KEY" in raw_sql.upper():
                has_pk = True

        if not has_pk:
            cols_str = ", ".join(cols)
            messages.append(f"Таблица {table} ({cols_str}) без PRIMARY KEY")

        # 2) Проверка на дубли имён столбцов
        seen = set()
        for name in cols:
            if cols.count(name) > 1 and name not in seen:
                messages.append(f"В таблице {table} дублируется имя столбца {name}")
                seen.add(name)

        # 3) Проверка на отсутствие столбцов
        if not cols:
            messages.append(f"Таблица {table} не содержит ни одного столбца")

    return messages
