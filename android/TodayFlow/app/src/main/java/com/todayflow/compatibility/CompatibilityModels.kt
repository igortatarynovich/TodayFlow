package com.todayflow.compatibility

import com.squareup.moshi.Json

data class EncyclopediaIntroBlock(
    val kind: String = "paragraph",
    val text: String? = null,
    val items: List<String>? = null,
)

data class EncyclopediaAnalyzeParams(
    val topic: String? = null,
    val reading: String? = null,
    val series: String? = null,
)

data class CompatibilityEncyclopediaHero(
    val eyebrow: String,
    val title: String,
    val lead: String,
)

data class CompatibilityEncyclopediaCategory(
    val id: String,
    val emoji: String,
    val title: String,
    val subtitle: String,
    @Json(name = "analyze_params") val analyzeParams: EncyclopediaAnalyzeParams,
    @Json(name = "intro_blocks") val introBlocks: List<EncyclopediaIntroBlock>? = null,
)

data class CompatibilityEncyclopediaReading(
    val id: String,
    val title: String,
    @Json(name = "analyze_params") val analyzeParams: EncyclopediaAnalyzeParams,
    @Json(name = "intro_blocks") val introBlocks: List<EncyclopediaIntroBlock>? = null,
)

data class CompatibilityEncyclopediaSeries(
    val id: String,
    val title: String,
    val subtitle: String,
    @Json(name = "analyze_params") val analyzeParams: EncyclopediaAnalyzeParams,
    @Json(name = "intro_blocks") val introBlocks: List<EncyclopediaIntroBlock>? = null,
    @Json(name = "scenario_bullets") val scenarioBullets: List<String>? = null,
)

data class CompatibilityEncyclopediaResponse(
    @Json(name = "content_locale") val contentLocale: String,
    val version: String,
    val hero: CompatibilityEncyclopediaHero,
    val categories: List<CompatibilityEncyclopediaCategory>,
    @Json(name = "popular_readings") val popularReadings: List<CompatibilityEncyclopediaReading>,
    val series: List<CompatibilityEncyclopediaSeries>,
    @Json(name = "entry_routes") val entryRoutes: Map<String, String>? = null,
)

data class EncyclopediaAnalyzeSelection(
    val label: String,
    val selectionKind: String,
    val selectionId: String,
    val topicId: String? = null,
    val readingId: String? = null,
    val seriesId: String? = null,
    val introBlocks: List<EncyclopediaIntroBlock> = emptyList(),
    val scenarioBullets: List<String> = emptyList(),
)

data class CompatibilityDynamicsRequest(
    val mode: String,
    @Json(name = "from_sign") val fromSign: String? = null,
    @Json(name = "to_sign") val toSign: String? = null,
    @Json(name = "relationship_context") val relationshipContext: String? = null,
    val generation: String = "llm",
    @Json(name = "name_1") val name1: String? = null,
    @Json(name = "name_2") val name2: String? = null,
    @Json(name = "birth_date_1") val birthDate1: String? = null,
    @Json(name = "birth_date_2") val birthDate2: String? = null,
    @Json(name = "include_personalized") val includePersonalized: Boolean = true,
    val locale: String? = null,
    @Json(name = "topic_id") val topicId: String? = null,
    @Json(name = "reading_id") val readingId: String? = null,
    @Json(name = "series_id") val seriesId: String? = null,
)

data class SignCompatibilitySubscores(
    val attraction: Int,
    val stability: Int,
    val conflicts: Int,
    val sexuality: Int,
)

data class SignCompatibilityAnalysisBlock(
    val key: String,
    val title: String,
    val subtitle: String,
    val takeaway: String,
    val detail: String,
    val risk: String,
    val action: String,
)

data class SignCompatibilityRoles(
    @Json(name = "you_bullets") val youBullets: List<String>,
    @Json(name = "partner_bullets") val partnerBullets: List<String>,
)

data class SignCompatibilityProductSurface(
    @Json(name = "score_tagline") val scoreTagline: String,
    val subscores: SignCompatibilitySubscores,
    @Json(name = "overview_paragraphs") val overviewParagraphs: List<String>,
    val blocks: List<SignCompatibilityAnalysisBlock>,
    val roles: SignCompatibilityRoles,
)

data class AttachmentStyleHint(
    val code: String,
    val label: String,
    val summary: String,
    @Json(name = "evidence_blocks") val evidenceBlocks: List<String>? = null,
)

