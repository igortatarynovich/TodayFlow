package com.todayflow.guidance

/**
 * Зеркало контракта `GuidanceReadingResponse` (backend) для будущего Retrofit.
 * Имена полей — как в JSON (snake_case в API; Moshi с @Json).
 */
object GuidanceReadingModels {
    const val SCAFFOLD_NOTE =
        "Подключи API_BASE_URL, OAuth и UI расклада по образцу ios/TodayFlow (SwiftUI) и frontend Guidance."

    @Suppress("unused")
    data class FlowBridgeDto(
        val href: String,
        val label: String,
        val reason: String,
        val kind: String,
    )

    @Suppress("unused")
    data class SuggestedRouteDto(
        val href: String,
        val label: String,
        val reason: String,
    )
}
