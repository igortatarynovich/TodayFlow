"""Generate shareable snippets from Lite reports."""

from __future__ import annotations

import re

from todayflow_backend.core import models
from todayflow_backend.db import models as db_models
from todayflow_backend.services.lite_reports import LiteReportService, get_lite_report_service


class SharingService:
    def __init__(self, lite_service: LiteReportService | None = None) -> None:
        self.lite_service = lite_service or LiteReportService()

    def shareable_snippet(self, user: db_models.User) -> models.ShareableSnippet:
        report = self.lite_service._get_latest_report(user)
        if not report or not report.paragraphs:
            raise ValueError("No lite report available")
        paragraph = self._pick_paragraph(report.paragraphs)
        snippet_text = self._extract_sentence(paragraph.text)
        return models.ShareableSnippet(
            paragraph_id=paragraph.paragraph_id,
            section=paragraph.section,
            text=snippet_text,
            meaning_type=paragraph.meaning_type,
        )

    def _pick_paragraph(self, paragraphs):
        # Prefer Emotional Patterns first; fallback to first entry.
        for paragraph in paragraphs:
            if paragraph.section == "Emotional Patterns":
                return paragraph
        return paragraphs[0]

    def _extract_sentence(self, text: str) -> str:
        match = re.split(r"(?<=[.!?])\s+", text.strip())
        if match:
            sentence = match[0]
        else:
            sentence = text.strip()
        return sentence


async def get_sharing_service() -> SharingService:
    return SharingService()
