import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const Spinner = () => <div className="spinner" />;

export default function App() {
  const [file, setFile] = useState(null);
  const [sql, setSql] = useState("");
  const [report, setReport] = useState(null);
  const [convertLoading, setConvertLoading] = useState(false);
  const [validateLoading, setValidateLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (e) => {
    setFile(e.target.files[0]);
    setSql("");
    setReport(null);
    setError("");
  };

  const handleConvert = async () => {
    if (!file) {
      setError("Выберите файл (.xml, .erd или .graphml)");
      return;
    }
    setConvertLoading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await axios.post("http://127.0.0.1:8000/convert", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSql(res.data.sql.join("\n"));
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setConvertLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!sql) {
      setError("Сначала нужно сгенерировать SQL");
      return;
    }
    setValidateLoading(true);
    setError("");
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/validate",
        { sql },
        { headers: { "Content-Type": "application/json" } }
      );
      // очистка LLM-отчёта
      const rawLLM = res.data.llm_report || [];
      const cleanLLM = rawLLM
        .map((line) => line.trim())
        .filter((line) => line.length > 5)
        .filter((line, i, arr) => arr.indexOf(line) === i);

      setReport({
        lint_issues: res.data.lint_issues,
        sqlite_error: res.data.sqlite_error,
        ast_messages: res.data.ast_messages,
        llm_report: cleanLLM,
      });
    } catch (e) {
      setError(
        e.response?.data?.detail ||
          JSON.stringify(e.response?.data) ||
          e.message
      );
    } finally {
      setValidateLoading(false);
    }
  };

  const downloadFile = (content, filename, mime) => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container">
      <h1>ER to SQL & Validator</h1>

      <div className="uploader">
        <input
          type="file"
          accept=".xml,.erd,.graphml"
          onChange={handleFile}
        />
        <button
          className="btn-primary"
          onClick={handleConvert}
          disabled={convertLoading}
        >
          {convertLoading && <Spinner />}
          {convertLoading ? "Конвертация..." : "Конвертировать"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {sql && (
        <section className="panel">
          <h2>Сгенерированный SQL</h2>
          <textarea readOnly value={sql} rows={10} />
          <div className="download-bar">
            <button
              className="btn-secondary"
              onClick={() => downloadFile(sql, "schema.sql", "application/sql")}
            >
              Скачать SQL
            </button>
            <button
              className="btn-primary"
              onClick={handleValidate}
              disabled={validateLoading}
            >
              {validateLoading && <Spinner />}
              {validateLoading ? "Проверка..." : "Проверить на валидность"}
            </button>
          </div>
        </section>
      )}

      {report && (
        <>
          {/* Lint Issues */}
          {report.lint_issues.length > 0 && (
            <section className="panel">
              <h2>Lint Issues</h2>
              <pre>
{report.lint_issues
  .map(
    (issue) =>
      `${issue.code}` +
      (issue.line != null
        ? ` (строка ${issue.line}${
            issue.pos != null ? `, позиция ${issue.pos}` : ""
          })`
        : "") +
      `: ${issue.description}`
  )
  .join("\n")}
              </pre>
            </section>
          )}

          {/* SQLite Error */}
          {report.sqlite_error && (
            <section className="panel">
              <h2>SQLite Error</h2>
              <pre>{report.sqlite_error}</pre>
            </section>
          )}

          {/* AST Messages */}
          {report.ast_messages.length > 0 && (
            <section className="panel">
              <h2>AST Messages</h2>
              <pre>{report.ast_messages.join("\n")}</pre>
            </section>
          )}

          {/* LLM Report */}
          {report.llm_report.length > 0 && (
            <section className="panel">
              <h2>LLM Report</h2>
              <pre>{report.llm_report.join("\n")}</pre>
            </section>
          )}

          {/* Скачать JSON-отчёт */}
          <section className="panel">
            <h2>Скачать отчёт</h2>
            <button
              className="btn-secondary"
              onClick={() =>
                downloadFile(
                  JSON.stringify(report, null, 2),
                  "report.json",
                  "application/json"
                )
              }
            >
              Скачать JSON-отчёт
            </button>
          </section>
        </>
      )}
    </div>
  );
}
