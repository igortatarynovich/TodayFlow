import SwiftUI

/// Question-first Tarot funnel — mirror web `TarotQuestionFlow.tsx`.
struct TarotQuestionFlowView: View {
    let store: TodayFlowStore
    var onBeginRitual: (TarotSpreadRitualConfig) -> Void
    var onOpenDailyCard: (() -> Void)?

    @State private var session: TarotQuestionSession?
    @State private var customQuestion = ""
    @State private var selectedSpreadId: String?

    private var step: TarotFlowStep { session?.step ?? .hero }

    private var composedQuestion: String {
        TarotQuestionFlowCanon.composeQuestion(
            concernDomain: session?.concernDomain,
            refinementId: session?.refinementId,
            customQuestion: customQuestion
        )
    }

    private var spreadOffers: [TarotSpreadOffer] {
        TarotQuestionFlowCanon.rankSpreadOffers(for: session?.concernDomain)
    }

    var body: some View {
        Group {
            if session != nil {
                VStack(alignment: .leading, spacing: 20) {
                    switch step {
                    case .hero:
                        heroStep
                    case .concern:
                        concernStep
                    case .refine:
                        refineStep
                    case .spread:
                        spreadStep
                    }
                }
                .padding(.vertical, 8)
            } else {
                ProgressView()
                    .frame(maxWidth: .infinity, minHeight: 120)
            }
        }
        .onAppear {
            bootstrapSession()
        }
    }

    // MARK: - Steps

