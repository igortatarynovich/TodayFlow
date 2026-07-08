import Foundation

/// RU/EN chrome для `TodayExperienceLayout` — дословное зеркало `TODAY_EXPERIENCE_CHROME_RU` / `TODAY_EXPERIENCE_CHROME_EN` в `todayRitualCopy.ts`.
enum TodayExperienceChromeCopy {
    private static var prefersRu: Bool { IOSAppLocale.prefersRussian }

    // MARK: - RU bundle (канон)

    private enum RU {
        static let todayEyebrow = "СЕГОДНЯ"
        static let of100 = "из 100"
        static let rhythmSummary = "сводный ритм дня"
        static let a11yRhythm = "Сводный ритм дня"
        static let whyDayFeels = "Почему день ощущается так"
        static let a11yWhyHint = "Краткий разбор и контекст дня"
        static let energy = "Энергия"
        static let balance = "Баланс"
        static let focus = "Фокус"
        static let heroFallback =
            "Собери день вокруг одного спокойного вектора — меньше распыления, больше ясности."
        static let dayHeadlineFallback = "День внимательного выбора"
        static let meaningToday = "Смысл сегодня"
        static let lookDeeper = "Смотреть глубже"
        static let lessonSubtitleFallback =
            "Сейчас важно не сделать больше, а сделать осознаннее. Один вектор лучше трёх планов."
        static let todayPrefix = "Сегодня: "
        static let cardOfDay = "Карта дня"
        static let tarotA11yFaceUp = "Раскрыта карта дня"
        static let tarotA11yBack = "Рубашка карты дня"
        static let tarotA11yFlip = "Дважды нажмите или коснитесь, чтобы перевернуть"
        static let deeper = "Глубже"
        static let firstMovePrefix = "Опорный ход: "
        static let cautionPrefix = "Осторожность: "
        static let todayDoPrefix = "Сегодня: "
        static let firstMoveFallback = "один честный шаг, без суеты"
        static let cautionFallback = "не наращивай шум и спешку"
        static let todayDoFallback = "зафиксируй смысл до обеда"
        static let fullGuidanceCta = "Полный расклад в Центре разборов"
        static let numberOfDay = "Число дня"
        static let luckyWindowPrefix = "Удачное окно · "
        static let colorDotPrefix = "Цвет · "
        static let stoneDotPrefix = "Камень · "
        static let elementDotPrefix = "Стихия · "
        static let ringsTitle = "Кольца выравнивания"
        static let ringsSubtitle =
            "Удерживай ясность — смотри, что просаживает кольцо, и куда вести день"
        static let practicesTitle = "Рекомендовано на сегодня"
        static let ringHintWater = "→ сильнее кольцо: эмоции +4"
        static let ringHintBody = "→ сильнее: собранность +4"
        static let ringHintMoney = "→ сильнее: ресурс +4"
        static let ringHintDefault = "→ сильнее: смысл +2"
        static let ritualAffirmation = "Аффирмация"
        static let ritualAscetic = "Аскеза дня"
        static let ritualPractice = "Практика"
        static let ritualJournal = "Записать"
        static let ritualRite = "Ритуал"
        static let ritualAsceticBody = "Без импульсивных трат"
        static let ritualPracticeBody = "Дыхание по Луне, 2 мин"
        static let ritualJournalBody = "Что ты боишься сказать вслух?"
        static let ritualRiteBody = "Серебро в контакте с кожей сегодня"
        static let microTitle = "Короткий вопрос дня"
        static let microPrompt = "Что больше всего забирает силы?"
        static let microReward = "Кольцо близости +3% — профиль глубже учитывает твой день"
        static let microOptions: [String] = [
            "Отношения", "Неопределённость", "Работа", "Деньги", "Перетаранивание в голове",
        ]
        static let ritualAffirmationFallback = "Я выбираю ясность важнее удобства"
        static let habitsTitle = "Сегодня: база"
        static let habitWater = "Вода"
        static let habitMove = "Движение"
        static let habitReflect = "Пауза"
        static let habitWork = "Глубокая работа"
        static let habitSpend = "Без эмоциональных трат"
        static let compatTitle = "Совместимость сегодня"
        static let compatBody =
            "Линия отношений может пульсировать сильнее — сравнить пары важно, пока внимание в теме"
        static let compatCta = "Совместимость"
        static let guidTitle = "Спросить то, что нельзя обсудить в чате"
        static let guidBody = "Сценарии: «вернётся ли», «уходить ли с работы», «почему снова стопор»"
        static let guidCta = "Разбор: вопрос"
        static let diaryTitle = "Пиши чувство, а не план"
        static let diaryBody =
            "Что ранит? Чем гордишься? Чего боишься признать? Это питает персонализацию."
        static let diaryCta = "Отметить в Flow"
        static let tomorrowTitle = "Завтра: окно ясности"
        static let tomorrowBody =
            "К после 8:00 откроется сильный слой намерения. Загляни — короткое планирование, без паники."
        static let tomorrowCta = "Напомнить (завтра в Today)"
        static let sheetWhyTitle = "Сегодня: почему так"
        static let sheetDone = "Готово"
        static let sheetNatal = "Натал"
        static let sheetMeaning = "Смысл"
        static let sheetMoon = "Луна (натал)"
        static let sheetMoonFallback = "считается с картой"
        static let sheetFirstMove = "Опорный ход"
        static let sheetFirstMoveFallback = "один устойчивый вектор"
        static let sheetRisk = "Риск дня"
        static let sheetBody = "Тело и сигналы"
        static let sheetBodyFallback = "собирай сигналы, не обещай лишнего"
        static let ringSheetTitle = "Разбор"
        static let ringSheetClose = "Закрыть"
        static let ringSheetHeadlinePrefix = "Кольцо: "
        static let ringSheetNowPrefix = "Сейчас "
        static let ringSheetScoreMid = " из 100. "
        static let ringSheetTailEmpty = "Сигналы копим ежедневными фиксациями."
        static let ringSheetTailFactorsPrefix = "Сильные факторы: "
        static let ringAskGuidance = "Спросить в разборе"
        static let ringLove = "близость"
        static let ringWealth = "ресурс"
        static let ringDiscipline = "собранность"
        static let ringEmotion = "эмоции"
        static let ringPurpose = "смысл"
        static let ringSelf = "опора в себе"
        static let gridLove = "Близость"
        static let gridWealth = "Ресурс"
        static let gridDiscipline = "Собранность"
        static let gridEmotion = "Эмоции"
        static let gridPurpose = "Смысл"
        static let gridSelf = "В себе"
        static let luckyPresets: [(String, String, String, String)] = [
            ("8:00–10:00", "Голубой", "Сапфир", "Воздух"),
            ("14:00–16:00", "Синий глубокий", "Лунный камень", "Вода"),
            ("19:00–21:00", "Индиго", "Аметист", "Свет"),
        ]
    }