data class AttachmentReference(
    @Json(name = "attachment_style_hints") val attachmentStyleHints: List<AttachmentStyleHint>? = null,
    @Json(name = "reference_status") val referenceStatus: String? = null,
)

data class SignCompatibilityResponse(
    @Json(name = "from_sign") val fromSign: String,
    @Json(name = "to_sign") val toSign: String,
    @Json(name = "from_sign_name") val fromSignName: String,
    @Json(name = "to_sign_name") val toSignName: String,
    val score: Int,
    val summary: String,
    @Json(name = "product_surface") val productSurface: SignCompatibilityProductSurface? = null,
    @Json(name = "content_locale") val contentLocale: String? = null,
    @Json(name = "generation_source") val generationSource: String? = null,
    @Json(name = "attachment_reference") val attachmentReference: AttachmentReference? = null,
)

enum class ZodiacSign(val apiId: String, val titleRu: String, val titleEn: String) {
    ARIES("aries", "Овен", "Aries"),
    TAURUS("taurus", "Телец", "Taurus"),
    GEMINI("gemini", "Близнецы", "Gemini"),
    CANCER("cancer", "Рак", "Cancer"),
    LEO("leo", "Лев", "Leo"),
    VIRGO("virgo", "Дева", "Virgo"),
    LIBRA("libra", "Весы", "Libra"),
    SCORPIO("scorpio", "Скорпион", "Scorpio"),
    SAGITTARIUS("sagittarius", "Стрелец", "Sagittarius"),
    CAPRICORN("capricorn", "Козерог", "Capricorn"),
    AQUARIUS("aquarius", "Водолей", "Aquarius"),
    PISCES("pisces", "Рыбы", "Pisces"),
    ;

    fun title(useRussian: Boolean): String = if (useRussian) titleRu else titleEn
}

enum class RelationshipContext(val apiId: String, val labelRu: String, val labelEn: String) {
    JUST_MET("just_met", "Только познакомились", "Just met"),
    MUTUAL_ATTRACTION("mutual_attraction", "Есть притяжение", "Mutual attraction"),
    IN_RELATIONSHIP("in_relationship", "Уже в отношениях", "In a relationship"),
    UNCLEAR("unclear", "Непонятная ситуация", "Unclear situation"),
    CONFLICT_DISTANCE("conflict_distance", "Конфликт или дистанция", "Conflict or distance"),
    SPLIT_BUT_PULL("split_but_pull", "Расстались, но тянет", "Split but still pulled"),
    ;

    fun label(useRussian: Boolean): String = if (useRussian) labelRu else labelEn
}

object CompatibilitySelectionMapper {
    fun fromCategory(item: CompatibilityEncyclopediaCategory): EncyclopediaAnalyzeSelection =
        EncyclopediaAnalyzeSelection(
            label = item.title,
            selectionKind = "category",
            selectionId = item.id,
            topicId = item.analyzeParams.topic,
            readingId = item.analyzeParams.reading,
            seriesId = item.analyzeParams.series,
            introBlocks = item.introBlocks.orEmpty(),
        )

    fun fromReading(item: CompatibilityEncyclopediaReading): EncyclopediaAnalyzeSelection =
        EncyclopediaAnalyzeSelection(
            label = item.title,
            selectionKind = "reading",
            selectionId = item.id,
            topicId = item.analyzeParams.topic,
            readingId = item.analyzeParams.reading,
            seriesId = item.analyzeParams.series,
            introBlocks = item.introBlocks.orEmpty(),
        )

    fun fromSeries(item: CompatibilityEncyclopediaSeries): EncyclopediaAnalyzeSelection =
        EncyclopediaAnalyzeSelection(
            label = item.title,
            selectionKind = "series",
            selectionId = item.id,
            topicId = item.analyzeParams.topic,
            readingId = item.analyzeParams.reading,
            seriesId = item.analyzeParams.series,
            introBlocks = item.introBlocks.orEmpty(),
            scenarioBullets = item.scenarioBullets.orEmpty(),
        )

    fun topicSelectPayload(selection: EncyclopediaAnalyzeSelection): Map<String, String?> =
        mapOf(
            "selection_kind" to selection.selectionKind,
            "selection_id" to selection.selectionId,
            "topic_id" to selection.topicId,
            "reading_id" to selection.readingId,
            "series_id" to selection.seriesId,
        )
}
