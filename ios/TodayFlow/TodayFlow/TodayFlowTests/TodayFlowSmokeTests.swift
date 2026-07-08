import XCTest
@testable import TodayFlow

final class TodayFlowSmokeTests: XCTestCase {
    func testSmoke() {
        XCTAssertTrue(true)
    }

    func testTodayRitualSpinePhase_notStarted() {
        let s = TodayRitualSpineSnapshot(
            dayOpened: false,
            tarotContinueAck: false,
            numberRevealed: false,
            tarotMainId: nil,
            tarotMainResolved: false,
            selectedMoodId: nil,
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        XCTAssertEqual(TodayRitualSpinePhaseResolver.phase(for: s), .notStarted)
        XCTAssertTrue(TodayRitualSpineTransition.allows(.openedDay, snapshot: s))
        XCTAssertFalse(TodayRitualSpineTransition.allows(.continuedPastTarot, snapshot: s))
    }

    func testTodayRitualSpinePhase_dayReadyRefreshing() {
        let s = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: true,
            numberRevealed: true,
            tarotMainId: 1,
            tarotMainResolved: true,
            selectedMoodId: "tired",
            checkInSubmitted: true,
            guideNarrativeLoading: true
        )
        XCTAssertEqual(TodayRitualSpinePhaseResolver.phase(for: s), .dayReady(isNarrativeRefreshing: true))
        XCTAssertTrue(TodayRitualSpinePhaseResolver.consistencyIssues(s).isEmpty)
    }

    func testTodayRitualSpineConsistency_detectsBrokenCheckin() {
        let s = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: true,
            numberRevealed: false,
            tarotMainId: 1,
            tarotMainResolved: true,
            selectedMoodId: nil,
            checkInSubmitted: true,
            guideNarrativeLoading: false
        )
        XCTAssertTrue(TodayRitualSpinePhaseResolver.consistencyIssues(s).contains("checkin_without_number"))
    }

    func testTodayRitualSpineReducer_openedDay() {
        let before = TodayRitualSpineSnapshot(
            dayOpened: false,
            tarotContinueAck: false,
            numberRevealed: false,
            tarotMainId: nil,
            tarotMainResolved: false,
            selectedMoodId: nil,
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        guard let (after, effects) = TodayRitualSpineReducer.apply(event: .openedDay, to: before) else {
            XCTFail("expected reducer success")
            return
        }
        XCTAssertTrue(after.dayOpened)
        XCTAssertTrue(effects.saveOpenedDay)
        XCTAssertEqual(effects.scrollToAnchorId, "ritualDeck")
    }

    func testTodayRitualSpineReducer_rejectsDoubleOpen() {
        let before = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: false,
            numberRevealed: false,
            tarotMainId: nil,
            tarotMainResolved: false,
            selectedMoodId: nil,
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        XCTAssertNil(TodayRitualSpineReducer.apply(event: .openedDay, to: before))
    }

    func testTodayRitualSpineReducer_continuedPastTarot() {
        let before = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: false,
            numberRevealed: false,
            tarotMainId: 2,
            tarotMainResolved: true,
            selectedMoodId: nil,
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        guard let (after, effects) = TodayRitualSpineReducer.apply(event: .continuedPastTarot, to: before) else {
            XCTFail("expected success")
            return
        }
        XCTAssertTrue(after.tarotContinueAck)
        XCTAssertTrue(effects.persistRitualExtras)
        XCTAssertEqual(effects.scrollToAnchorId, "ritualNumber")
    }

    func testTodayRitualSpineReducer_revealedNumber() {
        let before = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: true,
            numberRevealed: false,
            tarotMainId: 2,
            tarotMainResolved: true,
            selectedMoodId: nil,
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        guard let (after, effects) = TodayRitualSpineReducer.apply(event: .revealedNumber, to: before) else {
            XCTFail("expected success")
            return
        }
        XCTAssertTrue(after.numberRevealed)
        XCTAssertTrue(effects.saveNumberRevealed)
        XCTAssertTrue(effects.resetNumberExtraSteps)
        XCTAssertEqual(effects.analyticsHint, .numberRevealed)
    }

    func testTodayRitualSpineReducer_selectedMood() {
        let before = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: true,
            numberRevealed: true,
            tarotMainId: 2,
            tarotMainResolved: true,
            selectedMoodId: nil,
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        guard let (after, effects) = TodayRitualSpineReducer.apply(event: .selectedMood("quiet_wish"), to: before) else {
            XCTFail("expected success")
            return
        }
        XCTAssertEqual(after.selectedMoodId, "quiet_wish")
        XCTAssertTrue(effects.persistRitualExtras)
        XCTAssertEqual(effects.analyticsHint, .moodSelected(moodId: "quiet_wish"))
    }

    func testTodayRitualSpineComplete_requiresTarotContinueAck() {
        let s = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: false,
            numberRevealed: true,
            tarotMainId: 1,
            tarotMainResolved: true,
            selectedMoodId: "tired",
            checkInSubmitted: true,
            guideNarrativeLoading: false
        )
        XCTAssertFalse(s.isSpineComplete)
        XCTAssertEqual(TodayRitualSpinePhaseResolver.phase(for: s), .tarotInteractive)
    }

    func testTodayRitualSpineReducer_submittedCheckIn() {
        let before = TodayRitualSpineSnapshot(
            dayOpened: true,
            tarotContinueAck: true,
            numberRevealed: true,
            tarotMainId: 2,
            tarotMainResolved: true,
            selectedMoodId: "tired",
            checkInSubmitted: false,
            guideNarrativeLoading: false
        )
        guard let (after, effects) = TodayRitualSpineReducer.apply(event: .submittedCheckIn, to: before) else {
            XCTFail("expected success")
            return
        }
        XCTAssertTrue(after.checkInSubmitted)
        XCTAssertEqual(effects.scrollAfterNarrativeRefresh, "ritualYourDay")
    }
}

