package com.todayflow.today

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ExecuteRitualSpineAnalyticsTest {

    @Test
    fun none_doesNothing() {
        val calls = mutableListOf<String>()
        executeRitualSpineAnalytics(
            RitualSpineAnalyticsHint.None,
            numerologyValue = "7",
            trackSurfaceEvent = { _, _, _, _ -> calls += "track" },
            onTrackMood = { calls += "mood" },
        )
        assertTrue(calls.isEmpty())
    }

    @Test
    fun numberRevealed_skipsWhenNumerologyBlank() {
        var tracked = 0
        executeRitualSpineAnalytics(
            RitualSpineAnalyticsHint.NumberRevealed,
            numerologyValue = "   ",
            trackSurfaceEvent = { _, _, _, _ -> tracked++ },
        )
        assertEquals(0, tracked)
    }

    @Test
    fun numberRevealed_sendsNumberSelected() {
        var type: String? = null
        var score: Double? = null
        var payload: Map<String, Any?>? = null
        executeRitualSpineAnalytics(
            RitualSpineAnalyticsHint.NumberRevealed,
            numerologyValue = "3",
            trackSurfaceEvent = { t, src, q, p ->
                assertEquals("today", src)
                type = t
                score = q
                payload = p
            },
        )
        assertEquals("number_selected", type)
        assertEquals(0.85, score)
        assertEquals(true, payload?.get("revealed"))
        assertEquals("3", payload?.get("numerology_value"))
    }

    @Test
    fun numberRevealed_includesGenerationIdWhenProvided() {
        var payload: Map<String, Any?>? = null
        executeRitualSpineAnalytics(
            RitualSpineAnalyticsHint.NumberRevealed,
            numerologyValue = "3",
            trackSurfaceEvent = { _, _, _, p -> payload = p },
            guideGenerationId = 9001L,
        )
        assertEquals(9001L, payload?.get("generation_id"))
    }

    @Test
    fun moodSelected_onTrackMoodBeforeTrack() {
        val order = mutableListOf<String>()
        executeRitualSpineAnalytics(
            RitualSpineAnalyticsHint.MoodSelected("tired"),
            numerologyValue = "",
            trackSurfaceEvent = { _, _, _, _ -> order += "track" },
            onTrackMood = { order += "mood:${it}" },
        )
        assertEquals(listOf("mood:tired", "track"), order)
    }

    @Test
    fun moodSelected_withoutCallback_stillTracks() {
        var type: String? = null
        executeRitualSpineAnalytics(
            RitualSpineAnalyticsHint.MoodSelected("calm"),
            numerologyValue = "1",
            trackSurfaceEvent = { t, _, q, p ->
                type = t
                assertEquals(0.8, q)
                assertEquals("calm", p["mood_id"])
                assertEquals("today_ritual", p["source"])
            },
            onTrackMood = null,
        )
        assertEquals("mood_selected", type)
    }
}
