# validator.py
import sqlite3
from sqlfluff.core import Linter
from sqlglot import parse
from transformers import pipeline
import json

from ..config import CODET5_MODEL
from .ast_checks import run_ast_checks

class SQLValidator:
    def __init__(self):
        # SQLFluff для lint’а
        self.linter = Linter(dialect="sqlite")
        # CodeT5 для семантической проверки
        self.llm = pipeline("text2text-generation", model=CODET5_MODEL)
    
    def lint(self, sql: str) -> list[dict]:
        """
        Линтуем SQL через временный .sql-файл, собираем реальные номера строк,
        убираем дубли и формируем список словарей из to_dict().
        """
        import tempfile, os

        # 1) Записать SQL в файл
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sql", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(sql)
            tmp_path = tmp.name

        try:
            result = self.linter.lint_path(tmp_path)
        finally:
            os.remove(tmp_path)

        seen = set()
        issues = []
        for v in result.get_violations():
            info = v.to_dict()
            code = info.get("code") or info.get("rule_code") or ""
            line = info.get("line_no") or info.get("line")
            pos  = info.get("line_pos") or info.get("position")
            desc = info.get("description") or ""

            key = (code, line, pos, desc)
            if key in seen:
                continue
            seen.add(key)

            issues.append({
                "code": code,
                "line": line,
                "pos":  pos,
                "description": desc,
            })
        return issues

    def check_sqlite(self, sql: str) -> str | None:
        """Проверяет в SQLite-in-memory; возвращает текст ошибки или None"""
        conn = sqlite3.connect(":memory:")
        try:
            conn.executescript(sql)
            return None
        except sqlite3.DatabaseError as e:
            return str(e)
        finally:
            conn.close()

    def ast_analysis(self, sql: str) -> list[str]:
        """Запускает AST-чеки через sqlglot"""
        trees = parse(sql)
        msgs: list[str] = []
        for tree in trees:
            msgs.extend(run_ast_checks(tree))
        return msgs

    def llm_validate(self, sql: str) -> list[str]:
        """
        Run a semantic check of the SQL script via CodeT5, asking for an
        English JSON array of error messages.
        """
        prompt = """
            You are an expert SQL validator.  
            Given an SQL DDL script, return a JSON array of short English error messages.
            Each message should describe exactly one issue.

            Example 1:
            Input SQL:
            CREATE TABLE users (id INT, name TEXT PRIMARY KEY);
            Output JSON:
            []

            Example 2:
            Input SQL:
            CREATE TABLE customers (name TEXT);
            ALTER TABLE customers ADD FOREIGN KEY (name) REFERENCES other(id);
            Output JSON:
            [
            "Missing PRIMARY KEY in table customers",
            "Foreign key column 'name' does not reference an existing primary key"
            ]

            Now analyze this SQL and output ONLY the JSON array:
            """ + sql + "\n\nOutput JSON:\n"

        # generate
        out = self.llm(prompt, max_length=512, do_sample=False)
        text = out[0]["generated_text"].strip()

        # try to parse JSON
        try:
            arr = json.loads(text)
            if isinstance(arr, list) and all(isinstance(e, str) for e in arr):
                # dedupe and clean
                seen = set(); result = []
                for e in arr:
                    e = e.strip()
                    if e and e not in seen:
                        seen.add(e); result.append(e)
                return result
        except json.JSONDecodeError:
            pass

        # fallback: return entire text as single message
        return [text]