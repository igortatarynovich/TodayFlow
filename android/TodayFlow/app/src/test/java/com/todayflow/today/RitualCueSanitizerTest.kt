package com.todayflow.today

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RitualCueSanitizerTest {
    @Test
    fun repair_replaces_quoted_general() {
        val raw = "Не заходить в линию 'general', если хаос."
        val out = RitualCueSanitizer.repairRitualDoNotEnterLine(raw)
        assertFalse(out.lowercase().contains("general"))
        assertFalse(out.lowercase().contains("линию"))
        assertTrue(out.contains("хаос"))
    }

    @Test
    fun garbage_detects_topic_label() {
        assertTrue(RitualCueSanitizer.isGarbageRitualActionCue("Смысл и коммуникация"))
        assertFalse(RitualCueSanitizer.isGarbageRitualActionCue("До обеда выбрать одну задачу"))
    }

    @Test
    fun o3_abstract_topic_headline() {
        assertTrue(RitualCueSanitizer.isRuAbstractTopicHeadline("Картина дня"))
        assertFalse(RitualCueSanitizer.isRuAbstractTopicHeadline("Один завершённый шаг до обеда"))
    }

    @Test
    fun o5_replace_quoted_mood_slug() {
        val out = RitualCueSanitizer.replaceQuotedEnSlugsForRuDisplay("Настроение «tired» — мягче.")
        assertFalse(out.lowercase().contains("tired"))
        assertTrue(out.contains("устало"))
    }

    @Test
    fun strip_llm_meta_drops_meta_sentences() {
        val raw =
            "Коротко: держи фокус. Карта и число остаются в сводке — я не дублирую их большими блоками. " +
                "Дальше — один шаг."
        val out = RitualCueSanitizer.stripLlmMetaCommentary(raw)
        assertFalse(out.lowercase().contains("не дублиру"))
        assertTrue(out.lowercase().contains("шаг"))
    }
}
