import SwiftUI

enum InterpretationResonance: String, CaseIterable, Identifiable {
    case yes
    case partial
    case no

    var id: String { rawValue }

    var label: String {
        switch self {
        case .yes: return "Да"
        case .partial: return "Частично"
        case .no: return "Нет"
        }
    }
}

enum ProximityChoiceId: String, CaseIterable, Identifiable {
    case wait
    case seeDifferently = "see_differently"
    case firstStep = "first_step"
    case unsure
    case pause
    case move
    case both
    case clarity
    case patience

    var id: String { rawValue }
}

enum InterpretationConfirmTarget: String {
    case tarotImpact = "tarot_impact"
    case numberImpact = "number_impact"
    case dayPulse = "day_pulse"
}

struct InterpretationProximityOption: Identifiable {
    let choiceId: ProximityChoiceId
    let resonance: InterpretationResonance
    let label: String

    var id: String { choiceId.rawValue }
}

enum PimInterpretationConfirmCopy {
    static func proximityQuestion(for _: InterpretationConfirmTarget) -> String {
        "Что сейчас ближе?"
    }

    static func proximityOptions(for target: InterpretationConfirmTarget) -> [InterpretationProximityOption] {
        switch target {
        case .tarotImpact:
            return [
                InterpretationProximityOption(choiceId: .wait, resonance: .partial, label: "Подождать"),
                InterpretationProximityOption(choiceId: .seeDifferently, resonance: .yes, label: "Посмотреть иначе"),
                InterpretationProximityOption(choiceId: .firstStep, resonance: .yes, label: "Сделать первый шаг"),
                InterpretationProximityOption(choiceId: .unsure, resonance: .no, label: "Пока не понимаю"),
            ]
        case .numberImpact:
            return [
                InterpretationProximityOption(choiceId: .wait, resonance: .partial, label: "Дать дню время"),
                InterpretationProximityOption(choiceId: .seeDifferently, resonance: .yes, label: "Замечаю закономерность"),
                InterpretationProximityOption(choiceId: .firstStep, resonance: .yes, label: "Готов действовать"),
                InterpretationProximityOption(choiceId: .unsure, resonance: .no, label: "Пока не понимаю"),
            ]
        case .dayPulse:
            return [
                InterpretationProximityOption(choiceId: .pause, resonance: .partial, label: "Скорее про паузу"),
                InterpretationProximityOption(choiceId: .move, resonance: .yes, label: "Скорее про движение"),
                InterpretationProximityOption(choiceId: .both, resonance: .partial, label: "И то, и другое"),
                InterpretationProximityOption(choiceId: .unsure, resonance: .no, label: "Пока не ясно"),
            ]
        }
    }

    static func correction(for resonance: InterpretationResonance) -> String {
        switch resonance {
        case .yes: return "confirm"
        case .partial: return "partial"
        case .no: return "reject"
        }
    }
}

struct PimInterpretationConfirmView: View {
    let target: InterpretationConfirmTarget
    let selectedChoiceId: ProximityChoiceId?
    let onSelect: (ProximityChoiceId, InterpretationResonance) -> Void

    private var options: [InterpretationProximityOption] {
        PimInterpretationConfirmCopy.proximityOptions(for: target)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(PimInterpretationConfirmCopy.proximityQuestion(for: target))
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 8)], spacing: 8) {
                ForEach(options) { option in
                    Button {
                        onSelect(option.choiceId, option.resonance)
                    } label: {
                        Text(option.label)
                            .font(.caption.weight(.medium))
                            .multilineTextAlignment(.center)
                            .fixedSize(horizontal: false, vertical: true)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 8)
                            .frame(maxWidth: .infinity)
                            .background(
                                selectedChoiceId == option.choiceId
                                    ? TodayFlowTheme.sunset.opacity(0.22)
                                    : Color.white.opacity(0.55)
                            )
                            .clipShape(Capsule())
                    }
                    .buttonStyle(.plain)
                    .disabled(selectedChoiceId != nil && selectedChoiceId != option.choiceId)
                }
            }
        }
        .accessibilityElement(children: .contain)
    }
}

enum PimKnowledgeVerdictStore {
    private static let prefix = "todayflow.profile_atom_verdict.v1"

    static func readVerdicts() -> [String: String] {
        guard let data = UserDefaults.standard.data(forKey: prefix),
              let decoded = try? JSONDecoder().decode([String: String].self, from: data) else {
            return [:]
        }
        return decoded
    }

    static func writeVerdict(knowledgeID: String, resonance: InterpretationResonance) {
        var next = readVerdicts()
        next[knowledgeID] = resonance.rawValue
        if let data = try? JSONEncoder().encode(next) {
            UserDefaults.standard.set(data, forKey: prefix)
        }
    }

    static func hasVerdict(knowledgeID: String) -> Bool {
        readVerdicts()[knowledgeID] != nil
    }
}
