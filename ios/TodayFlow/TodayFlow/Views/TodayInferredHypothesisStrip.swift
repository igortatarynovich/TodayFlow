import SwiftUI

/// Today ILR v0 — one unconfirmed hypothesis from CUM after ritual (web `TodayInferredHypothesisStrip`).
struct TodayInferredHypothesisStrip: View {
    let store: TodayFlowStore
    let localDate: String
    let visible: Bool

    @State private var model: CompactUserModelResponse?
    @State private var selected: ProximityChoiceId?

    private var hypothesis: CompactUserModelKnowledgeAtom? {
        model?.knowledgeAtomsTopK.first { atom in
            atom.confirmationRequired == true
                && !(atom.claimSummary?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ?? true)
        }
    }

    private var dismissKey: String? {
        guard let id = hypothesis?.knowledgeID else { return nil }
        return "todayflow.inferred_hypothesis.dismiss.v1.\(id)"
    }

    var body: some View {
        Group {
            if visible, let hypothesis, let summary = hypothesis.claimSummary?.trimmingCharacters(in: .whitespacesAndNewlines), !summary.isEmpty {
                if dismissKey.map({ !UserDefaults.standard.bool(forKey: $0) }) ?? true {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Наблюдение · не факт")
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        Text(summary)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                        PimInterpretationConfirmView(
                            target: .dayPulse,
                            selectedChoiceId: selected,
                            onSelect: { choiceId, resonance in
                                selected = choiceId
                                if let key = dismissKey {
                                    UserDefaults.standard.set(true, forKey: key)
                                }
                                guard let kid = hypothesis.knowledgeID else { return }
                                Task {
                                    await store.trackMeaningEventWithIdempotency(
                                        eventType: "profile_atom_correction",
                                        eventSource: "today",
                                        idempotencyKey: "inferred_hypothesis:\(kid):\(choiceId.rawValue)",
                                        qualityScore: 0.88,
                                        payload: [
                                            "knowledge_id": .string(kid),
                                            "correction": .string(PimInterpretationConfirmCopy.correction(for: resonance)),
                                            "claim_summary": .string(summary),
                                            "surface": .string("today_inferred_hypothesis"),
                                            "inferred": .bool(true),
                                            "proximity_choice": .string(choiceId.rawValue),
                                        ]
                                    )
                                }
                            }
                        )
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.58))
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                }
            }
        }
        .task(id: visible) {
            guard visible else { return }
            model = try? await store.loadCompactUserModel(localDate: localDate, force: true)
        }
    }
}
