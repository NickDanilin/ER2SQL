import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .schemas import (
    ConvertResponse,
    ValidateRequest,
    ValidateResponse,
    LintIssue,
)
from .converters.erd_converter import parse_erd
from .converters.graphml_converter import parse_graphml
from .converters.xml_converter import parse_drawio_xml
from .validator.validator import SQLValidator

app = FastAPI(title="ER2SQL Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validator = SQLValidator()

def _save_temp(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        return tmp.name

@app.post("/convert", response_model=ConvertResponse)
async def convert(file: UploadFile = File(...)):
    tmp_path = _save_temp(file)
    try:
        if tmp_path.endswith(".erd"):
            sql = parse_erd(tmp_path)
        elif tmp_path.endswith(".graphml"):
            sql = parse_graphml(tmp_path)
        elif tmp_path.endswith(".xml"):
            sql = parse_drawio_xml(tmp_path)
        else:
            raise HTTPException(400, "Неподдерживаемый формат файла")
    finally:
        os.remove(tmp_path)

    return {"sql": sql}

@app.post("/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    sql = req.sql

    # 1. Статический анализ (SQLFluff)
    lint_raw = validator.lint(sql)
    lint = [
        LintIssue(
            code=issue.get("code",""),
            line=issue.get("line_no") or issue.get("line") or 0,
            pos=issue.get("line_pos") or issue.get("position") or 0,
            description=issue.get("description","")
        )
        for issue in lint_raw
    ]

    # 2. Динамическая проверка (SQLite)
    sqlite_err = validator.check_sqlite(sql)

    # 3. AST-анализ (sqlglot)
    ast_msgs = validator.ast_analysis(sql)

    # 4. LLM-проверка (CodeT5)
    llm_report = validator.llm_validate(sql)

    return ValidateResponse(
        lint_issues=lint,
        sqlite_error=sqlite_err,
        ast_messages=ast_msgs,
        llm_report=llm_report,
    )

@app.post("/convert_and_validate", response_model=ValidateResponse)
async def convert_and_validate(file: UploadFile = File(...)):
    conv = await convert(file)
    joined_sql = "\n".join(conv.sql)
    return await validate(ValidateRequest(sql=joined_sql))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
