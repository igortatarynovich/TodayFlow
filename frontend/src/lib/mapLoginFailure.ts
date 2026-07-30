import { ApiError } from "@/lib/api";
import { t } from "@/lib/i18n";

export type LoginFieldErrors = {
  email?: string;
  password?: string;
};

function isTransportLikeError(err: unknown): boolean {
  if (err instanceof ApiError) {
    return err.status === 0;
  }
  if (typeof DOMException !== "undefined" && err instanceof DOMException) {
    return err.name === "AbortError" || err.name === "NetworkError" || err.name === "TimeoutError";
  }
  if (err instanceof TypeError) {
    return true;
  }
  if (err instanceof Error) {
    const lower = err.message.toLowerCase();
    return (
      lower.includes("network") ||
      lower.includes("fetch") ||
      lower.includes("load failed") ||
      lower.includes("failed to load") ||
      lower.includes("connection") ||
      lower.includes("offline") ||
      lower.includes("подключ")
    );
  }
  return false;
}

/** Maps login transport / HTTP failures to inline field copy (RU via i18n). */
export function mapLoginFailure(err: unknown): LoginFieldErrors {
  const invalidCredentials = t("auth.errors.invalidCredentials", "Неверный email или пароль");
  const networkError = t(
    "auth.errors.network",
    "Не удалось подключиться. Попробуйте ещё раз",
  );
  const rateLimited = t(
    "auth.errors.rateLimited",
    "Слишком много попыток. Попробуйте позже",
  );
  const serverError = t("auth.errors.server", "Не удалось подключиться. Попробуйте ещё раз");

  if (isTransportLikeError(err)) {
    return { password: networkError };
  }

  if (err instanceof ApiError) {
    if (err.status === 429) {
      return { password: rateLimited };
    }
    if (err.status >= 500) {
      return { password: serverError };
    }
    if (err.status === 401) {
      return { email: invalidCredentials, password: invalidCredentials };
    }
  }

  const errorMessage = err instanceof Error ? err.message : t("auth.login.error", "Ошибка входа");
  const lower = errorMessage.toLowerCase();

  if (lower.includes("too many") || lower.includes("rate") || lower.includes("попыток")) {
    return { password: rateLimited };
  }
  if (
    lower.includes("unauthorized") ||
    lower.includes("credential") ||
    lower.includes("invalid") ||
    lower.includes("неверн") ||
    lower.includes("пароль") ||
    lower.includes("password") ||
    lower.includes("email")
  ) {
    return { email: invalidCredentials, password: invalidCredentials };
  }

  return { password: errorMessage };
}

/** Field focus is for validation / credentials; transport copy stays visible without stealing focus. */
export function shouldFocusLoginFieldError(errors: LoginFieldErrors, err: unknown): boolean {
  if (isTransportLikeError(err)) return false;
  if (err instanceof ApiError && (err.status === 429 || err.status >= 500)) return false;
  return Boolean(errors.email || errors.password);
}