    // MARK: - EN bundle

    private enum EN {
        static let todayEyebrow = "TODAY"
        static let of100 = "of 100"
        static let rhythmSummary = "blended day rhythm"
        static let a11yRhythm = "Blended day rhythm"
        static let whyDayFeels = "Why today feels like this"
        static let a11yWhyHint = "Short read on today’s context"
        static let energy = "Energy"
        static let balance = "Balance"
        static let focus = "Focus"
        static let heroFallback = "Anchor the day around one calm vector—less scatter, more clarity."
        static let dayHeadlineFallback = "A day of careful choices"
        static let meaningToday = "Today’s meaning"
        static let lookDeeper = "Go deeper"
        static let lessonSubtitleFallback =
            "What matters now is not doing more, but doing it with awareness. One vector beats three plans."
        static let todayPrefix = "Today: "
        static let cardOfDay = "Card of the day"
        static let tarotA11yFaceUp = "Daily card face up"
        static let tarotA11yBack = "Daily card back"
        static let tarotA11yFlip = "Double-tap to flip"
        static let deeper = "Deeper"
        static let firstMovePrefix = "Key move: "
        static let cautionPrefix = "Caution: "
        static let todayDoPrefix = "Today: "
        static let firstMoveFallback = "one honest step, no rush"
        static let cautionFallback = "don’t add noise or hurry"
        static let todayDoFallback = "lock in the meaning before noon"
        static let fullGuidanceCta = "Full reading in Guidance"
        static let numberOfDay = "Number of the day"
        static let luckyWindowPrefix = "Lucky window · "
        static let colorDotPrefix = "Color · "
        static let stoneDotPrefix = "Stone · "
        static let elementDotPrefix = "Element · "
        static let ringsTitle = "Alignment rings"
        static let ringsSubtitle = "Stay clear—see what drags a ring down and where to steer the day"
        static let practicesTitle = "Suggested for today"
        static let ringHintWater = "→ stronger: emotions +4"
        static let ringHintBody = "→ stronger: discipline +4"
        static let ringHintMoney = "→ stronger: resources +4"
        static let ringHintDefault = "→ stronger: meaning +2"
        static let ritualAffirmation = "Affirmation"
        static let ritualAscetic = "Daily ascetic"
        static let ritualPractice = "Practice"
        static let ritualJournal = "Journal"
        static let ritualRite = "Ritual"
        static let ritualAsceticBody = "No impulsive spending"
        static let ritualPracticeBody = "Moon breath, 2 min"
        static let ritualJournalBody = "What are you afraid to say out loud?"
        static let ritualRiteBody = "Silver touching skin today"
        static let microTitle = "Quick question"
        static let microPrompt = "What drains you most?"
        static let microReward = "Closeness ring +3%—your profile learns your day better"
        static let microOptions: [String] = ["Relationships", "Uncertainty", "Work", "Money", "Overthinking"]
        static let ritualAffirmationFallback = "I choose clarity over comfort"
        static let habitsTitle = "Today: basics"
        static let habitWater = "Water"
        static let habitMove = "Movement"
        static let habitReflect = "Pause"
        static let habitWork = "Deep work"
        static let habitSpend = "No emotional spending"
        static let compatTitle = "Compatibility today"
        static let compatBody =
            "Relationship energy may pulse louder—compare pairs while it’s on your mind"
        static let compatCta = "Compatibility"
        static let guidTitle = "Ask what’s hard to say in chat"
        static let guidBody = "Themes: “will they return”, “should I leave this job”, “why I’m stuck again”"
        static let guidCta = "Guidance: ask"
        static let diaryTitle = "Write feeling, not plans"
        static let diaryBody =
            "What hurts? What are you proud of? What’s hard to admit? This feeds personalization."
        static let diaryCta = "Log in Flow"
        static let tomorrowTitle = "Tomorrow: clarity window"
        static let tomorrowBody =
            "After ~8:00 a stronger intention layer opens—peek in for light planning, no panic."
        static let tomorrowCta = "Remind (tomorrow in Today)"
        static let sheetWhyTitle = "Today: why it feels this way"
        static let sheetDone = "Done"
        static let sheetNatal = "Natal"
        static let sheetMeaning = "Meaning"
        static let sheetMoon = "Moon (natal)"
        static let sheetMoonFallback = "from your chart"
        static let sheetFirstMove = "Key move"
        static let sheetFirstMoveFallback = "one steady vector"
        static let sheetRisk = "Day risk"
        static let sheetBody = "Body and signals"
        static let sheetBodyFallback = "gather signals, promise less"
        static let ringSheetTitle = "Read"
        static let ringSheetClose = "Close"
        static let ringSheetHeadlinePrefix = "Ring: "
        static let ringSheetNowPrefix = "Now "
        static let ringSheetScoreMid = " of 100. "
        static let ringSheetTailEmpty = "We build signals with daily check-ins."
        static let ringSheetTailFactorsPrefix = "Strong factors: "
        static let ringAskGuidance = "Ask in Guidance"
        static let ringLove = "closeness"
        static let ringWealth = "resources"
        static let ringDiscipline = "discipline"
        static let ringEmotion = "emotions"
        static let ringPurpose = "meaning"
        static let ringSelf = "self-trust"
        static let gridLove = "Closeness"
        static let gridWealth = "Resources"
        static let gridDiscipline = "Focus"
        static let gridEmotion = "Emotions"
        static let gridPurpose = "Meaning"
        static let gridSelf = "Inner"
        static let luckyPresets: [(String, String, String, String)] = [
            ("8:00–10:00", "Azure", "Sapphire", "Air"),
            ("14:00–16:00", "Deep blue", "Moonstone", "Water"),
            ("19:00–21:00", "Indigo", "Amethyst", "Light"),
        ]
    }

