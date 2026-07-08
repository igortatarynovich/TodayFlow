package com.todayflow.today

import com.squareup.moshi.Json

data class TodayContractDomainLens(
    val status: String,
    val opportunity: String,
    val risk: String,
    val action: String,
)

data class TodayContractDomains(
    val relationships: TodayContractDomainLens,
    @Json(name = "money_work") val moneyWork: TodayContractDomainLens,
    val family: TodayContractDomainLens,
)

data class TodayContractDayStoryV1(
    @Json(name = "contract_version") val contractVersion: String,
    val theme: String? = null,
    val direction: String? = null,
    val story: String? = null,
    val `do`: List<String>? = null,
    val avoid: List<String>? = null,
    val advantage: String? = null,
    val abstain: String? = null,
    @Json(name = "today_move") val todayMove: String? = null,
) {
    fun headline(): String {
        val t = theme?.trim().orEmpty()
        if (t.isNotEmpty()) return t
        return story?.substringBefore('.')?.trim().orEmpty()
    }
}

data class TodayContractV1(
    @Json(name = "contract_version") val contractVersion: String,
    @Json(name = "global_context") val globalContext: Map<String, String>,
    @Json(name = "personal_growth") val personalGrowth: Map<String, String>,
    val domains: TodayContractDomains,
    @Json(name = "primary_action") val primaryAction: String,
    val progress: Map<String, String> = emptyMap(),
    @Json(name = "generation_id") val generationId: String,
    @Json(name = "day_story") val dayStory: TodayContractDayStoryV1? = null,
) {
    fun themeHeadline(): String {
        val fromStory = dayStory?.headline().orEmpty()
        if (fromStory.isNotEmpty()) return fromStory
        return globalContext["period"]?.trim().orEmpty()
    }
}

data class ProfileContractV1(
    @Json(name = "contract_version") val contractVersion: String,
    @Json(name = "identity_core") val identityCore: String,
    val strengths: List<String>,
    @Json(name = "growth_zones") val growthZones: List<String>,
    @Json(name = "relationship_style") val relationshipStyle: String,
    @Json(name = "money_style") val moneyStyle: String,
    @Json(name = "decision_style") val decisionStyle: String,
    @Json(name = "recurring_patterns") val recurringPatterns: List<String>,
    @Json(name = "living_changes") val livingChanges: String? = null,
)

data class TarotAnswerV1(
    @Json(name = "contract_version") val contractVersion: String,
    @Json(name = "question_text") val questionText: String,
    @Json(name = "main_answer") val mainAnswer: String,
    @Json(name = "story_narrative") val storyNarrative: String,
    @Json(name = "next_step") val nextStep: String,
    @Json(name = "generation_id") val generationId: String? = null,
)
