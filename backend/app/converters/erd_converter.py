import xml.etree.ElementTree as ET


def parse_erd(file_path):
    """Конвертирует ERD-файл в SQL"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        entities = {}
        fk_constraints = []

        # Парсим сущности
        for entity in root.findall('.//entity'):
            entity_id = entity.get('id')
            entities[entity_id] = {
                'name': entity.get('name'),
                'attributes': [],
                'fk_columns': []
            }

            for attribute in entity.findall('.//attribute'):
                entities[entity_id]['attributes'].append({
                    'name': attribute.get('name'),
                    'type': attribute.get('type', 'VARCHAR(255)'),
                    'is_pk': attribute.get('primary', 'false') == 'true'
                })

        # Парсим связи
        for relation in root.findall('.//relation'):
            if relation.get('type') == 'fk':
                fk_entity_id = relation.get('fk-ref')
                pk_entity_id = relation.get('pk-ref')

                if fk_entity_id in entities and pk_entity_id in entities:
                    fk_table = entities[fk_entity_id]['name']
                    pk_table = entities[pk_entity_id]['name']

                    # Находим PK целевой таблицы
                    pk_column = next(
                        (attr['name'] for attr in entities[pk_entity_id]['attributes'] if attr['is_pk']),
                        'id'
                    )

                    # Добавляем колонку FK
                    fk_column = f"{pk_table}_id"
                    entities[fk_entity_id]['fk_columns'].append({
                        'name': fk_column,
                        'type': 'INTEGER'
                    })

                    # Запоминаем ограничение
                    fk_constraints.append({
                        'table': fk_table,
                        'column': fk_column,
                        'target_table': pk_table,
                        'target_column': pk_column
                    })

        # Генерация SQL
        sql_commands = []
        for entity in entities.values():
            if not entity['name']:
                continue

            columns = []
            pk_columns = []

            # Атрибуты
            for attr in entity['attributes']:
                col_def = f"{attr['name']} {attr['type']}"
                if attr['is_pk']:
                    pk_columns.append(attr['name'])
                columns.append(col_def)

            # Колонки FK
            for fk in entity['fk_columns']:
                columns.append(f"{fk['name']} {fk['type']}")

            # Первичный ключ
            if pk_columns:
                columns.append(f"PRIMARY KEY ({', '.join(pk_columns)})")

            sql_commands.append(
                f"CREATE TABLE {entity['name']} (\n    " +
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