    // MARK: - Resolved strings

    static var todayEyebrow: String { prefersRu ? RU.todayEyebrow : EN.todayEyebrow }
    static var of100: String { prefersRu ? RU.of100 : EN.of100 }
    static var rhythmSummary: String { prefersRu ? RU.rhythmSummary : EN.rhythmSummary }
    static var a11yRhythm: String { prefersRu ? RU.a11yRhythm : EN.a11yRhythm }
    static var whyDayFeels: String { prefersRu ? RU.whyDayFeels : EN.whyDayFeels }
    static var a11yWhyHint: String { prefersRu ? RU.a11yWhyHint : EN.a11yWhyHint }
    static var energy: String { prefersRu ? RU.energy : EN.energy }
    static var balance: String { prefersRu ? RU.balance : EN.balance }
    static var focus: String { prefersRu ? RU.focus : EN.focus }
    static var heroFallback: String { prefersRu ? RU.heroFallback : EN.heroFallback }
    static var dayHeadlineFallback: String { prefersRu ? RU.dayHeadlineFallback : EN.dayHeadlineFallback }
    static var meaningToday: String { prefersRu ? RU.meaningToday : EN.meaningToday }
    static var lookDeeper: String { prefersRu ? RU.lookDeeper : EN.lookDeeper }
    static var lessonSubtitleFallback: String { prefersRu ? RU.lessonSubtitleFallback : EN.lessonSubtitleFallback }
    static var todayPrefix: String { prefersRu ? RU.todayPrefix : EN.todayPrefix }
    static var cardOfDay: String { prefersRu ? RU.cardOfDay : EN.cardOfDay }
    static var tarotA11yFaceUp: String { prefersRu ? RU.tarotA11yFaceUp : EN.tarotA11yFaceUp }
    static var tarotA11yBack: String { prefersRu ? RU.tarotA11yBack : EN.tarotA11yBack }
    static var tarotA11yFlip: String { prefersRu ? RU.tarotA11yFlip : EN.tarotA11yFlip }
    static var deeper: String { prefersRu ? RU.deeper : EN.deeper }
    static var firstMoveFallback: String { prefersRu ? RU.firstMoveFallback : EN.firstMoveFallback }
    static var cautionFallback: String { prefersRu ? RU.cautionFallback : EN.cautionFallback }
    static var todayDoFallback: String { prefersRu ? RU.todayDoFallback : EN.todayDoFallback }
    static var fullGuidanceCta: String { prefersRu ? RU.fullGuidanceCta : EN.fullGuidanceCta }
    static var numberOfDay: String { prefersRu ? RU.numberOfDay : EN.numberOfDay }
    static var ringsTitle: String { prefersRu ? RU.ringsTitle : EN.ringsTitle }
    static var ringsSubtitle: String { prefersRu ? RU.ringsSubtitle : EN.ringsSubtitle }
    static var practicesTitle: String { prefersRu ? RU.practicesTitle : EN.practicesTitle }
    static var ringHintWater: String { prefersRu ? RU.ringHintWater : EN.ringHintWater }
    static var ringHintBody: String { prefersRu ? RU.ringHintBody : EN.ringHintBody }
    static var ringHintMoney: String { prefersRu ? RU.ringHintMoney : EN.ringHintMoney }
    static var ringHintDefault: String { prefersRu ? RU.ringHintDefault : EN.ringHintDefault }
    static var ritualAffirmation: String { prefersRu ? RU.ritualAffirmation : EN.ritualAffirmation }
    static var ritualAscetic: String { prefersRu ? RU.ritualAscetic : EN.ritualAscetic }
    static var ritualPractice: String { prefersRu ? RU.ritualPractice : EN.ritualPractice }
    static var ritualJournal: String { prefersRu ? RU.ritualJournal : EN.ritualJournal }
    static var ritualRite: String { prefersRu ? RU.ritualRite : EN.ritualRite }
    static var ritualAsceticBody: String { prefersRu ? RU.ritualAsceticBody : EN.ritualAsceticBody }
    static var ritualPracticeBody: String { prefersRu ? RU.ritualPracticeBody : EN.ritualPracticeBody }
    static var ritualJournalBody: String { prefersRu ? RU.ritualJournalBody : EN.ritualJournalBody }
    static var ritualRiteBody: String { prefersRu ? RU.ritualRiteBody : EN.ritualRiteBody }
    static var microTitle: String { prefersRu ? RU.microTitle : EN.microTitle }
    static var microPrompt: String { prefersRu ? RU.microPrompt : EN.microPrompt }
    static var microReward: String { prefersRu ? RU.microReward : EN.microReward }
    static var microOptions: [String] { prefersRu ? RU.microOptions : EN.microOptions }
    static var ritualAffirmationFallback: String { prefersRu ? RU.ritualAffirmationFallback : EN.ritualAffirmationFallback }
    static var habitsTitle: String { prefersRu ? RU.habitsTitle : EN.habitsTitle }
    static var habitWater: String { prefersRu ? RU.habitWater : EN.habitWater }
    static var habitMove: String { prefersRu ? RU.habitMove : EN.habitMove }
    static var habitReflect: String { prefersRu ? RU.habitReflect : EN.habitReflect }
    static var habitWork: String { prefersRu ? RU.habitWork : EN.habitWork }
    static var habitSpend: String { prefersRu ? RU.habitSpend : EN.habitSpend }
    static var compatTitle: String { prefersRu ? RU.compatTitle : EN.compatTitle }
    static var compatBody: String { prefersRu ? RU.compatBody : EN.compatBody }
    static var compatCta: String { prefersRu ? RU.compatCta : EN.compatCta }
    static var guidTitle: String { prefersRu ? RU.guidTitle : EN.guidTitle }
    static var guidBody: String { prefersRu ? RU.guidBody : EN.guidBody }
    static var guidCta: String { prefersRu ? RU.guidCta : EN.guidCta }
    static var diaryTitle: String { prefersRu ? RU.diaryTitle : EN.diaryTitle }
    static var diaryBody: String { prefersRu ? RU.diaryBody : EN.diaryBody }
    static var diaryCta: String { prefersRu ? RU.diaryCta : EN.diaryCta }
    static var tomorrowTitle: String { prefersRu ? RU.tomorrowTitle : EN.tomorrowTitle }
    static var tomorrowBody: String { prefersRu ? RU.tomorrowBody : EN.tomorrowBody }
    static var tomorrowCta: String { prefersRu ? RU.tomorrowCta : EN.tomorrowCta }
    static var sheetWhyTitle: String { prefersRu ? RU.sheetWhyTitle : EN.sheetWhyTitle }
    static var sheetDone: String { prefersRu ? RU.sheetDone : EN.sheetDone }
    static var sheetNatal: String { prefersRu ? RU.sheetNatal : EN.sheetNatal }
    static var sheetMeaning: String { prefersRu ? RU.sheetMeaning : EN.sheetMeaning }
    static var sheetMoon: String { prefersRu ? RU.sheetMoon : EN.sheetMoon }
    static var sheetMoonFallback: String { prefersRu ? RU.sheetMoonFallback : EN.sheetMoonFallback }
    static var sheetFirstMove: String { prefersRu ? RU.sheetFirstMove : EN.sheetFirstMove }
    static var sheetFirstMoveFallback: String { prefersRu ? RU.sheetFirstMoveFallback : EN.sheetFirstMoveFallback }
    static var sheetRisk: String { prefersRu ? RU.sheetRisk : EN.sheetRisk }
    static var sheetBody: String { prefersRu ? RU.sheetBody : EN.sheetBody }
    static var sheetBodyFallback: String { prefersRu ? RU.sheetBodyFallback : EN.sheetBodyFallback }
    static var ringSheetTitle: String { prefersRu ? RU.ringSheetTitle : EN.ringSheetTitle }
    static var ringSheetClose: String { prefersRu ? RU.ringSheetClose : EN.ringSheetClose }
    static var ringSheetTailEmpty: String { prefersRu ? RU.ringSheetTailEmpty : EN.ringSheetTailEmpty }
    static var ringAskGuidance: String { prefersRu ? RU.ringAskGuidance : EN.ringAskGuidance }
    static var ringLove: String { prefersRu ? RU.ringLove : EN.ringLove }
    static var ringWealth: String { prefersRu ? RU.ringWealth : EN.ringWealth }
    static var ringDiscipline: String { prefersRu ? RU.ringDiscipline : EN.ringDiscipline }
    static var ringEmotion: String { prefersRu ? RU.ringEmotion : EN.ringEmotion }
    static var ringPurpose: String { prefersRu ? RU.ringPurpose : EN.ringPurpose }
    static var ringSelf: String { prefersRu ? RU.ringSelf : EN.ringSelf }
    static var gridLove: String { prefersRu ? RU.gridLove : EN.gridLove }
    static var gridWealth: String { prefersRu ? RU.gridWealth : EN.gridWealth }
    static var gridDiscipline: String { prefersRu ? RU.gridDiscipline : EN.gridDiscipline }
    static var gridEmotion: String { prefersRu ? RU.gridEmotion : EN.gridEmotion }
    static var gridPurpose: String { prefersRu ? RU.gridPurpose : EN.gridPurpose }
    static var gridSelf: String { prefersRu ? RU.gridSelf : EN.gridSelf }

