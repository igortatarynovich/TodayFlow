package com.todayflow.today

/**
 * Паритет с `frontend/src/components/today/ritualCueSanitizer.ts` и iOS `TodayRitualCueSanitizer.swift`.
 * Использовать, когда на Android появится UI ритуала «Сегодня».
 */
object RitualCueSanitizer {
    private const val CHAOS_LINE =
        "Осторожнее, если день начинает скатываться в хаос, резкие реакции и потерю своего ритма — держи одну линию, не хватайся за всё сразу."

    private val slugToRu: Map<String, String> =
        mapOf(
            "general" to "общий фон дня",
            "love" to "любовь и близость",
            "relations" to "отношения",
            "career" to "работа и карьера",
            "work" to "работа и карьера",
            "money" to "деньги и границы",
            "family" to "семья и дом",
            "home" to "семья и дом",
            "body" to "тело и восстановление",
            "health" to "тело и восстановление",
            "dialogue" to "общение и контакт",
            "communication" to "общение и контакт",
            "decision" to "решение, которое надо принять",
            "identity" to "линия про себя",
            "self" to "линия про себя",
        )

    private val headTopicSlugRu: Map<String, String> =
        mapOf(
            "general" to "общий фон дня",
            "body" to "тело и энергия",
            "money" to "деньги",
            "dialogue" to "общение и контакт",
            "family" to "семья и дом",
            "career" to "работа и дела",
            "love" to "близость и отношения",
        )

    private val moodSlugRu: Map<String, String> =
        mapOf(
            "calm" to "спокойно",
            "anxious" to "тревожно",
            "tired" to "устало",
            "driven" to "в драйве",
            "irritated" to "раздражённо",
            "other" to "другое",
            "motivated" to "в драйве",
            "confused" to "неясно",
            "quiet_wish" to "хочется тишины",
            "move_wish" to "хочется движения",
            "heavy" to "тяжело",
            "hopeful" to "с надеждой",
            "distant" to "на дистанции",
        )

    private val quotedServiceSlugToRu: Map<String, String> =
        buildMap {
            putAll(slugToRu)
            putAll(headTopicSlugRu)
            putAll(moodSlugRu)
        }

    private val quotedEnServiceSlug =
        Regex("""(?:['"]|«)([a-z][a-z0-9_]{0,31})(?:['"]|»)""", RegexOption.IGNORE_CASE)

    /** O5: паритет `ritual_cue_sanitize.replace_quoted_en_slugs_for_ru_display`. */
    @JvmStatic
    fun replaceQuotedEnSlugsForRuDisplay(raw: String?): String {
        val t = (raw ?: "").trim()
        if (t.isEmpty()) return ""
        return quotedEnServiceSlug.replace(t) { m ->
            val slug = m.groupValues[1].lowercase()
            val label = quotedServiceSlugToRu[slug]
            if (label != null) "«$label»" else m.value
        }
    }

    private val slugTopicJunk: Set<String> =
        setOf(
            "general",
            "overall",
            "dialogue",
            "communication",
            "mixed",
            "none",
            "other",
            "default",
        )

    /** Паритет `ritual_cue_sanitize._TOPIC_LABELS_NOT_ACTIONS` (O3). */
    private val topicOnly: Set<String> =
        setOf(
            "смысл и коммуникация",
            "смысл и коммуникации",
            "смысл и коммуникацию",
            "общий фокус дня",
            "общий фон дня",
            "общение и контакт",
            "смысл дня",
            "контекст дня",
            "рамка дня",
            "общая картина",
            "картина дня",
            "настрой на день",
            "тональность дня",
            "вектор дня",
            "форма дня",
            "сигнал дня",
            "паттерн дня",
        )

    /** O3: заголовок day_layer не только рубрика. */
    @JvmStatic
    fun isRuAbstractTopicHeadline(text: String?): Boolean {
        val t = (text ?: "").trim().lowercase()
        if (t.isEmpty()) return true
        return topicOnly.contains(t)
    }

