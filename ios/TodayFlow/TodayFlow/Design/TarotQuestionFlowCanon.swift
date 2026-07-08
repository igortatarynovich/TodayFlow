import Foundation

// MARK: - Types (mirror `frontend/src/lib/tarotQuestionFlowCanon.ts`)

enum TarotConcernDomain: String, Codable, CaseIterable, Hashable {
    case relationships
    case work
    case money
    case family
    case growth
    case decision
    case conflict
    case innerState = "inner_state"
    case other
}

enum TarotFlowStep: String, Codable {
    case hero
    case concern
    case refine
    case spread
}

struct TarotConcernOption: Identifiable, Hashable {
    let id: TarotConcernDomain
    let emoji: String
    let label: String
    let hint: String
}

struct TarotRefinementOption: Identifiable, Hashable {
    let id: String
    let label: String
    let questionSeed: String
}

struct TarotSpreadOffer: Identifiable, Hashable {
    var id: String { spreadId }
    let spreadId: String
    let title: String
    let subtitle: String
    let answersQuestions: String
    let cardCount: Int
    let positionLabels: [String]
    let recommendedFor: [TarotConcernDomain]
}

enum TarotQuestionFlowCopy {
    static var heroTitle: String { "У каждого вопроса есть несколько сторон" }
    static var heroBody: String {
        "Иногда достаточно посмотреть на ситуацию под другим углом. Карты помогают увидеть то, что легко упустить, когда эмоции слишком сильны."
    }
    static var heroCta: String { "Разобраться с тем, что волнует" }
    static var heroSecondary: String { "Карта дня" }
    static var concernStep: String { "Шаг 1 из 3" }
    static var concernTitle: String { "Что сейчас занимает твои мысли?" }
    static var concernBody: String { "Выбери близкую тему — или сформулируй свой вопрос ниже." }
    static var concernCustomLabel: String { "Написать свой вопрос" }
    static var concernCustomPlaceholder: String { "Например: стоит ли менять работу?" }
    static var refineStep: String { "Шаг 2 из 3" }
    static var refineTitle: String { "Сегодня тебя больше волнует…" }
    static var spreadStep: String { "Шаг 3 из 3" }
    static var spreadTitle: String { "Какой взгляд нужен сейчас?" }
    static var spreadBody: String { "Каждый расклад отвечает на свои вопросы — не про количество карт." }
    static var back: String { "Назад" }
    static var `continue`: String { "Дальше" }
    static var skipRefine: String { "Пропустить уточнение" }
    static var beginRitual: String { "К ритуалу →" }
    static var composedQuestionLabel: String { "Твой вопрос" }
}

enum TarotQuestionFlowCanon {
    static let concernOptions: [TarotConcernOption] = [
        .init(id: .relationships, emoji: "❤️", label: "Отношения", hint: "Близость, пара, чувства"),
        .init(id: .work, emoji: "💼", label: "Работа", hint: "Карьера, роль, направление"),
        .init(id: .money, emoji: "💰", label: "Деньги", hint: "Ресурс, решения, стабильность"),
        .init(id: .family, emoji: "🏡", label: "Семья", hint: "Родные, дом, границы"),
        .init(id: .growth, emoji: "🌱", label: "Саморазвитие", hint: "Рост, смысл, путь"),
        .init(id: .decision, emoji: "🧭", label: "Важное решение", hint: "Выбор, развилка"),
        .init(id: .conflict, emoji: "⚡", label: "Конфликт", hint: "Напряжение, спор, застревание"),
        .init(id: .innerState, emoji: "🕊", label: "Внутреннее состояние", hint: "Настроение, опора, усталость"),
        .init(id: .other, emoji: "✨", label: "Другое", hint: "Своя формулировка"),
    ]

