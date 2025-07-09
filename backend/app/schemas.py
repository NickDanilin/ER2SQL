# backend/app/schemas.py
from typing import List, Optional
from pydantic import BaseModel

class ConvertResponse(BaseModel):
    sql: List[str]

class LintIssue(BaseModel):
    code: str
    line: Optional[int]
    pos:  Optional[int]
    description: str

class ValidateRequest(BaseModel):
    sql: str

class ValidateResponse(BaseModel):
    lint_issues: List[LintIssue]
    sqlite_error: Optional[str]
    ast_messages: List[str]
    llm_report: List[str]
