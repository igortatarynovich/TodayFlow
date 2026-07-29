/**
 * One-shot Profile motion flags — each accent plays once, then stays off.
 * localStorage so remount / revisit does not re-fire ambient news.
 */

const PREFIX = "tf.profile.motion.once.v1:";

export type ProfileMotionOnceKey =
  | "decode-pattern-wave"
  | "act2-selected-by-reveal";

export const PROFILE_DECODE_PATTERN_WAVE_EVENT = "tf:profile-decode-pattern-wave";

function storageKey(key: ProfileMotionOnceKey): string {
  return `${PREFIX}${key}`;
}

export function hasProfileMotionOnce(key: ProfileMotionOnceKey): boolean {
  if (typeof window === "undefined") return true;
  try {
    return window.localStorage.getItem(storageKey(key)) === "1";
  } catch {
    return true;
  }
}

/** Returns true only the first time; marks the key consumed. */
export function consumeProfileMotionOnce(key: ProfileMotionOnceKey): boolean {
  if (typeof window === "undefined") return false;
  if (hasProfileMotionOnce(key)) return false;
  try {
    window.localStorage.setItem(storageKey(key), "1");
  } catch {
    /* private mode — still allow one in-memory shot via return true below */
  }
  return true;
}

export function resetProfileMotionOnceForTests(key?: ProfileMotionOnceKey): void {
  if (typeof window === "undefined") return;
  try {
    if (key) {
      window.localStorage.removeItem(storageKey(key));
      return;
    }
    for (const k of Object.keys(window.localStorage)) {
      if (k.startsWith(PREFIX)) window.localStorage.removeItem(k);
    }
  } catch {
    /* ignore */
  }
}
