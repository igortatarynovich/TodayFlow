package com.todayflow.today

/**
 * Паритет `narrative_hierarchy` в HTTP payload guide (O2) с веб `parseNarrativeHierarchyFromGuide`
 * и iOS `TodayGuideActionable.narrativeHierarchyDisplay`.
 */
data class NarrativeHierarchyDisplay(
    val contractVersion: String,
    val primaryAnchorKey: String,
)

object GuideNarrativeHierarchy {
    const val CONTRACT_V0: String = "narrative_hierarchy_v0"
    const val PRIMARY_ANCHOR_DAY_ENGINE_BRIEF: String = "day_engine_brief"

    fun narrativeHierarchyFromGuidePayload(payload: Map<String, Any?>?): NarrativeHierarchyDisplay? {
        if (payload == null) return null
        val raw = payload["narrative_hierarchy"] ?: return null
        if (raw !is Map<*, *>) return null
        @Suppress("UNCHECKED_CAST")
        val h = raw as Map<String, Any?>
        val cv = (h["contract_version"] as? String)?.trim().orEmpty()
        val pa = (h["primary_anchor"] as? String)?.trim().orEmpty()
        if (cv != CONTRACT_V0 || pa != PRIMARY_ANCHOR_DAY_ENGINE_BRIEF) return null
        return NarrativeHierarchyDisplay(contractVersion = cv, primaryAnchorKey = pa)
    }
}

/** Паритет `guide_pipeline` / `guide_contract_v2` (DE-13 v5). */
data class GuidePipelineDisplay(
    val contractVersion: String,
    val generationMode: String,
    val coreSource: String?,
)

object GuideContractV2 {
    const val GUIDE_CONTRACT_V2: String = "guide_contract_v2"
    const val PIPELINE_V0: String = "guide_pipeline_v0"

    fun guidePipelineFromGuidePayload(payload: Map<String, Any?>?): GuidePipelineDisplay? {
        if (payload == null) return null
        if ((payload["contract_version"] as? String)?.trim() != GUIDE_CONTRACT_V2) return null
        val raw = payload["guide_pipeline"] ?: return null
        if (raw !is Map<*, *>) return null
        @Suppress("UNCHECKED_CAST")
        val p = raw as Map<String, Any?>
        if ((p["contract_version"] as? String)?.trim() != PIPELINE_V0) return null
        val mode = (p["generation_mode"] as? String)?.trim().orEmpty()
        if (mode != "funnel" && mode != "monolith") return null
        var coreSource: String? = null
        val steps = p["steps"]
        if (steps is Map<*, *>) {
            @Suppress("UNCHECKED_CAST")
            val core = (steps as Map<String, Any?>)["core_text"]
            if (core is Map<*, *>) {
                coreSource = (core["source"] as? String)?.trim()?.ifEmpty { null }
            }
        }
        return GuidePipelineDisplay(contractVersion = PIPELINE_V0, generationMode = mode, coreSource = coreSource)
    }
}
