# DS Task 2 visual acceptance

Captured: 2026-08-04T11:36:53.767Z

## Checks
- Primary CTA on Challenges join panel should match catalog gold (`--tf-accent-gold`), not zone purple/black ink CTA.
- Decorative surfaces on Challenges should read `--day-*` (soft/tint/decor), same fallback or pinned `visual_mode` as Design System shell.
- Weekly guest gate uses DsButton gold primary (ВОЙТИ / auth CTA path).

## Token snapshots
```json
{
  "capturedAt": "2026-08-04T11:36:53.767Z",
  "pages": {
    "after-challenges.png": {
      "url": "https://todayflow.today/challenges",
      "tokens": {
        "dayMode": null,
        "decor": "#5b6472",
        "soft": "rgba(120,130,145,.2)",
        "tint": "rgba(241,242,244,.92)",
        "bg": "#f1f2f4",
        "gold": "#a67c5b"
      }
    },
    "after-weekly.png": {
      "url": "https://todayflow.today/weekly",
      "tokens": {
        "dayMode": null,
        "decor": "#5b6472",
        "soft": "rgba(120,130,145,.2)",
        "tint": "rgba(241,242,244,.92)",
        "bg": "#f1f2f4",
        "gold": "#a67c5b"
      }
    },
    "after-design-system.png": {
      "url": "https://todayflow.today/design-system",
      "tokens": {
        "dayMode": null,
        "decor": "#5b6472",
        "soft": "rgba(120,130,145,.2)",
        "tint": "rgba(241,242,244,.92)",
        "bg": "#f1f2f4",
        "gold": "#a67c5b"
      }
    },
    "after-challenges-mode-tension.png": {
      "url": "https://todayflow.today/challenges",
      "tokens": {
        "dayMode": "tension",
        "decor": "#8a5a63",
        "soft": "rgba(120,40,50,.22)",
        "tint": "rgba(34,31,34,.9)",
        "bg": "#221f22",
        "gold": "#a67c5b"
      },
      "pinned": "tension"
    },
    "after-design-system-mode-tension.png": {
      "url": "https://todayflow.today/design-system",
      "tokens": {
        "dayMode": "tension",
        "decor": "#8a5a63",
        "soft": "rgba(120,40,50,.22)",
        "tint": "rgba(34,31,34,.9)",
        "bg": "#221f22",
        "gold": "#a67c5b"
      },
      "pinned": "tension"
    }
  }
}
```
