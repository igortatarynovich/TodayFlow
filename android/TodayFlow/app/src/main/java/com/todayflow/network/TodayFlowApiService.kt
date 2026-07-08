package com.todayflow.network

import com.todayflow.account.CompactUserModelResponse
import com.todayflow.compatibility.CompatibilityDynamicsRequest
import com.todayflow.compatibility.CompatibilityEncyclopediaResponse
import com.todayflow.compatibility.SignCompatibilityResponse
import com.todayflow.today.TodayContractV1
import com.squareup.moshi.Json
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Query

interface TodayFlowApiService {
    @GET("compatibility/encyclopedia")
    suspend fun getCompatibilityEncyclopedia(
        @Query("locale") locale: String,
        @Header("Accept-Language") acceptLanguage: String,
        @Header("Authorization") authorization: String? = null,
    ): CompatibilityEncyclopediaResponse

    @POST("compatibility/dynamics")
    suspend fun postCompatibilityDynamics(
        @Body body: CompatibilityDynamicsRequest,
        @Header("Accept-Language") acceptLanguage: String,
        @Header("Authorization") authorization: String? = null,
    ): SignCompatibilityResponse

    @POST("meaning/events")
    suspend fun postMeaningEvents(
        @Body body: MeaningEventsRequest,
        @Header("Authorization") authorization: String,
    ): MeaningEventsResponse

    @GET("account/compact-user-model")
    suspend fun getCompactUserModel(
        @Header("Authorization") authorization: String,
    ): CompactUserModelResponse

    @GET("today/contract")
    suspend fun getTodayContract(
        @Query("target_date") targetDate: String? = null,
        @Header("Accept-Language") acceptLanguage: String,
        @Header("Authorization") authorization: String,
    ): TodayContractV1
}

data class MeaningEventInput(
    @Json(name = "event_type") val eventType: String,
    @Json(name = "event_source") val eventSource: String,
    @Json(name = "local_date") val localDate: String? = null,
    @Json(name = "quality_score") val qualityScore: Double = 1.0,
    val payload: Map<String, String?>? = null,
    @Json(name = "idempotency_key") val idempotencyKey: String,
)

data class MeaningEventsRequest(
    val events: List<MeaningEventInput>,
)

data class MeaningEventsResponse(
    val accepted: Int,
    val deduplicated: Int,
    val total: Int,
)
