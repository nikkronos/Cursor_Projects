from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import time
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread

from app.config import get_settings


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


@dataclass
class GoogleExportResult:
    attempted: bool = False
    any_success: bool = False
    full_success: bool = False
    sheets_success: bool = False
    docs_success: bool = False
    sheets_url: str = ""
    sheets_worksheet: str = ""
    sheets_error: str = ""
    docs_error: str = ""
    docs_url: str = ""
    targets_configured: dict[str, bool] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "attempted": self.attempted,
            "any_success": self.any_success,
            "full_success": self.full_success,
            "sheets_success": self.sheets_success,
            "docs_success": self.docs_success,
            "sheets_url": self.sheets_url,
            "sheets_worksheet": self.sheets_worksheet,
            "sheets_error": self.sheets_error,
            "docs_error": self.docs_error,
            "docs_url": self.docs_url,
            "targets_configured": self.targets_configured,
            "warnings": self.warnings,
        }


class GoogleExportService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._creds = None

    def _load_creds(self):
        if self._creds:
            return self._creds
        payload: dict[str, Any] | None = None
        if self.settings.google_credentials_json:
            payload = json.loads(self.settings.google_credentials_json)
        elif self.settings.google_credentials_file:
            credentials_path = Path(self.settings.google_credentials_file)
            if not credentials_path.exists():
                raise ValueError(
                    f"GOOGLE_CREDENTIALS_FILE points to missing file: {credentials_path}"
                )
            payload = json.loads(credentials_path.read_text(encoding="utf-8"))

        if not payload:
            return None

        self._creds = Credentials.from_service_account_info(payload, scopes=SCOPES)
        return self._creds

    def export(self, report: dict[str, Any]) -> GoogleExportResult:
        result = GoogleExportResult(attempted=True)
        result.targets_configured = {
            "sheets": bool(self.settings.google_sheets_spreadsheet_id),
            # By product decision we keep Google export sheets-only.
            "docs": False,
        }
        try:
            creds = self._load_creds()
        except Exception as exc:
            result.warnings.append(f"Credentials loading failed: {exc}")
            return result

        if not creds:
            result.warnings.append("Google credentials are not configured.")
            return result

        if self.settings.google_sheets_spreadsheet_id:
            sheets_ok, sheets_error, sheets_meta = self._run_with_retries(
                lambda: self._export_to_sheets(creds, report),
                expects_value=True,
            )
            result.sheets_success = sheets_ok
            result.sheets_error = sheets_error
            if sheets_ok and isinstance(sheets_meta, dict):
                result.sheets_url = str(sheets_meta.get("sheets_url", ""))
                result.sheets_worksheet = str(sheets_meta.get("worksheet", ""))
        else:
            result.warnings.append("GOOGLE_SHEETS_SPREADSHEET_ID is not set.")

        # Docs export disabled: use local TXT/DOCX for human-readable reports.
        result.warnings.append("Google Docs export is disabled; use local TXT/DOCX export.")

        result.any_success = result.sheets_success or result.docs_success
        configured = result.targets_configured
        required = []
        if configured.get("sheets"):
            required.append(result.sheets_success)
        if configured.get("docs"):
            required.append(result.docs_success)
        result.full_success = bool(required) and all(required)
        return result

    def _run_with_retries(self, operation, expects_value: bool = False):
        retries = max(1, int(self.settings.google_export_retries or 1))
        last_error = ""
        for attempt in range(1, retries + 1):
            try:
                value = operation()
                if expects_value:
                    return True, "", value
                return True, ""
            except Exception as exc:
                last_error = str(exc)
                if attempt < retries:
                    time.sleep(0.5 * attempt)
        if expects_value:
            return False, last_error, ""
        return False, last_error

    def _export_to_sheets(self, creds, report: dict[str, Any]) -> dict[str, str]:
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(self.settings.google_sheets_spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet("analysis")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="analysis", rows=1000, cols=30)
            worksheet.append_row(
                [
                    "id",
                    "url",
                    "shortcode",
                    "media_type",
                    "author",
                    "likes",
                    "comments",
                    "views",
                    "engagement_rate",
                    "engagement_basis",
                    "engagement_by_views",
                    "engagement_proxy",
                    "hook_score",
                    "retention_score",
                    "transfer_score",
                    "confidence_score",
                    "created_at",
                ]
            )

        worksheet.append_row(
            [
                report["id"],
                report["url"],
                report["shortcode"],
                report["media_type"],
                report["author_username"],
                report["likes_count"],
                report["comments_count"],
                report["view_count"],
                report["engagement_rate"],
                report["insights"]["engagement"]["basis"],
                report["insights"]["engagement"]["by_views"],
                report["insights"]["engagement"]["proxy"],
                report["insights"]["hook"]["score"],
                report["insights"]["retention"]["score"],
                report["insights"]["transfer"]["score"],
                report["insights"]["confidence_score"],
                report["created_at"],
            ]
        )
        return {
            "sheets_url": f"https://docs.google.com/spreadsheets/d/{self.settings.google_sheets_spreadsheet_id}/edit",
            "worksheet": worksheet.title,
        }

    def _export_to_docs(self, creds, report: dict[str, Any]) -> str:
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)
        # Creating the document via Drive API in the target folder is usually
        # more reliable for service accounts than documents.create in root.
        drive_file = drive_service.files().create(
            body={
                "name": f"Instagram analysis {report['shortcode']}",
                "mimeType": "application/vnd.google-apps.document",
                "parents": [self.settings.google_docs_folder_id],
            },
            fields="id, webViewLink",
        ).execute()
        doc_id = drive_file["id"]

        lines = [
            f"URL: {report['url']}",
            f"Автор: {report['author_username']}",
            f"Тип медиа: {report['media_type']}",
            f"Лайки/Комментарии/Просмотры: {report['likes_count']} / {report['comments_count']} / {report['view_count']}",
            f"ER: {report['engagement_rate']}%",
            f"ER basis: {report['insights']['engagement']['basis']}",
            f"ER by views: {report['insights']['engagement']['by_views']}%",
            f"ER proxy: {report['insights']['engagement']['proxy']}%",
            "",
            "Захват:",
            f"{report['insights']['hook']['score']}/10 - {report['insights']['hook']['rationale']}",
            "",
            "Удержание:",
            f"{report['insights']['retention']['score']}/10 - {report['insights']['retention']['rationale']}",
            "",
            "Перелив:",
            f"{report['insights']['transfer']['score']}/10 - {report['insights']['transfer']['rationale']}",
            "",
            "Рекомендации:",
        ]
        lines.extend([f"- {item}" for item in report["insights"]["actionable_recommendations"]])
        content = "\n".join(lines) + "\n"

        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": content}}]},
        ).execute()
        web_view_link = drive_file.get("webViewLink", "")
        if web_view_link:
            return web_view_link
        return f"https://docs.google.com/document/d/{doc_id}/edit"
