package com.todayflow.today

/**
 * Паритет iOS `applySpineEffects` (ветка `analyticsHint`) и веб `executeRitualSpineAnalytics`.
 * Конкретный транспорт (Firebase, свой бэкенд) — в лямбде [trackSurfaceEvent].
 */
fun executeRitualSpineAnalytics(
    hint: RitualSpineAnalyticsHint,
    numerologyValue: String,
    trackSurfaceEvent: (
        eventType: String,
        eventSource: String,
        qualityScore: Double?,
        payload: Map<String, Any?>,
    ) -> Unit,
    onTrackMood: ((String) -> Unit)? = null,
    guideGenerationId: Long? = null,
) {
    fun withGenerationId(base: Map<String, Any?>): Map<String, Any?> {
        val gid = guideGenerationId
        return if (gid != null && gid > 0L) base + ("generation_id" to gid) else base
    }
    when (hint) {
        RitualSpineAnalyticsHint.None -> Unit
        RitualSpineAnalyticsHint.NumberRevealed -> {
            val digit = numerologyValue.trim()
            if (digit.isEmpty()) return
            trackSurfaceEvent(
                "number_selected",
                "today",
                0.85,
                withGenerationId(mapOf("revealed" to true, "numerology_value" to digit)),
            )
        }
        is RitualSpineAnalyticsHint.MoodSelected -> {
            onTrackMood?.invoke(hint.moodId)
            trackSurfaceEvent(
                "mood_selected",
                "today",
                0.8,
                withGenerationId(mapOf("mood_id" to hint.moodId, "source" to "today_ritual")),
            )
        }
    }
}
