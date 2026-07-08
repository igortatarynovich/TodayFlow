package com.todayflow.today

/**
 * Конечный автомат хребта Today — зеркало iOS `TodayRitualStateMachine.swift` и веб `todayRitualSpineMachine.ts`.
 * Нативный экран «Сегодня» подключит reducer при реализации ритуала.
 */
data class RitualSpineSnapshot(
    val dayOpened: Boolean,
    val tarotContinueAck: Boolean,
    val numberRevealed: Boolean,
    val tarotMainId: Int?,
    val tarotMainResolved: Boolean,
    val selectedMoodId: String?,
    val checkInSubmitted: Boolean,
    val guideNarrativeLoading: Boolean,
) {
    fun isSpineComplete(): Boolean =
        tarotMainId != null &&
            tarotMainResolved &&
            tarotContinueAck &&
            numberRevealed &&
            selectedMoodId != null &&
            checkInSubmitted
}

sealed class RitualSpineUserEvent {
    data object OpenedDay : RitualSpineUserEvent()
    data object ContinuedPastTarot : RitualSpineUserEvent()
    data object RevealedNumber : RitualSpineUserEvent()
    data class SelectedMood(val moodId: String) : RitualSpineUserEvent()
    data object SubmittedCheckIn : RitualSpineUserEvent()
}

/** Паритет iOS `TodayRitualSpineAnalyticsHint` / веб `RitualSpineAnalyticsHint`. */
sealed class RitualSpineAnalyticsHint {
    data object None : RitualSpineAnalyticsHint()

    data object NumberRevealed : RitualSpineAnalyticsHint()

    data class MoodSelected(val moodId: String) : RitualSpineAnalyticsHint()
}

data class RitualSpineEffects(
    val saveOpenedDay: Boolean = false,
    val saveNumberRevealed: Boolean = false,
    val persistRitualExtras: Boolean = false,
    val resetNumberExtraSteps: Boolean = false,
    val scrollToAnchorId: String? = null,
    val scrollAfterNarrativeRefresh: String? = null,
    val analyticsHint: RitualSpineAnalyticsHint = RitualSpineAnalyticsHint.None,
)

object TodayRitualSpinePhaseResolver {
    fun phase(snapshot: RitualSpineSnapshot): String =
        when {
            !snapshot.dayOpened -> "not_started"
            snapshot.isSpineComplete() ->
                if (snapshot.guideNarrativeLoading) "day_ready_refreshing" else "day_ready"
            !snapshot.tarotContinueAck -> "tarot_interactive"
            !snapshot.numberRevealed -> "number_selecting"
            else -> "check_in"
        }

    fun consistencyIssues(s: RitualSpineSnapshot): List<String> {
        val issues = mutableListOf<String>()
        if (s.tarotContinueAck && !s.dayOpened) issues += "tarot_continue_without_opened_day"
        if (s.numberRevealed && !s.dayOpened) issues += "number_without_opened_day"
        if (s.checkInSubmitted && !s.numberRevealed) issues += "checkin_without_number"
        if (s.checkInSubmitted && s.selectedMoodId == null) issues += "checkin_without_mood"
        if (s.isSpineComplete() && !s.tarotMainResolved) issues += "spine_complete_without_resolved_tarot"
        return issues
    }
}

object TodayRitualSpineTransition {
    fun allows(event: RitualSpineUserEvent, before: RitualSpineSnapshot): Boolean {
        val phase = TodayRitualSpinePhaseResolver.phase(before)
        return when (event) {
            is RitualSpineUserEvent.OpenedDay ->
                phase == "not_started" && !before.dayOpened
            is RitualSpineUserEvent.ContinuedPastTarot ->
                phase == "tarot_interactive" && before.dayOpened && !before.tarotContinueAck
            is RitualSpineUserEvent.RevealedNumber ->
                phase == "number_selecting" && before.tarotContinueAck && !before.numberRevealed
            is RitualSpineUserEvent.SelectedMood ->
                before.numberRevealed && !before.checkInSubmitted
            is RitualSpineUserEvent.SubmittedCheckIn ->
                before.numberRevealed &&
                    !before.checkInSubmitted &&
                    before.selectedMoodId != null &&
                    before.tarotMainResolved
        }
    }
}

object TodayRitualSpineReducer {
    fun apply(event: RitualSpineUserEvent, before: RitualSpineSnapshot): Pair<RitualSpineSnapshot, RitualSpineEffects>? {
        if (!TodayRitualSpineTransition.allows(event, before)) return null
        val after =
            when (event) {
                is RitualSpineUserEvent.OpenedDay -> before.copy(dayOpened = true)
                is RitualSpineUserEvent.ContinuedPastTarot -> before.copy(tarotContinueAck = true)
                is RitualSpineUserEvent.RevealedNumber -> before.copy(numberRevealed = true)
                is RitualSpineUserEvent.SelectedMood -> before.copy(selectedMoodId = event.moodId)
                is RitualSpineUserEvent.SubmittedCheckIn -> before.copy(checkInSubmitted = true)
            }
        val effects =
            when (event) {
                is RitualSpineUserEvent.OpenedDay ->
                    RitualSpineEffects(saveOpenedDay = true, scrollToAnchorId = "ritualDeck")
                is RitualSpineUserEvent.ContinuedPastTarot ->
                    RitualSpineEffects(persistRitualExtras = true, scrollToAnchorId = "ritualNumber")
                is RitualSpineUserEvent.RevealedNumber ->
                    RitualSpineEffects(
                        saveNumberRevealed = true,
                        resetNumberExtraSteps = true,
                        scrollToAnchorId = "ritualCheckin",
                        analyticsHint = RitualSpineAnalyticsHint.NumberRevealed,
                    )
                is RitualSpineUserEvent.SelectedMood ->
                    RitualSpineEffects(
                        persistRitualExtras = true,
                        analyticsHint = RitualSpineAnalyticsHint.MoodSelected(event.moodId),
                    )
                is RitualSpineUserEvent.SubmittedCheckIn ->
                    RitualSpineEffects(
                        persistRitualExtras = true,
                        scrollAfterNarrativeRefresh = "ritualYourDay",
                    )
            }
        return after to effects
    }
}
