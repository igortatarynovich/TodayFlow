package com.todayflow.meaning

import android.content.Context
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import com.todayflow.network.ApiClient
import com.todayflow.network.MeaningEventInput
import com.todayflow.network.MeaningEventsRequest
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.util.UUID

/**
 * Lightweight meaning-event outbox — parity with web/iOS learning surfaces.
 */
class MeaningEventTracker(context: Context) {
    private val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val moshi =
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    private val listType = Types.newParameterizedType(List::class.java, MeaningEventInput::class.java)
    private val listAdapter = moshi.adapter<List<MeaningEventInput>>(listType)

    fun track(
        eventType: String,
        eventSource: String,
        payload: Map<String, String?> = emptyMap(),
        authToken: String? = null,
        idempotencyKey: String? = null,
    ) {
        val event =
            MeaningEventInput(
                eventType = eventType,
                eventSource = eventSource,
                localDate = LocalDate.now().toString(),
                payload = payload.ifEmpty { null },
                idempotencyKey = idempotencyKey ?: "android-${UUID.randomUUID()}",
            )
        val outbox = loadOutbox().toMutableList()
        outbox.add(event)
        saveOutbox(outbox.takeLast(MAX_OUTBOX))
        flush(authToken)
    }

    fun flush(authToken: String?) {
        val token = ApiClient.bearerToken(authToken) ?: return
        scope.launch {
            var outbox = loadOutbox()
            while (outbox.isNotEmpty()) {
                val batch = outbox.take(BATCH_SIZE)
                try {
                    ApiClient.service.postMeaningEvents(
                        MeaningEventsRequest(batch),
                        token,
                    )
                    outbox = outbox.drop(batch.size)
                    saveOutbox(outbox)
                } catch (_: Exception) {
                    break
                }
            }
        }
    }

    private fun loadOutbox(): List<MeaningEventInput> {
        val raw = prefs.getString(OUTBOX_KEY, null) ?: return emptyList()
        return listAdapter.fromJson(raw).orEmpty()
    }

    private fun saveOutbox(events: List<MeaningEventInput>) {
        prefs.edit().putString(OUTBOX_KEY, listAdapter.toJson(events)).apply()
    }

    companion object {
        private const val PREFS = "todayflow_meaning"
        private const val OUTBOX_KEY = "outbox"
        private const val MAX_OUTBOX = 500
        private const val BATCH_SIZE = 50
    }
}
