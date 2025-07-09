import xml.etree.ElementTree as ET
from collections import defaultdict


def parse_drawio_xml(file_path):
    """Конвертирует XML из Draw.io в SQL с FOREIGN KEY через ALTER TABLE"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Namespace для Draw.io
        ns = {'mx': 'http://schemas.microsoft.com/office/2006/01/customui'}

        tables = {}
        relationships = []

        # 1. Парсинг таблиц
        for cell in root.findall('.//mxCell', ns):
            if cell.get('style', '').startswith('shape=table'):
                table_id = cell.get('id')
                value = cell.get('value', '')

                if value:
                    # Очистка HTML-тегов и разбор структуры
                    clean_value = value.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
                    parts = [p.strip() for p in clean_value.split('\n') if p.strip()]

                    if parts:
                        table_name = parts[0]
                        columns = []
                        pk = None

                        for part in parts[1:]:
                            if part.startswith('PK:'):
                                pk = part.split(':')[1].strip()
                            elif ':' in part:
                                col_name, col_type = map(str.strip, part.split(':', 1))
                                columns.append((col_name, col_type))
                            else:
                                columns.append((part, 'VARCHAR(255)'))

                        tables[table_id] = {
                            'name': table_name,
                            'columns': columns,
                            'pk': pk or (columns[0][0] if columns else 'id'),
                            'fk_columns': []
                        }

        # 2. Парсинг связей
        for edge in root.findall('.//mxCell', ns):
            if edge.get('edge') == '1':
                source = edge.get('source')
                target = edge.get('target')

                if source in tables and target in tables:
                    target_table = tables[target]['name']
                    target_pk = tables[target]['pk']
                    fk_column = f"{target_table.lower()}_id"

                    # Добавляем FK колонку в исходную таблицу
                    tables[source]['fk_columns'].append({
                        'name': fk_column,
                        'ref_table': target_table,
                        'ref_column': target_pk
                    })

                    relationships.append({
                        'source_table': tables[source]['name'],
                        'source_column': fk_column,
                        'target_table': target_table,
                        'target_column': target_pk
                    })

        # 3. Генерация SQL
        sql_commands = []
        type_mapping = {
            'int': 'INTEGER',
            'integer': 'INTEGER',
            'str': 'VARCHAR(255)',
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'date': 'DATE',
            'datetime': 'TIMESTAMP',
            'bool': 'BOOLEAN',
            'float': 'FLOAT',
            'number': 'NUMERIC'
        }

        # Сначала создаем все таблицы без FK constraints
        for table in tables.values():
            if not table['columns']:
                continue

            columns = []

            # Обычные колонки
            for col_name, col_type in table['columns']:
                sql_type = type_mapping.get(col_type.lower(), 'VARCHAR(255)')
                if col_name == table['pk']:
                    columns.append(f"{col_name} {sql_type} PRIMARY KEY")
                else:
                    columns.append(f"{col_name} {sql_type}")

            # Колонки для FK (без constraints)
            for fk in table['fk_columns']:
                columns.append(f"{fk['name']} INTEGER")

            sql_commands.append(
                f"CREATE TABLE {table['name']} (\n    " +
                ",\n    ".join(columns) +
                "\n);"
            )

        # Затем добавляем FOREIGN KEY через ALTER TABLE
        for rel in relationships:
            sql_commands.append(
                f"ALTER TABLE {rel['source_table']} "
                f"ADD FOREIGN KEY ({rel['source_column']}) "
                f"REFERENCES {rel['target_table']}({rel['target_column']});"
            )

        return sql_commands if sql_commands else ["Не обнаружено таблиц"]

    except Exception as e:
        return [f"Ошибка: {str(e)}"]