    private var heroStep: some View {
        VStack(alignment: .leading, spacing: 16) {
            tarotFlowPanel {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Таро · новый взгляд")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color(red: 0.78, green: 0.72, blue: 0.62))
                        .textCase(.uppercase)
                        .kerning(1.2)
                    Text(TarotQuestionFlowCopy.heroTitle)
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(Color(red: 0.96, green: 0.94, blue: 0.91))
                        .fixedSize(horizontal: false, vertical: true)
                    Text(TarotQuestionFlowCopy.heroBody)
                        .font(.subheadline)
                        .foregroundStyle(Color(red: 0.82, green: 0.78, blue: 0.72))
                        .lineSpacing(4)
                }
            }

            Button {
                trackFlow("tarot_session_started", payload: ["surface": .string("tarot_hub")], suffix: "started")
                goToStep(.concern)
            } label: {
                Text(TarotQuestionFlowCopy.heroCta)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color(red: 0.92, green: 0.86, blue: 0.74))

            if let onOpenDailyCard {
                Button(action: onOpenDailyCard) {
                    Text("\(TarotQuestionFlowCopy.heroSecondary) →")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(Color(red: 0.78, green: 0.72, blue: 0.62))
                }
                .buttonStyle(.plain)
                .frame(maxWidth: .infinity)
            }
        }
    }

    private var concernStep: some View {
        VStack(alignment: .leading, spacing: 14) {
            stepHeader(
                eyebrow: TarotQuestionFlowCopy.concernStep,
                title: TarotQuestionFlowCopy.concernTitle,
                body: TarotQuestionFlowCopy.concernBody
            )

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                ForEach(TarotQuestionFlowCanon.concernOptions) { option in
                    Button {
                        handleConcernSelect(option.id)
                    } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("\(option.emoji) \(option.label)")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(Color(red: 0.94, green: 0.91, blue: 0.86))
                            Text(option.hint)
                                .font(.caption)
                                .foregroundStyle(Color(red: 0.72, green: 0.68, blue: 0.62))
                                .multilineTextAlignment(.leading)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(session?.concernDomain == option.id
                                    ? Color.white.opacity(0.12)
                                    : Color.white.opacity(0.05))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(Color.white.opacity(0.1), lineWidth: 1)
                        )
                    }
                    .buttonStyle(.plain)
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Text(TarotQuestionFlowCopy.concernCustomLabel)
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(Color(red: 0.78, green: 0.72, blue: 0.62))
                TextField(TarotQuestionFlowCopy.concernCustomPlaceholder, text: $customQuestion, axis: .vertical)
                    .textFieldStyle(.plain)
                    .padding(12)
                    .background(Color.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 12))
                    .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
            }

            flowNavRow(
                back: { goToStep(.hero) },
                forwardTitle: TarotQuestionFlowCopy.continue,
                forwardEnabled: session?.concernDomain != nil || !customQuestion.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                forward: handleContinueFromConcern
            )
        }
    }

    private var refineStep: some View {
        let refinements: [TarotRefinementOption] = {
            guard let domain = session?.concernDomain, domain != .other else { return [] }
            return TarotQuestionFlowCanon.refinements[domain] ?? []
        }()

        return VStack(alignment: .leading, spacing: 14) {
            stepHeader(
                eyebrow: TarotQuestionFlowCopy.refineStep,
                title: TarotQuestionFlowCopy.refineTitle,
                body: nil
            )

            ForEach(refinements) { option in
                Button {
                    handleRefineSelect(option.id)
                } label: {
                    Text(option.label)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(14)
                        .background(Color.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 14))
                }
                .buttonStyle(.plain)
            }

            flowNavRow(
                back: { goToStep(.concern) },
                forwardTitle: TarotQuestionFlowCopy.skipRefine,
                forwardEnabled: true,
                forward: { goToStep(.spread) }
            )
        }
    }

    private var spreadStep: some View {
        VStack(alignment: .leading, spacing: 14) {
            stepHeader(
                eyebrow: TarotQuestionFlowCopy.spreadStep,
                title: TarotQuestionFlowCopy.spreadTitle,
                body: TarotQuestionFlowCopy.spreadBody
            )

            tarotFlowPanel {
                VStack(alignment: .leading, spacing: 6) {
                    Text(TarotQuestionFlowCopy.composedQuestionLabel)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color(red: 0.72, green: 0.68, blue: 0.62))
                    Text("«\(composedQuestion)»")
                        .font(.subheadline)
                        .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            ForEach(spreadOffers) { offer in
                Button {
                    handleSpreadPick(offer.spreadId)
                } label: {
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(offer.title)
                                .font(.headline)
                                .foregroundStyle(Color(red: 0.96, green: 0.94, blue: 0.91))
                            Spacer()
                            Text(offer.subtitle)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(Color(red: 0.72, green: 0.68, blue: 0.62))
                        }
                        Text(offer.answersQuestions)
                            .font(.subheadline)
                            .foregroundStyle(Color(red: 0.78, green: 0.74, blue: 0.68))
                            .multilineTextAlignment(.leading)
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(selectedSpreadId == offer.spreadId
                                ? Color.white.opacity(0.14)
                                : Color.white.opacity(0.06))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(
                                selectedSpreadId == offer.spreadId
                                    ? Color(red: 0.85, green: 0.72, blue: 0.45).opacity(0.55)
                                    : Color.white.opacity(0.08),
                                lineWidth: 1
                            )
                    )
                }
                .buttonStyle(.plain)
            }

            flowNavRow(
                back: {
                    if session?.concernDomain == .other || session?.concernDomain == nil {
                        goToStep(.concern)
                    } else {
                        goToStep(.refine)
                    }
                },
                forwardTitle: TarotQuestionFlowCopy.beginRitual,
                forwardEnabled: selectedSpreadId != nil,
                forward: handleBeginRitual
            )
        }
    }

    // MARK: - Actions

    private func bootstrapSession() {
        if let existing = TarotQuestionFlowSessionStore.read() {
            session = existing
            customQuestion = existing.customQuestion
            selectedSpreadId = existing.spreadId
            return
        }
        let fresh = TarotQuestionFlowSessionStore.create()
        TarotQuestionFlowSessionStore.write(fresh)
        session = fresh
    }

    private func writeSession(_ next: TarotQuestionSession) {
        TarotQuestionFlowSessionStore.write(next)
        session = next
    }

    private func goToStep(_ nextStep: TarotFlowStep, patch: (inout TarotQuestionSession) -> Void = { _ in }) {
        guard var current = session else { return }
        patch(&current)
        current.step = nextStep
        writeSession(current)
    }

    private func handleConcernSelect(_ domain: TarotConcernDomain) {
        trackFlow(
            "tarot_question_domain_selected",
            payload: ["concern_domain": .string(domain.rawValue)],
            suffix: "domain-\(domain.rawValue)"
        )
        guard var current = session else { return }
        current.concernDomain = domain
        current.refinementId = nil
        current.step = domain == .other ? .spread : .refine
        writeSession(current)
    }

    private func handleRefineSelect(_ refinementId: String) {
        trackFlow(
            "tarot_question_refined",
            payload: [
                "concern_domain": .string(session?.concernDomain?.rawValue ?? ""),
                "refinement_id": .string(refinementId),
            ],
            suffix: "refine-\(refinementId)"
        )
        goToStep(.spread) { $0.refinementId = refinementId }
    }

    private func handleContinueFromConcern() {
        let trimmed = customQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty {
            goToStep(session?.concernDomain == nil ? .spread : .refine) {
                $0.customQuestion = trimmed
                if $0.concernDomain == nil {
                    $0.concernDomain = .other
                }
            }
            customQuestion = trimmed
            return
        }
        if session?.concernDomain != nil {
            goToStep(.refine)
        }
    }

    private func handleSpreadPick(_ spreadId: String) {
        selectedSpreadId = spreadId
        trackFlow(
            "tarot_spread_selected",
            payload: [
                "spread_id": .string(spreadId),
                "concern_domain": .string(session?.concernDomain?.rawValue ?? ""),
                "question_text": .string(composedQuestion),
            ],
            suffix: "spread-\(spreadId)"
        )
        goToStep(.spread) { $0.spreadId = spreadId }
    }

    private func handleBeginRitual() {
        guard let current = session, let spreadId = selectedSpreadId,
              let offer = TarotQuestionFlowCanon.spreadOffer(for: spreadId) else { return }
        trackFlow(
            "tarot_question_submitted",
            payload: [
                "concern_domain": .string(current.concernDomain?.rawValue ?? ""),
                "refinement_id": .string(current.refinementId ?? ""),
                "question_text": .string(composedQuestion),
                "spread_id": .string(spreadId),
            ],
            suffix: "question-submitted"
        )
        let config = TarotSpreadRitualConfig(
            spreadId: spreadId,
            title: offer.title,
            question: composedQuestion,
            concernDomain: current.concernDomain?.rawValue,
            refinementId: current.refinementId,
            cardCount: offer.cardCount,
            positionLabels: offer.positionLabels,
            anchorCardId: nil,
            anchorOrientation: nil
        )
        onBeginRitual(config)
    }

    private func trackFlow(_ eventType: String, payload: [String: JSONValue], suffix: String) {
        guard let sessionId = session?.sessionId else { return }
        Task {
            await store.trackTarotFlowEvent(
                eventType: eventType,
                idempotencyKey: TarotQuestionFlowCanon.flowEventKey(sessionId: sessionId, suffix: suffix),
                payload: payload.merging(["session_id": .string(sessionId)]) { _, new in new }
            )
        }
    }

    // MARK: - UI helpers

    private func stepHeader(eyebrow: String, title: String, body: String?) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(eyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(Color(red: 0.72, green: 0.68, blue: 0.62))
            Text(title)
                .font(.title3.weight(.semibold))
                .foregroundStyle(Color(red: 0.96, green: 0.94, blue: 0.91))
            if let body {
                Text(body)
                    .font(.subheadline)
                    .foregroundStyle(Color(red: 0.78, green: 0.74, blue: 0.68))
            }
        }
    }

    private func flowNavRow(
        back: @escaping () -> Void,
        forwardTitle: String,
        forwardEnabled: Bool,
        forward: @escaping () -> Void
    ) -> some View {
        HStack(spacing: 10) {
            Button(TarotQuestionFlowCopy.back, action: back)
                .buttonStyle(.bordered)
                .tint(Color(red: 0.72, green: 0.68, blue: 0.62))
            Button(forwardTitle, action: forward)
                .buttonStyle(.borderedProminent)
                .tint(Color(red: 0.92, green: 0.86, blue: 0.74))
                .disabled(!forwardEnabled)
        }
        .padding(.top, 4)
    }

    private func tarotFlowPanel<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        content()
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(Color(red: 0.09, green: 0.10, blue: 0.14).opacity(0.92))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
    }
}
