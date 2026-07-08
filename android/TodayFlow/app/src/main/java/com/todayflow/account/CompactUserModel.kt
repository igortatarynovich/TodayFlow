package com.todayflow.account

import com.squareup.moshi.Json

data class CompactUserModelInterpretationInstance(
    @Json(name = "instance_id") val instanceId: String? = null,
    @Json(name = "interpretation_ref_id") val interpretationRefId: String? = null,
    val level: String? = null,
    val summary: String? = null,
    @Json(name = "dominant_meaning") val dominantMeaning: String? = null,
    @Json(name = "confirmation_required") val confirmationRequired: Boolean? = null,
    @Json(name = "evidence_count") val evidenceCount: Int? = null,
    @Json(name = "user_verdict") val userVerdict: String? = null,
)

data class CompactUserModelResponse(
    @Json(name = "interpretation_instances_top_k") val interpretationInstancesTopK: List<CompactUserModelInterpretationInstance>? = null,
)

object InterpretationInstanceFilters {
    fun pendingCompatInstance(
        rows: List<CompactUserModelInterpretationInstance>?,
    ): CompactUserModelInterpretationInstance? =
        rows
            .orEmpty()
            .firstOrNull { row ->
                val ref = row.interpretationRefId.orEmpty()
                ref.startsWith("beh.compat_") &&
                    row.userVerdict.isNullOrBlank() &&
                    !row.summary.isNullOrBlank() &&
                    !row.instanceId.isNullOrBlank()
            }
}
