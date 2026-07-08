import SwiftUI

private enum ProfileIlrInstanceStore {
    static let dismissPrefix = "todayflow.profile_ilr_instance.dismiss.v1"

    static func isDismissed(instanceID: String) -> Bool {
        UserDefaults.standard.string(forKey: "\(dismissPrefix).\(instanceID)") != nil
    }

    static func markDismissed(instanceID: String, resonance: InterpretationResonance) {
        UserDefaults.standard.set(resonance.rawValue, forKey: "\(dismissPrefix).\(instanceID)")
    }
}

struct ProfileInterpretationInstanceSection: View {
    let store: TodayFlowStore

    @State private var instances: [CompactUserModelInterpretationInstance] = []
    @State private var verdicts: [String: ProximityChoiceId] = [:]

    private var visible: [CompactUserModelInterpretationInstance] {
        instances.filter { row in
            guard let id = row.instanceID else { return false }
            if verdicts[id] != nil { return false }
            if ProfileIlrInstanceStore.isDismissed(instanceID: id) { return false }
            return true
        }
    }

    var body: some View {
        Group {
            if !visible.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Паттерны")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text("Это откликается?")
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)

                    ForEach(visible) { row in
                        if let id = row.instanceID {
                            instanceCard(row, id: id)
                        }
                    }
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.66))
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                .accessibilityIdentifier("profile_interpretation_instance_confirm")
            }
        }
        .task {
            guard let model = try? await store.loadCompactUserModel(force: true) else { return }
            instances = (model.interpretationInstancesTopK ?? [])
                .filter { row in
                    guard let ref = row.interpretationRefID, !ref.hasPrefix("beh.compat_") else { return false }
                    let summary = row.summary?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
                    return row.userVerdict == nil && row.instanceID != nil && !summary.isEmpty
                }
                .prefix(2)
                .map { $0 }
        }
    }

    @ViewBuilder
    private func instanceCard(_ row: CompactUserModelInterpretationInstance, id: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Наблюдение · не вывод")
                .font(.caption2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(row.summary ?? "")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            PimInterpretationConfirmView(
                target: .dayPulse,
                selectedChoiceId: verdicts[id],
                onSelect: { choiceId, resonance in
                    verdicts[id] = choiceId
                    ProfileIlrInstanceStore.markDismissed(instanceID: id, resonance: resonance)
                    let correction = PimInterpretationConfirmCopy.correction(for: resonance)
                    let dayKey = ISO8601DateFormatter().string(from: Date()).prefix(10)
                    Task {
                        await store.trackMeaningEventWithIdempotency(
                            eventType: "interpretation_instance_confirm",
                            eventSource: "profile",
                            idempotencyKey: "interpretation_instance_confirm:\(id):\(choiceId.rawValue):\(dayKey)",
                            qualityScore: 0.9,
                            payload: [
                                "surface": .string("profile_quick_map"),
                                "instance_id": .string(id),
                                "interpretation_ref_id": row.interpretationRefID.map { .string($0) } ?? .null,
                                "correction": .string(correction),
                                "verdict": .string(correction),
                                "proximity_choice": .string(choiceId.rawValue),
                                "summary": .string(row.summary ?? ""),
                            ]
                        )
                        _ = try? await store.loadCompactUserModel(force: true)
                    }
                }
            )
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.55))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}