    static let refinements: [TarotConcernDomain: [TarotRefinementOption]] = [
        .relationships: [
            .init(id: "specific_person", label: "Конкретный человек", questionSeed: "Что сейчас важно понять в отношениях с этим человеком?"),
            .init(id: "relationships_general", label: "Отношения вообще", questionSeed: "Какой новый взгляд поможет мне в теме близости прямо сейчас?"),
            .init(id: "ex_partner", label: "Бывший партнёр", questionSeed: "Что мне важно увидеть в истории с бывшим партнёром?"),
            .init(id: "new_person", label: "Новый человек", questionSeed: "Как лучше понять то, что происходит с новым человеком?"),
            .init(id: "two_people", label: "Выбор между двумя людьми", questionSeed: "Какой взгляд поможет мне честнее увидеть выбор между двумя людьми?"),
        ],
        .work: [
            .init(id: "stay_or_leave", label: "Остаться или уйти", questionSeed: "Стоит ли менять работу — или сначала что-то прояснить здесь?"),
            .init(id: "direction", label: "Куда двигаться", questionSeed: "Какое направление в работе сейчас заслуживает внимания?"),
            .init(id: "team_conflict", label: "Конфликт на работе", questionSeed: "Как лучше пройти текущее напряжение на работе?"),
            .init(id: "burnout", label: "Усталость и выгорание", questionSeed: "Что поможет вернуть ясность, когда работа выматывает?"),
        ],
        .money: [
            .init(id: "big_purchase", label: "Крупная трата или вложение", questionSeed: "Какой взгляд поможет принять решение о деньгах спокойнее?"),
            .init(id: "stability", label: "Стабильность и страх", questionSeed: "Где сейчас реальная опора в теме денег, а где тревога?"),
            .init(id: "income_change", label: "Изменить доход", questionSeed: "Что важно учесть, если я хочу изменить свой доход?"),
        ],
        .family: [
            .init(id: "parent", label: "Родитель или старшие", questionSeed: "Что сейчас важно понять в отношениях с родителями или старшими?"),
            .init(id: "child", label: "Ребёнок", questionSeed: "Какой взгляд поможет мне быть ближе к ребёнку без давления?"),
            .init(id: "home", label: "Дом и быт", questionSeed: "Что дома требует честного взгляда прямо сейчас?"),
            .init(id: "boundaries", label: "Границы в семье", questionSeed: "Где в семье мне нужны более ясные границы?"),
        ],
        .growth: [
            .init(id: "direction", label: "Куда расти", questionSeed: "Какой следующий шаг в саморазвитии сейчас уместен?"),
            .init(id: "block", label: "Что мешает", questionSeed: "Что мешает мне двигаться вперёд в росте?"),
            .init(id: "purpose", label: "Смысл и предназначение", questionSeed: "Какой новый угол поможет увидеть свой путь яснее?"),
        ],
        .decision: [
            .init(id: "two_options", label: "Два варианта", questionSeed: "Как честнее сравнить два варианта, между которыми я выбираю?"),
            .init(id: "timing", label: "Срок и момент", questionSeed: "Сейчас время действовать — или лучше дать ситуации день?"),
            .init(id: "fear", label: "Страх ошибиться", questionSeed: "Что я боюсь потерять, откладывая это решение?"),
        ],
        .conflict: [
            .init(id: "with_person", label: "Конфликт с человеком", questionSeed: "Как лучше увидеть конфликт с этим человеком?"),
            .init(id: "inner", label: "Внутренний конфликт", questionSeed: "Какие части меня сейчас тянут в разные стороны?"),
            .init(id: "stuck", label: "Застрял и не могу сдвинуться", questionSeed: "Что поможет выйти из застревания без резких шагов?"),
        ],
        .innerState: [
            .init(id: "anxiety", label: "Тревога", questionSeed: "Что сейчас питает мою тревогу — и что может её смягчить?"),
            .init(id: "emptiness", label: "Пустота или апатия", questionSeed: "Что поможет вернуть контакт с собой, когда внутри пусто?"),
            .init(id: "overwhelm", label: "Перегруз", questionSeed: "Какой один взгляд поможет при перегрузе?"),
            .init(id: "need_rest", label: "Нужен покой", questionSeed: "Что сейчас действительно восстановит, а не отвлечёт?"),
        ],
        .other: [
            .init(id: "custom", label: "Сформулирую сам", questionSeed: ""),
        ],
    ]

