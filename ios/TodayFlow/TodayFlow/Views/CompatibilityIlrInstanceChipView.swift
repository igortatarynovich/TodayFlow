import SwiftUI

private enum CompatibilityIlrInstanceStore {
    static let dismissPrefix = "todayflow.compat_ilr_instance.dismiss.v1"

    static func isDismissed(instanceID: String) -> Bool {
        UserDefaults.standard.string(forKey: "\(dismissPrefix).\(instanceID)") != nil
    }

    static func markDismissed(instanceID: String, resonance: InterpretationResonance) {
        UserDefaults.standard.set(resonance.rawValue, forKey: "\(dismissPrefix).\(instanceID)")
    }
}

struct CompatibilityIlrInstanceChipView: View {
    let surface: String
    let scenarioId: String?
    let store: TodayFlowStore

    @State private var instance: CompactUserModelInterpretationInstance?
    @State private var selectedChoiceId: ProximityChoiceId?
    @State private var dismissed = false

    var body: some View {
        Group {
            if let instance, let instanceID = instance.instanceID, !dismissed, !CompatibilityIlrInstanceStore.isDismissed(instanceID: instanceID) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Паттерн из твоих откликов · не вывод")
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(instance.summary ?? "")
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                    PimInterpretationConfirmView(
                        target: .dayPulse,
                        selectedChoiceId: selectedChoiceId,
                        onSelect: { choiceId, resonance in
                            selectedChoiceId = choiceId
                            dismissed = true
                            CompatibilityIlrInstanceStore.markDismissed(instanceID: instanceID, resonance: resonance)
                            let correction = PimInterpretationConfirmCopy.correction(for: resonance)
                            let dayKey = ISO8601DateFormatter().string(from: Date()).prefix(10)
                            Task {
                                await store.trackMeaningEventWithIdempotency(
                                    eventType: "interpretation_instance_confirm",
                                    eventSource: "compatibility",
                                    idempotencyKey: "interpretation_instance_confirm:\(instanceID):\(choiceId.rawValue):\(dayKey)",
                                    qualityScore: 0.9,
                                    payload: [
                                        "surface": .string(surface),
                                        "scenario_id": scenarioId.map { .string($0) } ?? .null,
                                        "instance_id": .string(instanceID),
                                        "interpretation_ref_id": instance.interpretationRefID.map { .string($0) } ?? .null,
                                        "correction": .string(correction),
                                        "verdict": .string(correction),
                                        "proximity_choice": .string(choiceId.rawValue),
                                        "summary": .string(instance.summary ?? ""),
                                    ]
                                )
                                _ = try? await store.loadCompactUserModel(force: true)
                            }
                        }
                    )
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.72))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(TodayFlowTheme.gold.opacity(0.35), lineWidth: 1)
                )
                .accessibilityIdentifier("compatibility_ilr_instance")
            }
        }
        .task {
            guard instance == nil else { return }
            guard let model = try? await store.loadCompactUserModel(force: true) else { return }
            instance = model.interpretationInstancesTopK?.first(where: { row in
                guard let ref = row.interpretationRefID, ref.hasPrefix("beh.compat_") else { return false }
                let summary = row.summary?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
                return row.userVerdict == nil && !summary.isEmpty
            })
        }
    }
}
