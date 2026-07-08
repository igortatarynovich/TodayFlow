package com.todayflow.compatibility

import com.todayflow.account.CompactUserModelResponse
import com.todayflow.account.InterpretationInstanceFilters
import com.todayflow.network.ApiClient
import java.util.Locale

class CompatibilityRepository(
    private val authTokenProvider: () -> String? = { null },
) {
    suspend fun fetchEncyclopedia(locale: String): CompatibilityEncyclopediaResponse {
        val loc = if (locale.lowercase(Locale.US).startsWith("ru")) "ru" else "en"
        return ApiClient.service.getCompatibilityEncyclopedia(
            locale = loc,
            acceptLanguage = loc,
            authorization = ApiClient.bearerToken(authTokenProvider()),
        )
    }

    suspend fun postDynamics(body: CompatibilityDynamicsRequest): SignCompatibilityResponse =
        ApiClient.service.postCompatibilityDynamics(
            body = body,
            acceptLanguage = body.locale ?: "ru",
            authorization = ApiClient.bearerToken(authTokenProvider()),
        )

    suspend fun fetchCompactUserModel(): CompactUserModelResponse {
        val token =
            ApiClient.bearerToken(authTokenProvider())
                ?: throw IllegalStateException("auth required for compact user model")
        return ApiClient.service.getCompactUserModel(token)
    }

    suspend fun fetchPendingCompatIlrInstance() =
        InterpretationInstanceFilters.pendingCompatInstance(
            fetchCompactUserModel().interpretationInstancesTopK,
        )
}