    static let spreadOffers: [TarotSpreadOffer] = [
        .init(spreadId: "one_card", title: "Одна карта", subtitle: "Быстрый взгляд",
              answersQuestions: "Когда нужен один честный фокус — без длинного разбора.",
              cardCount: 1, positionLabels: ["Фокус"],
              recommendedFor: [.innerState, .other, .decision]),
        .init(spreadId: "three_cards", title: "Три карты", subtitle: "Линия ситуации",
              answersQuestions: "Что привело сюда, что происходит сейчас и куда может пойти следующий шаг.",
              cardCount: 3, positionLabels: ["Прошлое", "Настоящее", "Следующий шаг"],
              recommendedFor: [.relationships, .work, .decision, .conflict, .other]),
        .init(spreadId: "guidance_relationship_five", title: "Любовный", subtitle: "Пять карт",
              answersQuestions: "Что ты чувствуешь, что между вами, где риск и что лучше сделать.",
              cardCount: 5, positionLabels: ["Ты", "Другой", "Между вами", "Риск", "Шаг"],
              recommendedFor: [.relationships]),
        .init(spreadId: "guidance_choice_two", title: "Решение", subtitle: "Шесть карт",
              answersQuestions: "Сравнение двух путей: что даёт каждый, где риск и лучший следующий шаг.",
              cardCount: 6, positionLabels: ["A — даёт", "A — риск", "B — даёт", "B — риск", "Важно", "Шаг"],
              recommendedFor: [.decision, .work, .money]),
        .init(spreadId: "guidance_work_money", title: "Деньги", subtitle: "Пять карт",
              answersQuestions: "Где реальность, где страх, что сработает и какой практический шаг на этой неделе.",
              cardCount: 5, positionLabels: ["Реальность", "Страх", "Сработает", "Риск", "Шаг"],
              recommendedFor: [.money, .work]),
        .init(spreadId: "guidance_inner_conflict", title: "Конфликт", subtitle: "Пять карт",
              answersQuestions: "Чего ты хочешь, чего боишься, что подавляешь и как выйти из застревания.",
              cardCount: 5, positionLabels: ["Хочешь", "Боишься", "Подавляешь", "Если не менять", "Выход"],
              recommendedFor: [.conflict, .innerState]),
        .init(spreadId: "alignment_cross", title: "Внутреннее состояние", subtitle: "Четыре карты",
              answersQuestions: "Как сейчас связаны ум, сердце, тело и что из этого — действие.",
              cardCount: 4, positionLabels: ["Ум", "Сердце", "Тело", "Интеграция"],
              recommendedFor: [.innerState, .growth]),
        .init(spreadId: "guidance_deep_eight", title: "Предназначение", subtitle: "Полное исследование",
              answersQuestions: "Суть, роли, скрытое, риск, возможность, совет и первый реальный шаг.",
              cardCount: 8, positionLabels: ["Суть", "Твоя роль", "Другой фактор", "Скрытое", "Риск", "Шанс", "Совет", "Шаг"],
              recommendedFor: [.growth, .decision, .other]),
    ]

    static func spreadOffer(for spreadId: String) -> TarotSpreadOffer? {
        spreadOffers.first { $0.spreadId == spreadId }
    }

    static func rankSpreadOffers(for domain: TarotConcernDomain?) -> [TarotSpreadOffer] {
        guard let domain else { return spreadOffers }
        return spreadOffers
            .map { offer -> (TarotSpreadOffer, Int) in
                var score = 0
                if offer.recommendedFor.contains(domain) { score += 1 }
                if offer.spreadId != "one_card", offer.spreadId != "three_cards" { score += 1 }
                return (offer, score)
            }
            .sorted { $0.1 > $1.1 }
            .map(\.0)
    }

    static func composeQuestion(
        concernDomain: TarotConcernDomain?,
        refinementId: String?,
        customQuestion: String
    ) -> String {
        let custom = customQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
        if !custom.isEmpty { return custom }
        guard let domain = concernDomain else {
            return "Какой новый взгляд поможет мне сейчас?"
        }
        if let picked = refinements[domain]?.first(where: { $0.id == refinementId }),
           !picked.questionSeed.isEmpty {
            return picked.questionSeed
        }
        if let concern = concernOptions.first(where: { $0.id == domain }) {
            return "Какой новый взгляд поможет мне в теме «\(concern.label.lowercased())» прямо сейчас?"
        }
        return "Какой новый взгляд поможет мне сейчас?"
    }

    static func flowEventKey(sessionId: String, suffix: String) -> String {
        "tarot-flow:\(sessionId):\(suffix)"
    }
}
