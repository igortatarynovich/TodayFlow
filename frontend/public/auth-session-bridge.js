/**
 * Vanilla JS bridge for OAuth HTML callbacks (Apple form_post) before React loads.
 * Keep prefixes in sync with authSessionStorage.ts
 */
(function () {
  var LOCAL_PREFIXES = [
    "todayflow.day_engagement.v1.",
    "todayflow.day_continuity.v1.",
    "todayflow.energy_map.v1.",
    "todayflow.profile_atom_verdict.v1",
    "todayflow_core_profile:",
  ];
  var SESSION_PREFIXES = [
    "todayflow_core_profile:",
    "todayflow.compact_user_model.v0",
    "todayflow.ritual.v1.",
    "todayflow:tarot-question-flow:v1",
    "todayflow_guidance_compat_prefill_v1",
    "todayflow_active_jtbd_context",
    "todayflow_active_day_spine_context",
    "todayflow_guest_profile_session_v1",
  ];

  function removeByPrefix(storage, prefixes) {
    for (var i = storage.length - 1; i >= 0; i -= 1) {
      var key = storage.key(i);
      if (!key) continue;
      for (var j = 0; j < prefixes.length; j += 1) {
        if (key.indexOf(prefixes[j]) === 0 || key === prefixes[j]) {
          storage.removeItem(key);
          break;
        }
      }
    }
  }

  function clearUserCaches() {
    try {
      removeByPrefix(localStorage, LOCAL_PREFIXES);
      localStorage.removeItem("todayflow_meaning_outbox_v1");
      localStorage.removeItem("todayflow_meaning_rings_cache_v1");
      localStorage.removeItem("todayflow:tarot-journey:v1");
      removeByPrefix(sessionStorage, SESSION_PREFIXES);
    } catch (e) {
      /* private mode */
    }
  }

  /**
   * @param {string|object} tokenOrPair - access JWT string or {access_token|token, refresh_token}
   */
  window.__todayflowBeginAuthSession = function (tokenOrPair) {
    clearUserCaches();
    var access = "";
    var refresh = "";
    if (typeof tokenOrPair === "string") {
      access = tokenOrPair;
    } else if (tokenOrPair && typeof tokenOrPair === "object") {
      access = tokenOrPair.access_token || tokenOrPair.token || "";
      refresh = tokenOrPair.refresh_token || "";
    }
    try {
      localStorage.removeItem("todayflow_auth_snapshot_v1");
      localStorage.removeItem("todayflow_last_auth_validated_at");
      localStorage.removeItem("todayflow_last_session_snapshot_saved_at");
      localStorage.removeItem("todayflow_refresh_token");
      if (access) localStorage.setItem("todayflow_token", access);
      if (refresh) localStorage.setItem("todayflow_refresh_token", refresh);
    } catch (e) {}
    try {
      window.dispatchEvent(new Event("auth:update"));
    } catch (e2) {}
  };
})();
