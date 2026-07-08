"""Render reports to PDF bytes."""

from __future__ import annotations

import logging
from io import BytesIO

from weasyprint import HTML

from todayflow_backend.core import models

logger = logging.getLogger(__name__)


class PDFGenerationError(Exception):
    """Raised when PDF generation fails."""

    pass


class FullReportRenderer:
    def render(self, report: models.FullReport, user_email: str) -> bytes:
        """
        Render a FullReport to PDF bytes.
        
        Args:
            report: The FullReport model to render
            user_email: User email for the header
            
        Returns:
            PDF bytes
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            html = self._build_html(report, user_email)
            buffer = BytesIO()
            HTML(string=html).write_pdf(target=buffer)
            pdf_bytes = buffer.getvalue()
            
            if not pdf_bytes:
                raise PDFGenerationError("Generated PDF is empty")
                
            logger.info(f"PDF generated successfully for user {user_email}, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as exc:
            logger.error(f"PDF generation failed for user {user_email}: {exc}", exc_info=True)
            raise PDFGenerationError(f"Failed to generate PDF: {exc}") from exc

    def _build_html(self, report: models.FullReport, user_email: str) -> str:
        sections_html = []
        for section in report.sections:
            total = len(section.paragraphs)
            if not total:
                continue
            cards = []
            for index, paragraph in enumerate(section.paragraphs, start=1):
                meaning_label = paragraph.meaning_type or "Meaning Insight"
                cards.append(
                    f"""
                    <article class="meaning-card">
                      <header class="orientation-rail">
                        <div class="rail-info">
                          <span class="rail-section">{section.section}</span>
                          <span class="rail-badge">{meaning_label}</span>
                        </div>
                        <span class="rail-step">Step {index}/{total}</span>
                      </header>
                      <div class="meaning-text">
                        {paragraph.text}
                      </div>
                    </article>
                    """
                )
            sections_html.append(f"<section><h2>{section.section}</h2>{''.join(cards)}</section>")

        tarot_section = ""
        if report.tarot_spreads:
            rows = "".join(
                f"<tr><td>{entry.draw_date}</td><td>{entry.spread.title}</td><td>{', '.join(card.card.name for card in entry.spread.cards)}</td></tr>"
                for entry in report.tarot_spreads
            )
            tarot_section = f"<section><h2>Tarot Spread History</h2><table><thead><tr><th>Date</th><th>Spread</th><th>Cards</th></tr></thead><tbody>{rows}</tbody></table></section>"

        # Orbit Design System values (matching frontend globals.css)
        orbit_colors = {
            "ink": "#0f172a",
            "slate": "#334155",
            "muted": "#6b7280",
            "page": "#faf8f5",
            "card": "#ffffff",
            "mist": "#f5f3f0",
            "border": "#e5e0d8",
            "border-light": "#f0ede8",
        }
        
        orbit_fonts = {
            "display": '"Inter", "Inter var", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
            "body": '"Inter", "Inter var", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
        }
        
        orbit_spacing = {
            "xs": "6px",
            "sm": "12px",
            "md": "18px",
            "lg": "32px",
            "xl": "48px",
        }
        
        orbit_radius = {
            "sm": "8px",
            "md": "16px",
            "lg": "24px",
            "capsule": "999px",
        }
        
        orbit_shadows = {
            "soft": "0 4px 12px rgba(15, 23, 42, 0.04)",
            "medium": "0 8px 24px rgba(15, 23, 42, 0.06)",
            "card": "0 2px 8px rgba(15, 23, 42, 0.03)",
        }
        
        return f"""
        <html>
          <head>
            <meta charset="utf-8" />
            <style>
              @import url("https://rsms.me/inter/inter.css");
              
              body {{
                font-family: {orbit_fonts["body"]};
                background: {orbit_colors["page"]};
                color: {orbit_colors["ink"]};
                margin: {orbit_spacing["xl"]};
                line-height: 1.6;
                -webkit-font-smoothing: antialiased;
              }}
              
              h1 {{
                font-family: {orbit_fonts["display"]};
                font-size: 2rem;
                font-weight: 600;
                color: {orbit_colors["ink"]};
                margin-bottom: {orbit_spacing["sm"]};
                letter-spacing: -0.01em;
              }}
              
              h2 {{
                font-family: {orbit_fonts["display"]};
                font-size: 1.5rem;
                font-weight: 600;
                color: {orbit_colors["ink"]};
                margin-top: {orbit_spacing["lg"]};
                margin-bottom: {orbit_spacing["md"]};
                letter-spacing: -0.01em;
              }}
              
              section {{
                margin-bottom: {orbit_spacing["xl"]};
                page-break-inside: avoid;
              }}
              
              .orientation-rail {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid {orbit_colors["border"]};
                padding-bottom: {orbit_spacing["xs"]};
                margin-bottom: {orbit_spacing["md"]};
                flex-wrap: wrap;
                gap: {orbit_spacing["sm"]};
              }}
              
              .rail-info {{
                display: flex;
                gap: {orbit_spacing["sm"]};
                align-items: center;
                flex-wrap: wrap;
              }}
              
              .rail-section {{
                font-size: 0.85rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: {orbit_colors["ink"]};
              }}
              
              .rail-badge {{
                font-size: 0.85rem;
                font-weight: 500;
                border-radius: {orbit_radius["capsule"]};
                padding: {orbit_spacing["xs"]} {orbit_spacing["sm"]};
                border: 1px solid {orbit_colors["border"]};
                background: {orbit_colors["mist"]};
                color: {orbit_colors["slate"]};
                text-transform: uppercase;
                letter-spacing: 0.08em;
              }}
              
              .rail-step {{
                font-size: 0.9rem;
                color: {orbit_colors["muted"]};
              }}
              
              .meaning-card {{
                border: 1px solid {orbit_colors["border"]};
                border-radius: {orbit_radius["md"]};
                padding: {orbit_spacing["lg"]};
                margin-bottom: {orbit_spacing["md"]};
                background: {orbit_colors["card"]};
                box-shadow: {orbit_shadows["soft"]};
                page-break-inside: avoid;
              }}
              
              .meaning-text {{
                color: {orbit_colors["ink"]};
                line-height: 1.6;
                font-size: 1.05rem;
              }}
              
              table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: {orbit_spacing["md"]};
              }}
              
              th, td {{
                border: 1px solid {orbit_colors["border"]};
                padding: {orbit_spacing["sm"]};
                text-align: left;
              }}
              
              th {{
                background: {orbit_colors["mist"]};
                text-transform: uppercase;
                font-size: 0.85rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                color: {orbit_colors["ink"]};
              }}
              
              td {{
                color: {orbit_colors["slate"]};
              }}
              
              p {{
                color: {orbit_colors["slate"]};
                margin-bottom: {orbit_spacing["sm"]};
              }}
              
              @page {{
                margin: {orbit_spacing["xl"]};
                margin-bottom: 60px;
                size: A4;
              }}
              
              @page {{
                @bottom-center {{
                  content: "TodayFlow Full Birth Chart Report · Page " counter(page);
                  font-family: {orbit_fonts["body"]};
                  font-size: 0.7rem;
                  color: {orbit_colors["muted"]};
                  padding-top: {orbit_spacing["sm"]};
                }}
              }}
              
              h2 {{
                page-break-before: avoid;
                page-break-after: avoid;
                orphans: 3;
                widows: 3;
              }}
              
              .meaning-card {{
                page-break-inside: avoid;
              }}
              
              section {{
                page-break-inside: avoid;
              }}
              
              .meaning-text {{
                orphans: 2;
                widows: 2;
              }}
            </style>
          </head>
          <body>
            <h1>TodayFlow Full Birth Chart Report</h1>
            <p style="color: {orbit_colors["muted"]}; font-size: 0.95rem;">User: {user_email}</p>
            <p style="color: {orbit_colors["slate"]}; font-size: 1.05rem; margin-bottom: {orbit_spacing["xl"]};">
              Sun {report.summary.sun} · Moon {report.summary.moon} · Rising {report.summary.rising}
            </p>
            {tarot_section}
            {''.join(sections_html)}
          </body>
        </html>
        """
