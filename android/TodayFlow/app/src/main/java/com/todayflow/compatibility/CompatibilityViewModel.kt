package com.todayflow.compatibility

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.todayflow.account.CompactUserModelInterpretationInstance
import com.todayflow.meaning.MeaningEventTracker
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

enum class AnalyzeEntryMode { QUICK, PRECISE }

data class CompatibilityUiState(
    val catalog: CompatibilityEncyclopediaResponse? = null,
    val catalogLoading: Boolean = false,
    val catalogError: String? = null,
    val selected: EncyclopediaAnalyzeSelection? = null,
    val entryMode: AnalyzeEntryMode = AnalyzeEntryMode.QUICK,
    val signFrom: ZodiacSign = ZodiacSign.ARIES,
    val signTo: ZodiacSign = ZodiacSign.LIBRA,
    val birthDate1: String = "1992-03-21",
    val birthDate2: String = "1994-10-15",
    val name1: String = "",
    val name2: String = "",
    val relationshipContext: RelationshipContext? = null,
    val dynamicsLoading: Boolean = false,
    val dynamicsError: String? = null,
    val dynamicsResult: SignCompatibilityResponse? = null,
    val compatIlrInstance: CompactUserModelInterpretationInstance? = null,
)

class CompatibilityViewModel(
    private val repository: CompatibilityRepository,
    private val meaningTracker: MeaningEventTracker,
    private val authTokenProvider: () -> String? = { null },
) : ViewModel() {
    private val _uiState = MutableStateFlow(CompatibilityUiState())
    val uiState: StateFlow<CompatibilityUiState> = _uiState.asStateFlow()

    private var encyclopediaViewTracked = false

    fun loadEncyclopedia() {
        if (_uiState.value.catalogLoading) return
        viewModelScope.launch {
            _uiState.update { it.copy(catalogLoading = true, catalogError = null) }
            try {
                val locale = Locale.getDefault().language
                val catalog = repository.fetchEncyclopedia(locale)
                _uiState.update { it.copy(catalog = catalog, catalogLoading = false) }
                if (!encyclopediaViewTracked) {
                    encyclopediaViewTracked = true
                    meaningTracker.track(
                        eventType = "compatibility_encyclopedia_view",
                        eventSource = "compatibility",
                        payload =
                            mapOf(
                                "content_locale" to catalog.contentLocale,
                                "catalog_version" to catalog.version,
                            ),
                        authToken = authTokenProvider(),
                    )
                }
            } catch (_: Exception) {
                _uiState.update {
                    it.copy(
                        catalogLoading = false,
                        catalogError = CompatibilityChrome.loadError,
                    )
                }
            }
        }
    }

    fun selectTopic(selection: EncyclopediaAnalyzeSelection) {
        _uiState.update {
            it.copy(
                selected = selection,
                dynamicsResult = null,
                dynamicsError = null,
            )
        }
        val payload = CompatibilitySelectionMapper.topicSelectPayload(selection)
        meaningTracker.track(
            eventType = "compatibility_topic_select",
            eventSource = "compatibility",
            payload = payload.filterValues { value -> value != null }.mapValues { (_, v) -> v!! },
            authToken = authTokenProvider(),
        )
    }

    fun clearSelection() {
        _uiState.update { it.copy(selected = null, dynamicsResult = null, dynamicsError = null) }
    }

    fun setEntryMode(mode: AnalyzeEntryMode) {
        _uiState.update { it.copy(entryMode = mode) }
    }

    fun setSignFrom(sign: ZodiacSign) {
        _uiState.update { it.copy(signFrom = sign) }
    }

    fun setSignTo(sign: ZodiacSign) {
        _uiState.update { it.copy(signTo = sign) }
    }

    fun setBirthDate1(value: String) {
        _uiState.update { it.copy(birthDate1 = value) }
    }

    fun setBirthDate2(value: String) {
        _uiState.update { it.copy(birthDate2 = value) }
    }

    fun setName1(value: String) {
        _uiState.update { it.copy(name1 = value) }
    }

    fun setName2(value: String) {
        _uiState.update { it.copy(name2 = value) }
    }

    fun setRelationshipContext(context: RelationshipContext?) {
        _uiState.update { it.copy(relationshipContext = context) }
    }

    fun runDynamics() {
        val state = _uiState.value
        val selection = state.selected ?: return
        if (state.dynamicsLoading) return

        viewModelScope.launch {
            _uiState.update { it.copy(dynamicsLoading = true, dynamicsError = null) }
            val locale = if (CompatibilityChrome.useRussian()) "ru" else "en"
            val trimmedName1 = state.name1.trim()
            val trimmedName2 = state.name2.trim()
            val request =
                if (state.entryMode == AnalyzeEntryMode.PRECISE) {
                    CompatibilityDynamicsRequest(
                        mode = "precise",
                        birthDate1 = state.birthDate1,
                        birthDate2 = state.birthDate2,
                        relationshipContext = state.relationshipContext?.apiId,
                        generation = "llm",
                        name1 = trimmedName1.ifEmpty { null },
                        name2 = trimmedName2.ifEmpty { null },
                        includePersonalized = true,
                        locale = locale,
                        topicId = selection.topicId,
                        readingId = selection.readingId,
                        seriesId = selection.seriesId,
                    )
                } else {
                    CompatibilityDynamicsRequest(
                        mode = "quick",
                        fromSign = state.signFrom.apiId,
                        toSign = state.signTo.apiId,
                        relationshipContext = state.relationshipContext?.apiId,
                        generation = "llm",
                        name1 = trimmedName1.ifEmpty { null },
                        name2 = trimmedName2.ifEmpty { null },
                        includePersonalized = true,
                        locale = locale,
                        topicId = selection.topicId,
                        readingId = selection.readingId,
                        seriesId = selection.seriesId,
                    )
                }

            try {
                val response = repository.postDynamics(request)
                _uiState.update { it.copy(dynamicsLoading = false, dynamicsResult = response) }
                loadCompatIlrInstance()
                val payload =
                    buildMap {
                        put("selection_kind", selection.selectionKind)
                        put("selection_id", selection.selectionId)
                        put("mode", state.entryMode.name.lowercase(Locale.US))
                        put("from_sign", response.fromSign)
                        put("to_sign", response.toSign)
                        put("score", response.score.toString())
                        selection.topicId?.let { put("topic_id", it) }
                        selection.readingId?.let { put("reading_id", it) }
                        selection.seriesId?.let { put("series_id", it) }
                    }
                meaningTracker.track(
                    eventType = "compatibility_view",
                    eventSource = "compatibility",
                    payload = payload,
                    authToken = authTokenProvider(),
                )
            } catch (_: Exception) {
                _uiState.update {
                    it.copy(
                        dynamicsLoading = false,
                        dynamicsError = CompatibilityChrome.dynamicsError,
                        dynamicsResult = null,
                    )
                }
            }
        }
    }

    fun loadCompatIlrInstance() {
        if (authTokenProvider().isNullOrBlank()) {
            _uiState.update { it.copy(compatIlrInstance = null) }
            return
        }
        viewModelScope.launch {
            try {
                val instance = repository.fetchPendingCompatIlrInstance()
                _uiState.update { it.copy(compatIlrInstance = instance) }
            } catch (_: Exception) {
                _uiState.update { it.copy(compatIlrInstance = null) }
            }
        }
    }

    fun trackInterpretationInstanceConfirm(
        instanceId: String,
        interpretationRefId: String?,
        summary: String,
        echo: String,
        scenarioId: String? = null,
    ) {
        val correction =
            when (echo) {
                "yes" -> "confirm"
                "partial" -> "partial"
                else -> "reject"
            }
        val dayKey = LocalDate.now().toString()
        meaningTracker.track(
            eventType = "interpretation_instance_confirm",
            eventSource = "compatibility",
            payload =
                mapOf(
                    "surface" to "analyze_dynamics",
                    "scenario_id" to scenarioId,
                    "instance_id" to instanceId,
                    "interpretation_ref_id" to interpretationRefId,
                    "correction" to correction,
                    "verdict" to correction,
                    "summary" to summary,
                ),
            authToken = authTokenProvider(),
            idempotencyKey = "interpretation_instance_confirm:$instanceId:$echo:$dayKey",
        )
        _uiState.update { it.copy(compatIlrInstance = null) }
        loadCompatIlrInstance()
    }

    fun trackAttachmentLensConfirm(
        code: String,
        label: String,
        summary: String,
        echo: String,
        knowledgeId: String,
    ) {
        val correction =
            when (echo) {
                "yes" -> "confirm"
                "partial" -> "partial"
                else -> "reject"
            }
        meaningTracker.track(
            eventType = "compatibility_attachment_confirm",
            eventSource = "compatibility",
            payload =
                mapOf(
                    "surface" to "analyze_dynamics",
                    "attachment_style_code" to code,
                    "label" to label,
                    "summary" to summary,
                    "echo" to echo,
                    "verdict" to correction,
                    "knowledge_id" to knowledgeId,
                ),
            authToken = authTokenProvider(),
        )
        meaningTracker.track(
            eventType = "profile_atom_correction",
            eventSource = "compatibility",
            payload =
                mapOf(
                    "knowledge_id" to knowledgeId,
                    "correction" to correction,
                    "claim_summary" to summary,
                    "surface" to "analyze_dynamics",
                    "attachment_style_code" to code,
                ),
            authToken = authTokenProvider(),
        )
    }

    companion object {
        val birthDateFormatter: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE

        fun formatBirthDate(date: LocalDate): String = date.format(birthDateFormatter)
    }
}