    private val junkFocus: Set<String> =
        setOf(
            "general",
            "overall",
            "mixed",
            "none",
            "other",
            "default",
            "общее",
            "прочее",
            "другое",
            "без фокуса",
        )

    @JvmStatic
    fun humanizeFocusSlugForUi(slug: String): String {
        val k = slug.trim().lowercase()
        slugToRu[k]?.let { return it }
        if (Regex("^[a-z][a-z0-9_]{0,22}$").matches(k)) return "узкая тема дня"
        return slug.trim()
    }

    @JvmStatic
    fun isDiscardableMorningFocus(focus: String?): Boolean {
        val t = (focus ?: "").trim().lowercase()
        if (t.length < 2) return true
        if (junkFocus.contains(t)) return true
        if (Regex("^[a-z_]{1,20}$").matches(t)) return true
        return false
    }

    @JvmStatic
    fun isGarbageRitualActionCue(line: String?): Boolean {
        val raw = (line ?: "").trim()
        if (raw.isEmpty()) return true
        if (isDiscardableMorningFocus(raw)) return true
        val t = raw.lowercase()
        if (topicOnly.contains(t)) return true
        if (t.length <= 32 && Regex("^[\\s_a-z]+$").matches(t)) return true
        return false
    }

    private val quotedSlug = Regex("""['«]([a-z][a-z0-9_]{0,24})['»]""", RegexOption.IGNORE_CASE)

    @JvmStatic
    fun repairRitualDoNotEnterLine(raw: String?): String {
        val t = replaceQuotedEnSlugsForRuDisplay(raw)
        if (t.isEmpty()) return ""
        quotedSlug.find(t)?.groupValues?.getOrNull(1)?.let { slugRaw ->
            val slug = slugRaw.trim().lowercase()
            if (isDiscardableMorningFocus(slug) || slugTopicJunk.contains(slug)) {
                return CHAOS_LINE
            }
            val label = humanizeFocusSlugForUi(slugRaw)
            return "Осторожнее с темой «$label», если она начинает проживаться как хаос, резкие реакции и потеря своего ритма."
        }
        if (Regex("general", RegexOption.IGNORE_CASE).containsMatchIn(t) &&
            Regex("линию|линия", RegexOption.IGNORE_CASE).containsMatchIn(t)
        ) {
            return CHAOS_LINE
        }
        return t
    }

    /** Паритет `ritual_cue_sanitize.strip_llm_meta_commentary` / `stripLlmMetaCommentary` (TS). */
    private val llmMetaNeedles: List<String> =
        listOf(
            "не дублирую",
            "не дублируем",
            "я не дублиру",
            "чтобы экран не перегруж",
            "экран не перегружа",
            "карта и число остаются",
            "не дублирую их",
            "не дублируем их",
            "в сводке и в",
            "чтобы не перегруж",
            "чтобы не дублировать",
            "не дублирую информацию",
            "не дублируем информацию",
            "не повторяю блок",
            "не повторяю уже сказанное",
            "как просили в промпте",
            "как указано в задании",
            "в рамках формата ответа",
            "по требованиям к ответу",
            "согласно инструкции для модели",
            "убираю дублирование",
            "исключил дублирование",
            "дублирование с предыдущим",
            "уже было в предыдущем блоке",
            "из предыдущего абзаца",
            "as per the prompt",
            "as instructed, i will not",
            "i won't repeat the",
            "to avoid duplication",
            "avoiding repeating",
            "not repeating the card",
            "not repeating the number",
        )

    private val sentenceBoundarySplit = Regex("(?<=[.!?])\\s+")

    @JvmStatic
    fun stripLlmMetaCommentary(text: String?): String {
        val raw = (text ?: "").trim()
        if (raw.isEmpty()) return ""
        val low = raw.lowercase()
        if (llmMetaNeedles.none { low.contains(it) }) return raw
        return sentenceBoundarySplit
            .split(raw)
            .map { it.trim() }
            .filter { part ->
                part.isNotEmpty() && llmMetaNeedles.none { n -> part.lowercase().contains(n) }
            }
            .joinToString(" ")
            .trim()
    }
}
