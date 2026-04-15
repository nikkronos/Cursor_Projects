from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
import json
import threading

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine, get_db
from app.entities import AnalysisRecord, BatchJob, BatchJobItem
from app.schemas import (
    AnalyzeRequest,
    AnalysisInsights,
    AnalysisListItem,
    AnalysisResponse,
    BatchAnalyzeRequest,
    BatchItemResponse,
    BatchJobListItem,
    BatchJobResponse,
)
from app.services.analyzer import analyze_payload
from app.services.exporters import GoogleExportService
from app.services.instagram_client import InstagramClientService
from app.services.report_export import export_report_to_docx, export_report_to_txt


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inst Content Intelligence", version="0.1.0")
ig_service = InstagramClientService()
google_export = GoogleExportService()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Inst Analyzer</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 24px auto; line-height: 1.5; }
    input, button { padding: 10px; margin: 4px 0; }
    input[type=text] { width: 100%; }
    pre { background: #f4f4f4; padding: 12px; overflow: auto; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }
    th { background: #f7f7f7; }
    .muted { color: #666; font-size: 12px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 8px; margin: 8px 0 12px; }
    .kpi-card { border: 1px solid #ddd; border-radius: 8px; padding: 8px; background: #fafafa; }
    .kpi-label { font-size: 12px; color: #555; }
    .kpi-value { font-size: 18px; font-weight: 700; }
    .badge { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    .badge-completed { background: #e8f8ee; color: #1f7a39; }
    .badge-completed_with_warnings { background: #fff8e6; color: #9a6700; }
    .badge-running { background: #e7f1ff; color: #1f5fbf; }
    .badge-failed { background: #ffeaea; color: #b42318; }
    .badge-queued { background: #f0f0f0; color: #555; }
  </style>
</head>
<body>
  <h1>Instagram Analyzer MVP</h1>
  <div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-label">Всего анализов</div><div id="kpi_total_analyses" class="kpi-value">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Последний автор</div><div id="kpi_last_author" class="kpi-value" style="font-size:14px;">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Средний hook score</div><div id="kpi_avg_hook" class="kpi-value">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Последний batch</div><div id="kpi_last_batch" class="kpi-value" style="font-size:14px;">-</div></div>
  </div>
  <p>Вставь ссылку на пост и запусти анализ.</p>
  <input id="url" type="text" placeholder="https://www.instagram.com/p/..." />
  <div>
    <label>Лимит комментариев: <input id="comments_limit" type="number" value="200" min="10" max="1000"/></label>
  </div>
  <div>
    <label><input id="include_replies" type="checkbox" /> Включить ответы в комментариях</label>
  </div>
  <div>
    <label><input id="export_google" type="checkbox" /> Экспорт в Google (если настроено)</label>
  </div>
  <button onclick="run()">Анализировать</button>
  <div id="exports" style="margin-top: 8px;"></div>
  <pre id="output">Результат появится здесь...</pre>
  <h2>История анализов</h2>
  <div>
    <input id="history_q" type="text" placeholder="Поиск по URL/shortcode/author" />
    <input id="history_author" type="text" placeholder="Фильтр по автору" />
    <select id="history_media_type">
      <option value="">Все типы</option>
      <option value="1">Фото</option>
      <option value="2">Видео/Reel</option>
      <option value="8">Карусель</option>
    </select>
    <button onclick="loadHistory()">Обновить историю</button>
    <button onclick="clearHistory()">Очистить историю</button>
  </div>
  <div class="muted">Показаны последние 30 записей по фильтру.</div>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Дата</th>
        <th>Автор</th>
        <th>Тип</th>
        <th>Shortcode</th>
        <th>Ссылка</th>
        <th>Действия</th>
      </tr>
    </thead>
    <tbody id="history_tbody">
      <tr><td colspan="7">История загрузится здесь...</td></tr>
    </tbody>
  </table>
  <details style="margin-top:8px;">
    <summary>Raw JSON history (debug)</summary>
    <pre id="history_output">[]</pre>
  </details>
  <hr />
  <h2>Batch анализ (до 30 ссылок)</h2>
  <p>Вставь ссылки по одной в каждой строке и запусти пакетный анализ.</p>
  <input id="batch_file" type="file" accept=".txt,.csv" />
  <button onclick="loadBatchFile()">Загрузить ссылки из файла</button>
  <textarea id="batch_urls" rows="8" style="width: 100%;" placeholder="https://www.instagram.com/p/...&#10;https://www.instagram.com/p/..."></textarea>
  <div>
    <label>Ретраи на ссылку: <input id="batch_retries" type="number" value="2" min="1" max="5"/></label>
  </div>
  <button onclick="runBatch()">Запустить Batch</button>
  <button onclick="retryFailedBatch()">Retry failed only</button>
  <button onclick="downloadBatchCsv()">Скачать Batch CSV</button>
  <div id="batch_summary" style="margin: 8px 0; font-weight: bold;"></div>
  <table>
    <thead>
      <tr>
        <th>Item ID</th>
        <th>URL</th>
        <th>Статус</th>
        <th>Попытки</th>
        <th>Analysis ID</th>
        <th>Ошибка/Warning</th>
      </tr>
    </thead>
    <tbody id="batch_items_tbody">
      <tr><td colspan="6">Batch-элементы появятся здесь...</td></tr>
    </tbody>
  </table>
  <details style="margin-top:8px;">
    <summary>Raw JSON batch (debug)</summary>
    <pre id="batch_output">Batch-статус появится здесь...</pre>
  </details>
  <script>
    function escapeHtml(value) {
      return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    function statusBadge(status) {
      const normalized = String(status || '').toLowerCase();
      const known = ['completed', 'completed_with_warnings', 'running', 'failed', 'queued'];
      const cls = known.includes(normalized) ? normalized : 'queued';
      return `<span class="badge badge-${cls}">${escapeHtml(status || 'unknown')}</span>`;
    }

    function updateTopKpisFromHistory(items) {
      const totalEl = document.getElementById('kpi_total_analyses');
      const lastAuthorEl = document.getElementById('kpi_last_author');
      const avgHookEl = document.getElementById('kpi_avg_hook');
      if (!Array.isArray(items) || items.length === 0) {
        totalEl.textContent = '0';
        lastAuthorEl.textContent = '-';
        avgHookEl.textContent = '-';
        return;
      }
      totalEl.textContent = String(items.length);
      lastAuthorEl.textContent = items[0].author_username || '-';
      const scores = items
        .map(item => Number(item.hook_score))
        .filter(value => Number.isFinite(value));
      if (!scores.length) {
        avgHookEl.textContent = '-';
        return;
      }
      const avg = scores.reduce((acc, value) => acc + value, 0) / scores.length;
      avgHookEl.textContent = avg.toFixed(2);
    }

    function updateTopKpiBatch(data) {
      const el = document.getElementById('kpi_last_batch');
      if (!data || !data.id) {
        el.textContent = '-';
        return;
      }
      el.textContent = `#${data.id} ${data.status || ''}`;
    }

    async function run() {
      const payload = {
        url: document.getElementById('url').value.trim(),
        comments_limit: Number(document.getElementById('comments_limit').value || 200),
        include_comment_replies: document.getElementById('include_replies').checked,
        export_google: document.getElementById('export_google').checked
      };
      const out = document.getElementById('output');
      out.textContent = 'Обрабатываю...';
      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          out.textContent = JSON.stringify(data, null, 2);
          return;
        }
        out.textContent = JSON.stringify(data, null, 2);
        loadHistory();
        const exports = document.getElementById('exports');
        if (data && data.id) {
          exports.innerHTML = `
            <a href="/api/analysis/${data.id}/export/txt" target="_blank">Скачать TXT</a>
            &nbsp;|&nbsp;
            <a href="/api/analysis/${data.id}/export/docx" target="_blank">Скачать DOCX</a>
          `;
        } else {
          exports.innerHTML = '';
        }
      } catch (e) {
        out.textContent = String(e);
      }
    }

    async function viewAnalysisDetails(analysisId) {
      const out = document.getElementById('output');
      const exports = document.getElementById('exports');
      out.textContent = `Загружаю детали анализа #${analysisId}...`;
      const res = await fetch(`/api/analysis/${analysisId}`);
      const data = await res.json();
      if (!res.ok) {
        out.textContent = JSON.stringify(data, null, 2);
        return;
      }
      out.textContent = JSON.stringify(data, null, 2);
      exports.innerHTML = `
        <a href="/api/analysis/${analysisId}/export/txt" target="_blank">Скачать TXT</a>
        &nbsp;|&nbsp;
        <a href="/api/analysis/${analysisId}/export/docx" target="_blank">Скачать DOCX</a>
      `;
    }

    let batchPollHandle = null;
    let currentBatchId = null;

    function extractUrls(raw) {
      return raw
        .split(/\\r?\\n|,|;/)
        .map(x => x.trim())
        .filter(x => x.startsWith('http://') || x.startsWith('https://'));
    }

    async function loadBatchFile() {
      const input = document.getElementById('batch_file');
      const out = document.getElementById('batch_output');
      if (!input.files || !input.files.length) {
        out.textContent = 'Выбери .txt или .csv файл.';
        return;
      }
      const file = input.files[0];
      const text = await file.text();
      const urls = extractUrls(text);
      document.getElementById('batch_urls').value = urls.join('\\n');
      out.textContent = `Загружено ссылок: ${urls.length}`;
    }
    async function runBatch() {
      const raw = document.getElementById('batch_urls').value || '';
      const urls = extractUrls(raw);
      const out = document.getElementById('batch_output');
      if (!urls.length) {
        out.textContent = 'Добавь хотя бы одну ссылку.';
        return;
      }

      const payload = {
        urls,
        comments_limit: Number(document.getElementById('comments_limit').value || 200),
        include_comment_replies: document.getElementById('include_replies').checked,
        export_google: document.getElementById('export_google').checked,
        max_retries: Number(document.getElementById('batch_retries').value || 2)
      };

      out.textContent = 'Создаю batch-задачу...';
      const res = await fetch('/api/batch/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        out.textContent = JSON.stringify(data, null, 2);
        return;
      }
      if (!data.id) {
        out.textContent = JSON.stringify(data, null, 2);
        return;
      }
      currentBatchId = data.id;
      out.textContent = `Batch #${data.id} создан. Статус: ${data.status}`;
      renderBatchSummary(data);
      renderBatchItems(data.items || []);

      if (batchPollHandle) {
        clearInterval(batchPollHandle);
      }
      batchPollHandle = setInterval(async () => {
        const statusRes = await fetch(`/api/batch/${data.id}`);
        const statusData = await statusRes.json();
        renderBatchSummary(statusData);
        renderBatchItems(statusData.items || []);
        out.textContent = JSON.stringify(statusData, null, 2);
        if (['completed', 'completed_with_errors', 'failed'].includes(statusData.status)) {
          clearInterval(batchPollHandle);
          batchPollHandle = null;
        }
      }, 2000);
    }

    async function retryFailedBatch() {
      const out = document.getElementById('batch_output');
      if (!currentBatchId) {
        out.textContent = 'Сначала запусти или открой batch, чтобы появился его ID.';
        return;
      }
      out.textContent = `Создаю retry job для batch #${currentBatchId}...`;
      const res = await fetch(`/api/batch/${currentBatchId}/retry-failed`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) {
        out.textContent = JSON.stringify(data, null, 2);
        return;
      }
      if (!data.id) {
        out.textContent = JSON.stringify(data, null, 2);
        return;
      }
      currentBatchId = data.id;
      out.textContent = `Retry batch #${data.id} создан. Статус: ${data.status}`;
      renderBatchSummary(data);
      renderBatchItems(data.items || []);
    }

    function downloadBatchCsv() {
      const out = document.getElementById('batch_output');
      if (!currentBatchId) {
        out.textContent = 'Сначала запусти batch, чтобы появился его ID.';
        return;
      }
      window.open(`/api/batch/${currentBatchId}/export/csv`, '_blank');
    }

    function renderBatchSummary(data) {
      const el = document.getElementById('batch_summary');
      if (!data || typeof data !== 'object') {
        el.textContent = '';
        return;
      }
      const total = data.total_urls ?? 0;
      const processed = data.processed_urls ?? 0;
      const success = data.success_urls ?? 0;
      const failed = data.failed_urls ?? 0;
      const status = data.status ?? 'unknown';
      const withWarnings = Array.isArray(data.items)
        ? data.items.filter(i => i.status === 'completed_with_warnings').length
        : 0;
      el.innerHTML = `Batch #${escapeHtml(data.id ?? '-')} | status: ${statusBadge(status)} | processed: ${processed}/${total} | success: ${success} | failed: ${failed} | warnings: ${withWarnings}`;
      updateTopKpiBatch(data);
    }

    function renderBatchItems(items) {
      const tbody = document.getElementById('batch_items_tbody');
      if (!Array.isArray(items) || items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">Нет элементов batch.</td></tr>';
        return;
      }
      const rows = items.map(item => `
        <tr>
          <td>${escapeHtml(item.id)}</td>
          <td style="word-break: break-all;">${escapeHtml(item.url)}</td>
          <td>${statusBadge(item.status)}</td>
          <td>${escapeHtml(item.attempts)}</td>
          <td>${escapeHtml(item.analysis_id ?? '')}</td>
          <td style="word-break: break-all;">${escapeHtml(item.error_text || '')}</td>
        </tr>
      `);
      tbody.innerHTML = rows.join('');
    }

    async function loadHistory() {
      const q = encodeURIComponent((document.getElementById('history_q').value || '').trim());
      const author = encodeURIComponent((document.getElementById('history_author').value || '').trim());
      const mediaType = encodeURIComponent((document.getElementById('history_media_type').value || '').trim());
      const out = document.getElementById('history_output');
      const tbody = document.getElementById('history_tbody');
      out.textContent = 'Загружаю историю...';
      tbody.innerHTML = '<tr><td colspan="7">Загружаю историю...</td></tr>';
      const url = `/api/analysis?limit=30&q=${q}&author=${author}&media_type=${mediaType}`;
      const res = await fetch(url);
      const data = await res.json();
      out.textContent = JSON.stringify(data, null, 2);
      if (!res.ok) {
        tbody.innerHTML = `<tr><td colspan="7">${escapeHtml(data.detail || 'Ошибка загрузки истории')}</td></tr>`;
        return;
      }
      updateTopKpisFromHistory(data);
      if (!Array.isArray(data) || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">История пуста по текущему фильтру.</td></tr>';
        return;
      }
      const rows = data.map(item => `
        <tr>
          <td>${escapeHtml(item.id)}</td>
          <td>${escapeHtml(item.created_at)}</td>
          <td>${escapeHtml(item.author_username)}</td>
          <td>${escapeHtml(item.media_type)}</td>
          <td>${escapeHtml(item.shortcode)}</td>
          <td style="word-break: break-all;"><a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">Открыть</a></td>
          <td>
            <button onclick="viewAnalysisDetails(${escapeHtml(item.id)})">Просмотр</button>
            <a href="/api/analysis/${escapeHtml(item.id)}/export/txt" target="_blank">TXT</a>
            <a href="/api/analysis/${escapeHtml(item.id)}/export/docx" target="_blank">DOCX</a>
          </td>
        </tr>
      `);
      tbody.innerHTML = rows.join('');
    }

    async function clearHistory() {
      const out = document.getElementById('history_output');
      const ok = window.confirm('Удалить все сохраненные анализы из истории?');
      if (!ok) {
        return;
      }
      out.textContent = 'Очищаю историю...';
      const res = await fetch('/api/analysis/clear', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) {
        out.textContent = JSON.stringify(data, null, 2);
        return;
      }
      document.getElementById('output').textContent = 'Результат появится здесь...';
      document.getElementById('exports').innerHTML = '';
      out.textContent = `История очищена. Удалено анализов: ${data.deleted_analyses}`;
      loadHistory();
    }

    async function loadLatestBatchKpi() {
      const res = await fetch('/api/batch?limit=1');
      const data = await res.json();
      if (!res.ok || !Array.isArray(data) || data.length === 0) {
        updateTopKpiBatch(null);
        return;
      }
      updateTopKpiBatch(data[0]);
    }

    loadHistory();
    loadLatestBatchKpi();
  </script>
</body>
</html>
"""


def _to_response(record: AnalysisRecord) -> AnalysisResponse:
    insights_raw = json.loads(record.insights_json)
    if "engagement" not in insights_raw:
        insights_raw["engagement"] = {
            "basis": "legacy",
            "by_views": 0.0,
            "proxy": 0.0,
        }
    if "exports" not in insights_raw:
        insights_raw["exports"] = {}
    insights = AnalysisInsights.model_validate(insights_raw)
    return AnalysisResponse(
        id=record.id,
        url=record.url,
        shortcode=record.shortcode,
        media_type=record.media_type,
        author_username=record.author_username,
        likes_count=record.likes_count,
        comments_count=record.comments_count,
        view_count=record.view_count,
        comments_analyzed=record.comments_analyzed,
        engagement_rate=record.engagement_rate,
        exported_google=record.exported_google,
        insights=insights,
        created_at=record.created_at,
    )


def _to_batch_item_response(item: BatchJobItem) -> BatchItemResponse:
    return BatchItemResponse(
        id=item.id,
        url=item.url,
        status=item.status,
        attempts=item.attempts,
        analysis_id=item.analysis_id,
        error_text=item.error_text,
    )


def _to_batch_job_response(job: BatchJob, items: list[BatchJobItem]) -> BatchJobResponse:
    return BatchJobResponse(
        id=job.id,
        status=job.status,
        total_urls=job.total_urls,
        processed_urls=job.processed_urls,
        success_urls=job.success_urls,
        failed_urls=job.failed_urls,
        comments_limit=job.comments_limit,
        include_comment_replies=job.include_comment_replies,
        export_google=job.export_google,
        max_retries=job.max_retries,
        last_error=job.last_error,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        items=[_to_batch_item_response(item) for item in items],
    )


def _build_insights(result) -> dict:
    return {
        "hook": {"score": result.hook_score, "rationale": result.hook_rationale},
        "retention": {"score": result.retention_score, "rationale": result.retention_rationale},
        "transfer": {"score": result.transfer_score, "rationale": result.transfer_rationale},
        "confidence_score": result.confidence_score,
        "cta_detected": result.cta_detected,
        "cta_type": result.cta_type,
        "engagement": {
            "basis": result.engagement_basis,
            "by_views": round(result.engagement_rate_by_views, 2),
            "proxy": round(result.engagement_rate_proxy, 2),
        },
        "audience_reaction": result.audience_reaction,
        "actionable_recommendations": result.actionable_recommendations,
    }


def _analyze_single_url(
    db: Session,
    *,
    url: str,
    comments_limit: int,
    include_comment_replies: bool,
    export_google: bool,
    ig_client: InstagramClientService,
    gexport: GoogleExportService,
) -> AnalysisResponse:
    payload = ig_client.fetch_media(
        url=url,
        comments_limit=comments_limit,
        include_comment_replies=include_comment_replies,
    )
    result = analyze_payload(
        caption=payload.caption,
        likes=payload.likes_count,
        comments_count=payload.comments_count,
        views=payload.view_count,
        comments=payload.comments,
    )
    insights = _build_insights(result)
    record = AnalysisRecord(
        url=payload.url,
        shortcode=payload.shortcode,
        media_type=payload.media_type,
        author_username=payload.author_username,
        caption=payload.caption,
        likes_count=payload.likes_count,
        comments_count=payload.comments_count,
        view_count=payload.view_count,
        comments_analyzed=len(payload.comments),
        hook_score=result.hook_score,
        retention_score=result.retention_score,
        transfer_score=result.transfer_score,
        confidence_score=result.confidence_score,
        engagement_rate=f"{result.engagement_rate:.2f}",
        insights_json=json.dumps(insights, ensure_ascii=False),
        exported_google=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    response = _to_response(record)
    if export_google:
        export_result = gexport.export(response.model_dump(mode="json"))
        insights["exports"] = export_result.as_dict()
        record.insights_json = json.dumps(insights, ensure_ascii=False)
        record.exported_google = export_result.full_success
        db.add(record)
        db.commit()
        db.refresh(record)
        response = _to_response(record)
    return response


def _recompute_batch_progress(db: Session, job: BatchJob) -> None:
    items = db.query(BatchJobItem).filter(BatchJobItem.batch_job_id == job.id).all()
    total = len(items)
    success = sum(1 for item in items if item.status in {"completed", "completed_with_warnings"})
    failed = sum(1 for item in items if item.status == "failed")
    processed = success + failed
    job.total_urls = total
    job.success_urls = success
    job.failed_urls = failed
    job.processed_urls = processed
    db.add(job)
    db.commit()


def _run_batch_job(batch_job_id: int) -> None:
    db = SessionLocal()
    ig_client = InstagramClientService()
    gexport = GoogleExportService()
    try:
        job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
        if not job:
            return
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.add(job)
        db.commit()

        items = db.query(BatchJobItem).filter(BatchJobItem.batch_job_id == batch_job_id).all()
        for item in items:
            item.status = "running"
            db.add(item)
            db.commit()
            db.refresh(item)

            last_error = ""
            for attempt in range(1, job.max_retries + 1):
                item.attempts = attempt
                db.add(item)
                db.commit()
                try:
                    response = _analyze_single_url(
                        db,
                        url=item.url,
                        comments_limit=job.comments_limit,
                        include_comment_replies=job.include_comment_replies,
                        export_google=job.export_google,
                        ig_client=ig_client,
                        gexport=gexport,
                    )
                    item.status = "completed"
                    item.analysis_id = response.id
                    item.error_text = ""
                    exports_info = response.insights.exports or {}
                    if job.export_google and exports_info and not exports_info.get("full_success", False):
                        item.status = "completed_with_warnings"
                        warning_parts = []
                        sheets_error = exports_info.get("sheets_error", "")
                        docs_error = exports_info.get("docs_error", "")
                        if sheets_error:
                            warning_parts.append(f"sheets: {sheets_error}")
                        if docs_error:
                            warning_parts.append(f"docs: {docs_error}")
                        if exports_info.get("warnings"):
                            warning_parts.append("; ".join(exports_info.get("warnings", [])))
                        item.error_text = " | ".join(part for part in warning_parts if part)[:2000]
                    db.add(item)
                    db.commit()
                    break
                except Exception as exc:
                    last_error = str(exc)
                    item.error_text = last_error
                    db.add(item)
                    db.commit()
                    if attempt >= job.max_retries:
                        item.status = "failed"
                        db.add(item)
                        db.commit()

            _recompute_batch_progress(db, job)
            if item.status == "failed" and last_error:
                job.last_error = last_error
                db.add(job)
                db.commit()

        db.refresh(job)
        if job.failed_urls > 0 and job.success_urls > 0:
            job.status = "completed_with_errors"
        elif job.failed_urls > 0 and job.success_urls == 0:
            job.status = "failed"
        else:
            job.status = "completed"
        job.finished_at = datetime.utcnow()
        db.add(job)
        db.commit()
    except Exception as exc:
        job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
        if job:
            job.status = "failed"
            job.last_error = str(exc)
            job.finished_at = datetime.utcnow()
            db.add(job)
            db.commit()
    finally:
        db.close()


def _create_batch_job(
    db: Session,
    *,
    urls: list[str],
    comments_limit: int,
    include_comment_replies: bool,
    export_google: bool,
    max_retries: int,
) -> BatchJobResponse:
    unique_urls = list(dict.fromkeys([url.strip() for url in urls if url.strip()]))
    if not unique_urls:
        raise HTTPException(status_code=400, detail="No valid URLs provided.")
    if len(unique_urls) > 30:
        raise HTTPException(status_code=400, detail="Too many URLs. Limit is 30 per batch.")

    job = BatchJob(
        status="queued",
        total_urls=len(unique_urls),
        processed_urls=0,
        success_urls=0,
        failed_urls=0,
        comments_limit=comments_limit,
        include_comment_replies=include_comment_replies,
        export_google=export_google,
        max_retries=max_retries,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    for url in unique_urls:
        db.add(
            BatchJobItem(
                batch_job_id=job.id,
                url=url,
                status="queued",
                attempts=0,
                error_text="",
            )
        )
    db.commit()

    worker = threading.Thread(target=_run_batch_job, args=(job.id,), daemon=True)
    worker.start()

    items = db.query(BatchJobItem).filter(BatchJobItem.batch_job_id == job.id).all()
    return _to_batch_job_response(job, items)


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)) -> AnalysisResponse:
    try:
        return _analyze_single_url(
            db,
            url=str(request.url),
            comments_limit=request.comments_limit,
            include_comment_replies=request.include_comment_replies,
            export_google=request.export_google,
            ig_client=ig_service,
            gexport=google_export,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisResponse:
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _to_response(record)


@app.get("/api/analysis", response_model=list[AnalysisListItem])
def list_analysis(
    db: Session = Depends(get_db),
    limit: int = 50,
    q: str = "",
    author: str = "",
    media_type: str = "",
) -> list[AnalysisListItem]:
    query = db.query(AnalysisRecord)

    normalized_q = q.strip()
    if normalized_q:
        pattern = f"%{normalized_q}%"
        query = query.filter(
            or_(
                AnalysisRecord.url.ilike(pattern),
                AnalysisRecord.shortcode.ilike(pattern),
                AnalysisRecord.author_username.ilike(pattern),
            )
        )

    normalized_author = author.strip()
    if normalized_author:
        query = query.filter(AnalysisRecord.author_username.ilike(f"%{normalized_author}%"))

    normalized_media_type = media_type.strip()
    if normalized_media_type:
        query = query.filter(AnalysisRecord.media_type == normalized_media_type)

    records = query.order_by(AnalysisRecord.created_at.desc()).limit(max(1, min(200, limit))).all()
    return [
        AnalysisListItem(
            id=item.id,
            url=item.url,
            shortcode=item.shortcode,
            media_type=item.media_type,
            author_username=item.author_username,
            hook_score=item.hook_score,
            created_at=item.created_at,
        )
        for item in records
    ]


@app.post("/api/analysis/clear")
def clear_analysis_history(db: Session = Depends(get_db)):
    # Break links from batch items to analysis rows before deletion.
    linked_items = db.query(BatchJobItem).filter(BatchJobItem.analysis_id.is_not(None)).all()
    for item in linked_items:
        item.analysis_id = None
    deleted_analyses = db.query(AnalysisRecord).delete()
    db.commit()
    return {"ok": True, "deleted_analyses": deleted_analyses}


@app.post("/api/batch/analyze", response_model=BatchJobResponse)
def start_batch_analysis(request: BatchAnalyzeRequest, db: Session = Depends(get_db)) -> BatchJobResponse:
    return _create_batch_job(
        db,
        urls=[str(url) for url in request.urls],
        comments_limit=request.comments_limit,
        include_comment_replies=request.include_comment_replies,
        export_google=request.export_google,
        max_retries=request.max_retries,
    )


@app.post("/api/batch/{batch_job_id}/retry-failed", response_model=BatchJobResponse)
def retry_failed_batch(batch_job_id: int, db: Session = Depends(get_db)) -> BatchJobResponse:
    source_job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
    if not source_job:
        raise HTTPException(status_code=404, detail="Source batch job not found.")

    failed_items = (
        db.query(BatchJobItem)
        .filter(BatchJobItem.batch_job_id == batch_job_id, BatchJobItem.status == "failed")
        .all()
    )
    if not failed_items:
        raise HTTPException(status_code=400, detail="No failed URLs to retry in this batch.")

    return _create_batch_job(
        db,
        urls=[item.url for item in failed_items],
        comments_limit=source_job.comments_limit,
        include_comment_replies=source_job.include_comment_replies,
        export_google=source_job.export_google,
        max_retries=source_job.max_retries,
    )


@app.get("/api/batch/{batch_job_id}", response_model=BatchJobResponse)
def get_batch_job(batch_job_id: int, db: Session = Depends(get_db)) -> BatchJobResponse:
    job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found.")
    items = db.query(BatchJobItem).filter(BatchJobItem.batch_job_id == batch_job_id).all()
    return _to_batch_job_response(job, items)


@app.get("/api/batch", response_model=list[BatchJobListItem])
def list_batch_jobs(db: Session = Depends(get_db), limit: int = 50) -> list[BatchJobListItem]:
    jobs = (
        db.query(BatchJob)
        .order_by(BatchJob.created_at.desc())
        .limit(max(1, min(200, limit)))
        .all()
    )
    return [
        BatchJobListItem(
            id=job.id,
            status=job.status,
            total_urls=job.total_urls,
            processed_urls=job.processed_urls,
            success_urls=job.success_urls,
            failed_urls=job.failed_urls,
            created_at=job.created_at,
            finished_at=job.finished_at,
        )
        for job in jobs
    ]


@app.get("/api/batch/{batch_job_id}/export/csv")
def export_batch_csv(batch_job_id: int, db: Session = Depends(get_db)):
    job = db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found.")

    items = db.query(BatchJobItem).filter(BatchJobItem.batch_job_id == batch_job_id).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "batch_id",
            "item_id",
            "url",
            "item_status",
            "attempts",
            "analysis_id",
            "error_text",
            "shortcode",
            "author_username",
            "media_type",
            "likes_count",
            "comments_count",
            "view_count",
            "comments_analyzed",
            "engagement_rate",
            "hook_score",
            "retention_score",
            "transfer_score",
            "confidence_score",
            "created_at",
        ]
    )

    for item in items:
        analysis = None
        if item.analysis_id:
            analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == item.analysis_id).first()
        writer.writerow(
            [
                job.id,
                item.id,
                item.url,
                item.status,
                item.attempts,
                item.analysis_id or "",
                item.error_text or "",
                analysis.shortcode if analysis else "",
                analysis.author_username if analysis else "",
                analysis.media_type if analysis else "",
                analysis.likes_count if analysis else "",
                analysis.comments_count if analysis else "",
                analysis.view_count if analysis else "",
                analysis.comments_analyzed if analysis else "",
                analysis.engagement_rate if analysis else "",
                analysis.hook_score if analysis else "",
                analysis.retention_score if analysis else "",
                analysis.transfer_score if analysis else "",
                analysis.confidence_score if analysis else "",
                analysis.created_at.isoformat() if analysis and analysis.created_at else "",
            ]
        )

    output.seek(0)
    filename = f"batch_{job.id}_results.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)


@app.get("/api/analysis/{analysis_id}/export/{file_format}")
def export_analysis_file(analysis_id: int, file_format: str, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    response = _to_response(record)
    normalized_format = file_format.lower()
    if normalized_format == "txt":
        file_path = export_report_to_txt(response)
    elif normalized_format == "docx":
        file_path = export_report_to_docx(response)
    else:
        raise HTTPException(status_code=400, detail="Supported formats: txt, docx")

    return FileResponse(path=file_path, filename=file_path.name)
