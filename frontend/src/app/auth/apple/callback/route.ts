import { NextResponse } from "next/server";
import { getLocale, t } from "@/lib/i18n";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

function safeRedirect(path: string): string {
  if (path.startsWith("/") && !path.startsWith("//")) {
    return path;
  }
  return "/profile";
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/**
 * GET: прямое открытие URL (Apple обычно шлёт POST на этот же путь). Нельзя держать `page.tsx`
 * рядом с `route.ts` — Next.js запрещает два обработчика на одном пути.
 */
export async function GET() {
  const title = escapeHtml(t("auth.oauth.callback.appleTitle", "Вход через Apple"));
  const hint = escapeHtml(
    t(
      "auth.oauth.callback.appleGetHint",
      "Если окно входа Apple уже закрылось, открой вход снова со страницы авторизации. При редиректе с Apple сессия завершится автоматически.",
    ),
  );
  const cta = escapeHtml(t("auth.oauth.callback.backToAuth", "Вернуться ко входу"));
  const lang = escapeHtml(getLocale());
  const html = `<!DOCTYPE html><html lang="${lang}"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>${title}</title></head><body style="font-family:system-ui,sans-serif;max-width:520px;margin:2rem auto;padding:0 1rem;text-align:center;line-height:1.6"><h1 style="font-size:1.25rem;margin-bottom:1rem">${title}</h1><p style="opacity:0.85">${hint}</p><p style="margin-top:1.5rem"><a href="/auth?mode=login" style="display:inline-block;padding:0.6rem 1.2rem;border-radius:8px;background:#111;color:#fff;text-decoration:none">${cta}</a></p></body></html>`;
  return new NextResponse(html, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
}

/**
 * Sign in with Apple (web) may POST here with `id_token` after redirect (form_post).
 * Sets `todayflow_token` in localStorage via a short HTML bridge, then redirects.
 */
export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const idToken = formData.get("id_token");
    if (!idToken || typeof idToken !== "string") {
      return NextResponse.json({ error: "missing_id_token" }, { status: 400 });
    }

    let user: Record<string, unknown> | undefined;
    const rawUser = formData.get("user");
    if (rawUser && typeof rawUser === "string") {
      try {
        user = JSON.parse(rawUser) as Record<string, unknown>;
      } catch {
        user = undefined;
      }
    }

    let next = "/profile";
    const rawState = formData.get("state");
    if (rawState && typeof rawState === "string") {
      try {
        const state = JSON.parse(decodeURIComponent(rawState)) as { redirect?: string };
        if (state.redirect) {
          next = safeRedirect(state.redirect);
        }
      } catch {
        /* ignore */
      }
    }

    const res = await fetch(`${API_BASE}/oauth/apple`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        identity_token: idToken,
        user,
      }),
    });

    const data = (await res.json()) as {
      token?: string;
      access_token?: string;
      refresh_token?: string;
      detail?: unknown;
    };

    if (!res.ok) {
      const detail = data.detail;
      const msg =
        typeof detail === "string" ? detail : Array.isArray(detail) ? JSON.stringify(detail) : "Apple sign-in failed";
      const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><title>Apple</title></head><body><p>${escapeHtml(msg)}</p><p><a href="/auth?mode=login">Login</a></p></body></html>`;
      return new NextResponse(html, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
    }

    if (!data.token && !data.access_token) {
      return NextResponse.json({ error: "no_token" }, { status: 500 });
    }

    const pair = {
      access_token: data.access_token || data.token,
      refresh_token: data.refresh_token || null,
      token: data.token || data.access_token,
    };
    const tokenJs = JSON.stringify(pair);
    const nextJs = JSON.stringify(next);
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"/><script src="/auth-session-bridge.js"></script></head><body><script>
(function(){
  var t=${tokenJs};
  var n=${nextJs};
  if (typeof window.__todayflowBeginAuthSession === "function") {
    window.__todayflowBeginAuthSession(t);
  } else {
    try {
      localStorage.setItem("todayflow_token", t.access_token || t.token || t);
      if (t.refresh_token) localStorage.setItem("todayflow_refresh_token", t.refresh_token);
    } catch (e) {}
  }
  location.replace(n);
})();
</script><p>Redirecting…</p></body></html>`;

    return new NextResponse(html, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
  } catch {
    return NextResponse.json({ error: "callback_failed" }, { status: 500 });
  }
}
