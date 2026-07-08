package com.todayflow.today

import com.todayflow.network.TodayFlowApiService

class TodayRepository(
    private val api: TodayFlowApiService,
    private val authTokenProvider: () -> String?,
) {
    suspend fun fetchTodayContract(targetDate: String? = null): TodayContractV1? {
        val token = authTokenProvider()?.let { "Bearer $it" } ?: return null
        return api.getTodayContract(
            targetDate = targetDate,
            acceptLanguage = "ru,en;q=0.9",
            authorization = token,
        )
    }
}
