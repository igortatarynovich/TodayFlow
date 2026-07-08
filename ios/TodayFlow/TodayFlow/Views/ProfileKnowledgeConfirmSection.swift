import SwiftUI

/// Profile ILR v0 — confirm or reject knowledge atoms from CUM (web `ProfileKnowledgeConfirmBlock`).
struct ProfileKnowledgeConfirmSection: View {
    let store: TodayFlowStore

    @State private var model: CompactUserModelResponse?
    @State private var verdicts: [String: String] = [:]

    private var pendingAtoms: [CompactUserModelKnowledgeAtom] {
        let rows = model?.knowledgeAtomsTopK ?? []
        return rows
            .filter { atom in
                guard let id = atom.knowledgeID else { return false }
                return verdicts[id] == nil && !PimKnowledgeVerdictStore.hasVerdict(knowledgeID: id)
            }
            .filter { atom in
                let label = atom.claimSummary?.trimmingCharacters(in: .whitespacesAndNewlines) ?? atom.claim ?? ""
                return !label.isEmpty
            }
            .prefix(3)
            .map { $0 }
    }

    var body: some View {
        Group {
            if !pendingAtoms.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Про тебя")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text("Это похоже на правду?")
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)

                    ForEach(pendingAtoms) { atom in
                        atomCard(atom)
                    }
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.66))
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
            }
        }
        .task {
            verdicts = PimKnowledgeVerdictStore.readVerdicts()
            model = try? await store.loadCompactUserModel(force: true)
        }
    }

    @ViewBuilder
    private func atomCard(_ atom: CompactUserModelKnowledgeAtom) -> some View {
        let id = atom.knowledgeID ?? atom.id
        let label = atom.claimSummary?.trimmingCharacters(in: .whitespacesAndNewlines)
            ?? atom.claim
            ?? id

        VStack(alignment: .leading, spacing: 8) {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)

            LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 8)], spacing: 8) {
                ForEach(InterpretationResonance.allCases) { option in
                    Button {
                        submitVerdict(knowledgeID: id, claimSummary: atom.claimSummary, resonance: option)
                    } label: {
                        Text(option.label)
                            .font(.caption.weight(.medium))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 8)
                            .frame(maxWidth: .infinity)
                            .background(
                                option == .yes
                                    ? TodayFlowTheme.sunset.opacity(0.22)
                                    : Color.white.opacity(0.55)
                            )
                            .clipShape(Capsule())
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding(12)
        .background(Color.white.opacity(0.55))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func submitVerdict(
        knowledgeID: String,
        claimSummary: String?,
        resonance: InterpretationResonance
    ) {
        PimKnowledgeVerdictStore.writeVerdict(knowledgeID: knowledgeID, resonance: resonance)
        verdicts[knowledgeID] = resonance.rawValue
        Task {
            await store.trackMeaningEventWithIdempotency(
                eventType: "profile_atom_correction",
                eventSource: "profile",
                idempotencyKey: "profile_atom_correction:\(knowledgeID):\(resonance.rawValue)",
                qualityScore: 0.9,
                payload: [
                    "knowledge_id": .string(knowledgeID),
                    "correction": .string(PimInterpretationConfirmCopy.correction(for: resonance)),
                    "claim_summary": .string(claimSummary ?? ""),
                    "surface": .string("profile_quick_map"),
                ]
            )
            _ = try? await store.loadCompactUserModel(force: true)
        }
    }
}
