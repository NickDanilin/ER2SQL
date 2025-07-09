import xml.etree.ElementTree as ET
from collections import defaultdict


def parse_graphml(file_path):
    """Конвертирует GraphML (DBeaver) в SQL"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        ns = {
            'g': 'http://graphml.graphdrawing.org/xmlns',
            'y': 'http://www.yworks.com/xml/graphml'
        }

        tables = {}
        fk_constraints = []

        # Парсим таблицы
        for node in root.findall('.//g:node', ns):
            node_id = node.get('id')
            table_data = {
                'name': '',
                'columns': [],
                'pk': None,
                'fk_columns': []
            }

            # Название таблицы
            name_label = node.find('.//y:NodeLabel[@configuration="com.yworks.entityRelationship.label.name"]', ns)
            if name_label is not None:
                table_data['name'] = name_label.text.strip() if name_label.text else f"table_{node_id}"

            # Атрибуты
            attr_label = node.find('.//y:NodeLabel[@configuration="com.yworks.entityRelationship.label.attributes"]',
                                   ns)
            if attr_label is not None and attr_label.text:
                for col in attr_label.text.split('\n'):
                    col = col.strip()
                    if col:
                        if ':' in col:
                            col_name, col_type = map(str.strip, col.split(':', 1))
                            table_data['columns'].append((col_name, col_type))
                        else:
                            table_data['columns'].append((col, ''))

            if table_data['name']:
                tables[node_id] = table_data

        # Парсим связи
        for edge in root.findall('.//g:edge', ns):
            source_id = edge.get('source')
            target_id = edge.get('target')

            if source_id in tables and target_id in tables:
                source_table = tables[source_id]['name']
                target_table = tables[target_id]['name']
                target_pk = tables[target_id]['columns'][0][0] if tables[target_id]['columns'] else 'id'

                # Добавляем колонку FK
                fk_column = f"{target_table}_id"
                tables[source_id]['fk_columns'].append({
                    'name': fk_column,
                    'type': 'INTEGER'
                })

                # Запоминаем ограничение
                fk_constraints.append({
                    'table': source_table,
                    'column': fk_column,
                    'target_table': target_table,
                    'target_column': target_pk
                })

        # Генерация SQL
        sql_commands = []
        type_mapping = {
            'int': 'INTEGER',
            'str': 'VARCHAR(255)',
            'date': 'DATE',
            'bool': 'BOOLEAN'
        }

        for table in tables.values():
            if not table['columns']:
                continue

            columns = []

            # Атрибуты
            for i, (col_name, col_type) in enumerate(table['columns']):
                sql_type = "VARCHAR(255)"
                if col_type:
                    col_type_lower = col_type.lower()
                    for key, val in type_mapping.items():
                        if key in col_type_lower:
                            sql_type = val
                            break

                if i == 0:
                    col_def = f"{col_name} {sql_type} PRIMARY KEY"
                else:
                    col_def = f"{col_name} {sql_type}"

                columns.append(col_def)

            # Колонки FK
            for fk in table['fk_columns']:
                columns.append(f"{fk['name']} {fk['type']}")

            sql_commands.append(
                f"CREATE TABLE {table['name']} (\n    " +
                ",\n    ".join(columns) +
                "\n);"
            )

        # Внешние ключи
        for fk in fk_constraints:
            sql_commands.append(
                f"ALTER TABLE {fk['table']} "
                f"ADD FOREIGN KEY ({fk['column']}) "
                f"REFERENCES {fk['target_table']}({fk['target_column']});"
            )

        return sql_commands

    except Exception as e:
        return [f"Ошибка: {str(e)}"]