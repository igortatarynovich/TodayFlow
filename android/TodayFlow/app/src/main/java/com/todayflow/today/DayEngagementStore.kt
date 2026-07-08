package com.todayflow.today

import android.content.Context
import android.content.SharedPreferences

/** Локальное состояние ритуала дня — паритет веб `todayRitualPersisted.ts` / iOS ritual extras. */
class DayEngagementStore(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun loadSpine(dateISO: String): RitualSpineSnapshot =
        RitualSpineSnapshot(
            dayOpened = prefs.getBoolean(key(dateISO, "day_opened"), false),
            tarotContinueAck = prefs.getBoolean(key(dateISO, "tarot_continue"), false),
            numberRevealed = prefs.getBoolean(key(dateISO, "number_revealed"), false),
            tarotMainId = prefs.getInt(key(dateISO, "tarot_main_id"), -1).takeIf { it >= 0 },
            tarotMainResolved = prefs.getBoolean(key(dateISO, "tarot_resolved"), false),
            selectedMoodId = prefs.getString(key(dateISO, "mood_id"), null),
            checkInSubmitted = prefs.getBoolean(key(dateISO, "checkin"), false),
            guideNarrativeLoading = false,
        )

    fun saveSpine(dateISO: String, snapshot: RitualSpineSnapshot) {
        prefs.edit()
            .putBoolean(key(dateISO, "day_opened"), snapshot.dayOpened)
            .putBoolean(key(dateISO, "tarot_continue"), snapshot.tarotContinueAck)
            .putBoolean(key(dateISO, "number_revealed"), snapshot.numberRevealed)
            .putBoolean(key(dateISO, "tarot_resolved"), snapshot.tarotMainResolved)
            .putBoolean(key(dateISO, "checkin"), snapshot.checkInSubmitted)
            .apply {
                snapshot.tarotMainId?.let { putInt(key(dateISO, "tarot_main_id"), it) }
                    ?: remove(key(dateISO, "tarot_main_id"))
                snapshot.selectedMoodId?.let { putString(key(dateISO, "mood_id"), it) }
                    ?: remove(key(dateISO, "mood_id"))
            }
            .apply()
    }

    private fun key(dateISO: String, field: String): String = "todayflow.ritual.$dateISO.$field"

    companion object {
        private const val PREFS = "todayflow_day_engagement"
    }
}
