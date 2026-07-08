package com.todayflow.today

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class GuideNarrativeHierarchyTest {
    @Test
    fun parses_v0() {
        val payload =
            mapOf(
                "narrative_hierarchy" to
                    mapOf(
                        "contract_version" to GuideNarrativeHierarchy.CONTRACT_V0,
                        "primary_anchor" to GuideNarrativeHierarchy.PRIMARY_ANCHOR_DAY_ENGINE_BRIEF,
                    ),
            )
        val out = GuideNarrativeHierarchy.narrativeHierarchyFromGuidePayload(payload)
        assertEquals(GuideNarrativeHierarchy.CONTRACT_V0, out?.contractVersion)
        assertEquals(GuideNarrativeHierarchy.PRIMARY_ANCHOR_DAY_ENGINE_BRIEF, out?.primaryAnchorKey)
    }

    @Test
    fun rejects_wrong_contract() {
        val payload =
            mapOf(
                "narrative_hierarchy" to
                    mapOf(
                        "contract_version" to "other",
                        "primary_anchor" to GuideNarrativeHierarchy.PRIMARY_ANCHOR_DAY_ENGINE_BRIEF,
                    ),
            )
        assertNull(GuideNarrativeHierarchy.narrativeHierarchyFromGuidePayload(payload))
    }

    @Test
    fun rejects_missing() {
        assertNull(GuideNarrativeHierarchy.narrativeHierarchyFromGuidePayload(null))
        assertNull(GuideNarrativeHierarchy.narrativeHierarchyFromGuidePayload(emptyMap()))
    }

    @Test
    fun parses_guide_pipeline_v2() {
        val payload =
            mapOf(
                "contract_version" to GuideContractV2.GUIDE_CONTRACT_V2,
                "guide_pipeline" to
                    mapOf(
                        "contract_version" to GuideContractV2.PIPELINE_V0,
                        "generation_mode" to "funnel",
                        "steps" to mapOf("core_text" to mapOf("source" to "funnel_core_text_v0")),
                    ),
            )
        val out = GuideContractV2.guidePipelineFromGuidePayload(payload)
        assertEquals(GuideContractV2.PIPELINE_V0, out?.contractVersion)
        assertEquals("funnel", out?.generationMode)
        assertEquals("funnel_core_text_v0", out?.coreSource)
    }
}
