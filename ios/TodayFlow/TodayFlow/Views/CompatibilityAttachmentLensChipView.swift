import SwiftUI

struct CompatibilityAttachmentStyleHint: Codable, Hashable {
    let code: String
    let label: String
    let summary: String
    let evidenceBlocks: [String]?
    let confirmationRequired: Bool?

    enum CodingKeys: String, CodingKey {
        case code
        case label
        case summary
        case evidenceBlocks = "evidence_blocks"
        case confirmationRequired = "confirmation_required"
    }
}

struct CompatibilityAttachmentReference: Codable, Hashable {
    let attachmentStyleHints: [CompatibilityAttachmentStyleHint]?
    let referenceStatus: String?

    enum CodingKeys: String, CodingKey {
        case attachmentStyleHints = "attachment_style_hints"
        case referenceStatus = "reference_status"
    }

    var primaryHint: CompatibilityAttachmentStyleHint? {
        attachmentStyleHints?.first
    }
}

enum CompatibilityAttachmentLensStore {
    private static let dismissPrefix = "todayflow.compat_attachment_lens.dismiss.v1"

    static func dismissKey(for knowledgeID: String) -> String {
        "\(dismissPrefix).\(knowledgeID)"
    }

    static func isDismissed(knowledgeID: String) -> Bool {
        UserDefaults.standard.string(forKey: dismissKey(for: knowledgeID)) != nil
    }

    static func markDismissed(knowledgeID: String, resonance: InterpretationResonance) {
        UserDefaults.standard.set(resonance.rawValue, forKey: dismissKey(for: knowledgeID))
    }

    static func knowledgeID(for code: String) -> String {
        let slug = code.trimmingCharacters(in: .whitespacesAndNewlines).lowercased().replacingOccurrences(of: " ", with: "_")
        return "inf-attachment-lens-\(slug)"
    }
}

struct CompatibilityAttachmentLensChipView: View {
    let reference: CompatibilityAttachmentReference
    let surface: String
    let scenarioId: String?
    let store: TodayFlowStore

    @State private var selectedChoiceId: ProximityChoiceId?
    @State private var dismissed = false

    private var hint: CompatibilityAttachmentStyleHint? { reference.primaryHint }

    var body: some View {
        if let hint, !dismissed {
            let knowledgeID = CompatibilityAttachmentLensStore.knowledgeID(for: hint.code)
            if !CompatibilityAttachmentLensStore.isDismissed(knowledgeID: knowledgeID) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Возможный паттерн · не диагноз")
                        .font(.caption2.weight(.semibold))
                        .textCase(.uppercase)
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(hint.label)
                        .font(.subheadline.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(hint.summary)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                    PimInterpretationConfirmView(
                        target: .dayPulse,
                        selectedChoiceId: selectedChoiceId,
                        onSelect: { choiceId, resonance in
                            selectedChoiceId = choiceId
                            dismissed = true
                            CompatibilityAttachmentLensStore.markDismissed(knowledgeID: knowledgeID, resonance: resonance)
                            let dayKey = ISO8601DateFormatter().string(from: Date()).prefix(10)
                            Task {
                                await store.trackMeaningEventWithIdempotency(
                                    eventType: "compatibility_attachment_confirm",
                                    eventSource: "compatibility",
                                    idempotencyKey: "compat_attachment_confirm:\(hint.code):\(choiceId.rawValue):\(dayKey)",
                                    qualityScore: 0.9,
                                    payload: [
                                        "surface": .string(surface),
                                        "scenario_id": scenarioId.map { .string($0) } ?? .null,
                                        "attachment_style_code": .string(hint.code),
                                        "label": .string(hint.label),
                                        "summary": .string(hint.summary),
                                        "echo": .string(resonance.rawValue),
                                        "proximity_choice": .string(choiceId.rawValue),
                                        "verdict": .string(PimInterpretationConfirmCopy.correction(for: resonance)),
                                        "evidence_blocks": .array((hint.evidenceBlocks ?? []).map { .string($0) }),
                                        "knowledge_id": .string(knowledgeID),
                                        "reference_status": .string(reference.referenceStatus ?? "draft"),
                                    ]
                                )
                                await store.trackMeaningEventWithIdempotency(
                                    eventType: "profile_atom_correction",
                                    eventSource: "compatibility",
                                    idempotencyKey: "profile_atom_correction:\(knowledgeID):\(choiceId.rawValue)",
                                    qualityScore: 0.9,
                                    payload: [
                                        "knowledge_id": .string(knowledgeID),
                                        "correction": .string(PimInterpretationConfirmCopy.correction(for: resonance)),
                                        "claim_summary": .string(hint.summary),
                                        "surface": .string(surface),
                                        "attachment_style_code": .string(hint.code),
                                    ]
                                )
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
                .accessibilityIdentifier("compatibility_attachment_lens")
            }
        }
    }
}