    static var luckyPresets: [(String, String, String, String)] {
        prefersRu ? RU.luckyPresets : EN.luckyPresets
    }

    static func firstMove(_ v: String) -> String {
        (prefersRu ? RU.firstMovePrefix : EN.firstMovePrefix) + v
    }

    static func caution(_ v: String) -> String {
        (prefersRu ? RU.cautionPrefix : EN.cautionPrefix) + v
    }

    static func todayDo(_ v: String) -> String {
        (prefersRu ? RU.todayDoPrefix : EN.todayDoPrefix) + v
    }

    static func luckyWindow(_ t: String) -> String {
        (prefersRu ? RU.luckyWindowPrefix : EN.luckyWindowPrefix) + t
    }

    static func colorLine(_ c: String) -> String {
        (prefersRu ? RU.colorDotPrefix : EN.colorDotPrefix) + c
    }

    static func stoneLine(_ s: String) -> String {
        (prefersRu ? RU.stoneDotPrefix : EN.stoneDotPrefix) + s
    }

    static func elementLine(_ e: String) -> String {
        (prefersRu ? RU.elementDotPrefix : EN.elementDotPrefix) + e
    }

    static func ringSheetHeadline(_ name: String) -> String {
        (prefersRu ? RU.ringSheetHeadlinePrefix : EN.ringSheetHeadlinePrefix) + name
    }

    static func ringSheetBody(_ score: Int, _ tail: String) -> String {
        let p = prefersRu ? RU.ringSheetNowPrefix : EN.ringSheetNowPrefix
        let m = prefersRu ? RU.ringSheetScoreMid : EN.ringSheetScoreMid
        return p + "\(score)" + m + tail
    }

    static func ringSheetTailFactors(_ s: String) -> String {
        (prefersRu ? RU.ringSheetTailFactorsPrefix : EN.ringSheetTailFactorsPrefix) + s
    }
}
