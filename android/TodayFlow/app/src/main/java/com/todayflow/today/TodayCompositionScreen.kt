package com.todayflow.today

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.LocalDate

private val ritualMoods =
    listOf(
        "calm" to "спокойствие",
        "focused" to "фокус",
        "tired" to "усталость",
        "quiet_wish" to "хочется тишины",
        "anxious" to "тревога",
    )

@Composable
fun TodayCompositionScreen(
    repository: TodayRepository,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val engagementStore = remember { DayEngagementStore(context) }
    val dateISO = remember { LocalDate.now().toString() }

    var contract by remember { mutableStateOf<TodayContractV1?>(null) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    var spine by remember { mutableStateOf(engagementStore.loadSpine(dateISO)) }

    fun persist(next: RitualSpineSnapshot) {
        spine = next
        engagementStore.saveSpine(dateISO, next)
    }

    fun dispatch(event: RitualSpineUserEvent) {
        val result = TodayRitualSpineReducer.apply(event, spine) ?: return
        persist(result.first)
    }

    LaunchedEffect(repository, dateISO) {
        loading = true
        error = null
        contract =
            withContext(Dispatchers.IO) {
                runCatching { repository.fetchTodayContract(dateISO) }.getOrNull()
            }
        if (contract == null) {
            error = "Не удалось загрузить контракт дня"
        }
        spine = engagementStore.loadSpine(dateISO)
        loading = false
    }

    val phase = TodayRitualSpinePhaseResolver.phase(spine)
    val tarotId = spine.tarotMainId ?: deterministicTarotId(dateISO)
    val personalDayNumber = deterministicPersonalDay(dateISO)

    Column(
        modifier =
            modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("Сегодня", style = MaterialTheme.typography.headlineMedium)

        when {
            loading -> CircularProgressIndicator()
            contract != null -> {
                val c = contract!!
                CompositionFoundationBlock(contract = c)

                when (phase) {
                    "not_started" -> {
                        Text(
                            "Открой день — карта, число и настроение соберут персональную линию.",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Button(onClick = { dispatch(RitualSpineUserEvent.OpenedDay) }, modifier = Modifier.fillMaxWidth()) {
                            Text("Открыть день")
                        }
                    }
                    "tarot_interactive" -> {
                        RitualGateCard(
                            title = "Карта дня",
                            body = "Карта #$tarotId — символ, через который смотрим на день.",
                        )
                        if (!spine.tarotMainResolved) {
                            Button(
                                onClick = {
                                    persist(
                                        spine.copy(
                                            tarotMainId = tarotId,
                                            tarotMainResolved = true,
                                        ),
                                    )
                                },
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text("Принять карту")
                            }
                        } else {
                            Button(
                                onClick = { dispatch(RitualSpineUserEvent.ContinuedPastTarot) },
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text("Продолжить")
                            }
                        }
                    }
                    "number_selecting" -> {
                        RitualGateCard(
                            title = "Число дня",
                            body = "Число $personalDayNumber — ритм, в котором проще держать темп.",
                        )
                        Button(
                            onClick = { dispatch(RitualSpineUserEvent.RevealedNumber) },
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Раскрыть число")
                        }
                    }
                    "check_in" -> {
                        RitualGateCard(
                            title = "Как ты сейчас?",
                            body = "Короткий check-in помогает подстроить фокус дня.",
                        )
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            ritualMoods.forEach { (id, label) ->
                                FilterChip(
                                    selected = spine.selectedMoodId == id,
                                    onClick = { dispatch(RitualSpineUserEvent.SelectedMood(id)) },
                                    label = { Text(label) },
                                )
                            }
                        }
                        Button(
                            onClick = { dispatch(RitualSpineUserEvent.SubmittedCheckIn) },
                            enabled = spine.selectedMoodId != null && spine.tarotMainResolved,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Собрать мой день")
                        }
                    }
                    else -> {
                        PersonalizedDayBlock(contract = c, moodId = spine.selectedMoodId)
                        OutlinedButton(
                            onClick = {
                                persist(
                                    RitualSpineSnapshot(
                                        dayOpened = false,
                                        tarotContinueAck = false,
                                        numberRevealed = false,
                                        tarotMainId = null,
                                        tarotMainResolved = false,
                                        selectedMoodId = null,
                                        checkInSubmitted = false,
                                        guideNarrativeLoading = false,
                                    ),
                                )
                            },
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Начать день заново")
                        }
                    }
                }
            }
            else -> Text(error ?: "Нет данных", color = MaterialTheme.colorScheme.error)
        }
    }
}

@Composable
private fun CompositionFoundationBlock(contract: TodayContractV1) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(contract.themeHeadline(), style = MaterialTheme.typography.titleLarge)
        contract.dayStory?.direction?.takeIf { it.isNotBlank() }?.let {
            Text(it, style = MaterialTheme.typography.bodyMedium)
        }
        contract.dayStory?.story?.takeIf { it.isNotBlank() }?.let {
            Text(it, style = MaterialTheme.typography.bodyLarge)
        }
        Text("Главный шаг", style = MaterialTheme.typography.titleSmall)
        Text(
            contract.dayStory?.todayMove?.takeIf { it.isNotBlank() } ?: contract.primaryAction,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
private fun RitualGateCard(title: String, body: String) {
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(title, style = MaterialTheme.typography.titleMedium)
        Text(body, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun PersonalizedDayBlock(contract: TodayContractV1, moodId: String?) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Твой день", style = MaterialTheme.typography.titleLarge)
        moodId?.let {
            val label = ritualMoods.firstOrNull { m -> m.first == it }?.second ?: it
            Text("Настроение: $label", style = MaterialTheme.typography.bodySmall)
        }
        contract.dayStory?.story?.takeIf { it.isNotBlank() }?.let {
            Text(it, style = MaterialTheme.typography.bodyLarge)
        }
        contract.dayStory?.do?.takeIf { it.isNotEmpty() }?.let { items ->
            Text("Усилить", style = MaterialTheme.typography.titleSmall)
            items.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium) }
        }
        contract.dayStory?.avoid?.takeIf { it.isNotEmpty() }?.let { items ->
            Text("Не дожимать", style = MaterialTheme.typography.titleSmall)
            items.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium) }
        }
        Text("Отношения", style = MaterialTheme.typography.titleSmall)
        Text(contract.domains.relationships.action, style = MaterialTheme.typography.bodyMedium)
        Text("Работа и деньги", style = MaterialTheme.typography.titleSmall)
        Text(contract.domains.moneyWork.action, style = MaterialTheme.typography.bodyMedium)
        Text("Семья", style = MaterialTheme.typography.titleSmall)
        Text(contract.domains.family.action, style = MaterialTheme.typography.bodyMedium)
    }
}

private fun deterministicTarotId(dateISO: String): Int =
    (dateISO.hashCode().and(0x7fffffff) % 78) + 1

private fun deterministicPersonalDay(dateISO: String): Int {
    val digits = dateISO.filter { it.isDigit() }.map { it.digitToInt() }
    if (digits.isEmpty()) return 1
    var sum = digits.sum()
    while (sum > 9) {
        sum = sum.toString().map { it.digitToInt() }.sum()
    }
    return sum.coerceAtLeast(1)
}
