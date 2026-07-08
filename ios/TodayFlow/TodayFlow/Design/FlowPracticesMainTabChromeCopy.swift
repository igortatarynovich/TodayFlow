import Foundation

// MARK: - Главный TabView (`ContentView`) — зеркало `frontend/src/components/today/flowPracticesMainTabChrome.ts` (`TODAY_MAIN_TAB_COPY_*`)

enum TodayMainTabCopy {
    private static var prefersRu: Bool { IOSAppLocale.prefersRussian }
    static var today: String { prefersRu ? "Сегодня" : "Today" }
    static var flow: String { "Flow" }
    static var profile: String { prefersRu ? "Профиль" : "Profile" }
    static var compatibility: String { prefersRu ? "Совместимость" : "Compatibility" }
    /// Паритет `nav.header.guidance` в `CONTENT/i18n/app.ru.json` (короткая подпись таба).
    static var practices: String { prefersRu ? "Практики" : "Practices" }
    static var tarot: String { prefersRu ? "Таро" : "Tarot" }
}

// MARK: - Flow tab (календарь, цели, аскезы)

enum FlowTrackerChromeCopy {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var connectionHeader: String { ru ? "Подключение" : "Connection" }
    static var loadingBootstrap: String {
        ru ? "Загружаю календарь и карты..." : "Loading calendar and maps..."
    }
    static var calendarFailed: String { ru ? "Календарь не загрузился" : "Calendar didn’t load" }
    static var retry: String { ru ? "Повторить" : "Retry" }
    static var navFlow: String { "Flow" }
    static var trackerAlertTitle: String { ru ? "Карты" : "Maps" }
    static var goalSheetTitle: String { ru ? "Цель" : "Goal" }
    static var close: String { ru ? "Закрыть" : "Close" }
    static var monthSubtitle: String {
        ru
            ? "Выбери день и отметь шаги по целям, привычкам и практикам."
            : "Pick a day and log goals, habits, and practices."
    }
    static var streaksNow: String { ru ? "Серии сейчас" : "Streaks" }
    static var monthStatsTitle: String { ru ? "Этот месяц в цифрах" : "This month in numbers" }
    static var statGoalDays: String { ru ? "Дни с целями" : "Days with goals" }
    static var statHabitDays: String { ru ? "Дни с привычками" : "Days with habits" }
    static var statFullCheckins: String { ru ? "Полные отметки" : "Full check-ins" }
    static var monthMapTitle: String { ru ? "Карта месяца" : "Month map" }
    static var selectedDay: String { ru ? "Выбранный день" : "Selected day" }
    static var dayTracker: String { ru ? "Ход дня" : "Day flow" }
    static var noMarksDay: String { ru ? "За этот день пока нет отметок." : "No entries for this day yet." }
    static var pickDayOnMap: String { ru ? "Выбери день на карте месяца." : "Pick a day on the month map." }
    static var habitsTitle: String { ru ? "Привычки" : "Habits" }
    static var habitsSyncNote: String {
        ru ? "Отметки на выбранный день совпадают с сайтом." : "Entries for the selected day match the website."
    }
    static var habitsEmpty: String {
        ru ? "Пока нет активных привычек — добавь первую ниже." : "No active habits yet—add one below."
    }
    // MARK: Веб `/habits` — карта привычек
    static var habitsMapAddCreating: String { ru ? "Создание..." : "Creating…" }
    static var habitsMapAddCta: String { ru ? "Добавить привычку" : "Add habit" }
    static var habitsMapAddSectionTitle: String { ru ? "Добавить привычку" : "Add a habit" }
    static var habitsMapCategoryPlaceholder: String {
        ru ? "Категория: body / focus / mind" : "Category: body / focus / mind"
    }
    static var habitsMapCheckErrorFallback: String { ru ? "Не удалось отметить привычку" : "Couldn’t log the habit" }
    static var habitsMapCreateErrorFallback: String { ru ? "Ошибка создания привычки" : "Couldn’t create the habit" }
    static var habitsMapEmptyList: String {
        ru ? "Привычек пока нет. Создай первую привычку выше." : "No habits yet—create your first one above."
    }
    static var habitsMapEyebrow: String { ru ? "Карта привычек" : "Habit map" }
    static var habitsMapHeroBody: String {
        ru
            ? "Здесь привычки не спорят с аскезами и практиками. Это отдельный слой дисциплины: повторяемые действия, мягкая визуализация ритма и понятная сводка."
            : "Habits don’t compete with ascetics or practices here. It’s a separate discipline layer—repeatable actions, a soft rhythm strip, and a clear summary."
    }
    static var habitsMapHeroTitle: String {
        ru ? "Карта привычек без лишнего шума" : "A habit map without the noise"
    }
    static var habitsMapHowToReadLine1: String {
        ru
            ? "Каждая привычка показывает свой ритм за последние 28 дней через мягкую heatmap-ленту."
            : "Each habit shows its last 28 days as a soft heatmap strip."
    }
    static var habitsMapHowToReadLine2: String {
        ru
            ? "Отметка сегодня нужна не ради «галочки», а чтобы видеть, какие действия реально держат твой день."
            : "Logging today isn’t about a checkbox—it shows which actions actually carry your day."
    }
    static var habitsMapHowToReadTitle: String { ru ? "Как читать карту" : "How to read the map" }
    static var habitsMapLinkCalendar: String { ru ? "К календарю" : "Open calendar" }
    static var habitsMapLinkToday: String { ru ? "К Today" : "To Today" }
    static var habitsMapLinkTrackingHub: String { ru ? "Мои карты" : "My maps" }
    static var habitsMapLoadErrorFallback: String { ru ? "Не удалось загрузить карту привычек" : "Couldn’t load the habit map" }
    static var habitsMapLoginLead: String {
        ru
            ? "Войди, чтобы выстроить личный ритм и видеть, как складывается история — без таблиц и процентов."
            : "Sign in to shape your rhythm and see your story take shape—no spreadsheets or percentages."
    }
    static var habitsMapMarkedToday: String { ru ? "Отмечено" : "Logged" }
    static var habitsMapMarkToday: String { ru ? "Отметить сегодня" : "Log today" }
    static var habitsMapNamePlaceholder: String {
        ru ? "Например: 10 минут дыхания" : "e.g. 10 minutes breathing"
    }
    static var habitsMapNoCategory: String { ru ? "без категории" : "no category" }
    static var habitsMapPageTitle: String { ru ? "Карта привычек" : "Habit map" }
    static func habitsMapStatsCompact(streak: Int, rate: Int) -> String {
        _ = rate
        return Self.habitMapStatsLine(streakDays: streak)
    }

    static func habitMapStatsLine(streakDays: Int) -> String {
        if ru {
            if streakDays >= 14 { return "\(streakDays) дней подряд — узор на карте уже заметен" }
            if streakDays >= 7 { return "\(streakDays) дней подряд — история складывается" }
            if streakDays >= 1 {
                let dayWord = streakDays == 1 ? "день" : (streakDays < 5 ? "дня" : "дней")
                return "\(streakDays) \(dayWord) подряд на карте"
            }
            return "Первые отметки — узор только начинается"
        }
        if streakDays >= 14 { return "\(streakDays) days in a row—the weave on your map is showing" }
        if streakDays >= 7 { return "\(streakDays) days in a row—your story is taking shape" }
        if streakDays >= 1 { return "\(streakDays) day\(streakDays == 1 ? "" : "s") marked on the map" }
        return "First marks—the pattern is just beginning"
    }
    static var habitsMapStatsPending: String { ru ? "История только начинается" : "Your story is just beginning" }
    static func habitsMapStrongestRhythm(name: String, days: Int) -> String {
        ru
            ? "Самый сильный текущий ритм: \(name), стрик \(days) дн."
            : "Strongest rhythm now: \(name), streak \(days) d"
    }
    static var habitsMapStrongestRhythmEmpty: String {
        ru
            ? "Когда появятся первые отметки, здесь будет виден самый устойчивый ритм."
            : "After your first check-ins, the steadiest rhythm shows here."
    }
    static var habitsMapSummary30Empty: String {
        ru ? "Сводка появится после первых отметок." : "Summary appears after the first check-ins."
    }
    static var habitsMapSummary30Title: String { ru ? "Сводка за 30 дней" : "30-day summary" }
    static var habitsMapSummaryStreakLabel: String { ru ? "Стрик:" : "Streak:" }
    static func habitsMapTodayProgress(done: Int, total: Int) -> String {
        ru ? "\(done) из \(total) привычек отмечено" : "\(done) of \(total) habits logged today"
    }
    static var habitsMapTodaySnapshotEyebrow: String { ru ? "Сегодняшний срез" : "Today’s snapshot" }
    static var newHabit: String { ru ? "Новая привычка" : "New habit" }
    static var habitCategory: String { ru ? "Категория (как в веб-мастере)" : "Category (same as web)" }
    static var habitIdeas: String { ru ? "Идеи" : "Ideas" }
    static var habitSheetTitle: String { ru ? "Привычка" : "Habit" }
    static var habitCadence: String { ru ? "Частота" : "Cadence" }
    static var habitDaily: String { ru ? "Каждый день" : "Every day" }
    static var habitWeekly: String { ru ? "Несколько раз в неделю" : "A few times a week" }
    static func habitWeekTarget(_ n: Int) -> String {
        ru ? "Цель: \(n) раза за неделю" : "Target: \(n)× per week"
    }
    /// Общий плейсхолдер для названия привычки, цели и т.п.
    static var nameFieldPlaceholder: String { ru ? "Название" : "Name" }
    static var create: String { ru ? "Создать" : "Create" }
    static var asceticsTitle: String { ru ? "Аскезы" : "Ascetics" }
    static var asceticsSyncNote: String {
        ru ? "Отметка дня — тот же запрос, что и на сайте." : "Same day log as on the website."
    }
    static var asceticsEmpty: String {
        ru
            ? "Пока нет активных аскез для отметки. Создай контракт через Today: «Собрать день» → чип «эмоции»."
            : "No active ascetics to log. Create a contract from Today: Build day → emotions chip."
    }
    static var practiceTitle: String { ru ? "Практика" : "Practice" }
    static var practiceDoneLabel: String { ru ? "Отмечено на этот день" : "Logged for this day" }
    static var practiceHint: String {
        ru
            ? "Быстрая отметка, как на сайте. Снять её здесь нельзя — только в разделе практик."
            : "Quick log like on the website. You can’t remove it here—only in Practices."
    }
    static var logPractice: String { ru ? "Отметить практику" : "Log practice" }
    static var affirmationsTitle: String { ru ? "Аффирмации" : "Affirmations" }
    static var affirmationsSyncNote: String {
        ru ? "Отметки на выбранный день — через тот же журнал, что и на сайте." : "Same logging as on the website."
    }
    static var affirmationsCatalogEmpty: String {
        ru
            ? "Каталог не загрузился или пуст. Следующий шаг — отдельный нативный каталог."
            : "Catalog didn’t load or is empty. Next: a native catalog screen."
    }

    static func affirmationsCatalogCount(n: Int) -> String {
        if !ru {
            return n == 1 ? "\(n) item" : "\(n) items"
        }
        let mod10 = n % 10
        let mod100 = n % 100
        if mod10 == 1 && mod100 != 11 { return "\(n) позиция" }
        if mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20) { return "\(n) позиции" }
        return "\(n) позиций"
    }

    static var affirmationsCatalogSectionTitle: String { ru ? "Каталог" : "Catalog" }
    static var affirmationsCtaMoveToday: String { ru ? "Перенести в Today" : "Move to Today" }
    static var affirmationsCtaOpenPractices: String { ru ? "Открыть практики" : "Open practices" }
    static var affirmationsCtaOpenToday: String { ru ? "Открыть Today" : "Open Today" }
    static var affirmationsCtaOpenTracker: String { ru ? "Открыть карту" : "Open map" }
    static var affirmationsCtaSignInToday: String { ru ? "Войти и открыть Today" : "Sign in to open Today" }
    static var affirmationsCtaSignInUse: String { ru ? "Войти и использовать" : "Sign in to use" }
    static var affirmationsDefaultTitleAffirmation: String { ru ? "Аффирмация" : "Affirmation" }
    static var affirmationsDefaultTitleMantra: String { ru ? "Мантра" : "Mantra" }
    static var affirmationsEmptyFilterHint: String {
        ru
            ? "По этим условиям пока ничего не найдено. Попробуй снять часть фильтров или задать более широкий запрос."
            : "Nothing matches yet. Try loosening filters or broadening your search."
    }
    static var affirmationsFeaturedSectionTitle: String {
        ru ? "Сейчас может откликнуться" : "You might resonate with"
    }
    static var affirmationsFocusCalmHint: String {
        ru ? "Собраться, выдохнуть, не расплескать себя." : "Ground yourself, exhale, stay contained."
    }
    static var affirmationsFocusCalmTitle: String { ru ? "Спокойствие" : "Calm" }
    static var affirmationsFocusGrowthHint: String {
        ru ? "Развитие, смелость и движение дальше." : "Growth, courage, moving forward."
    }
    static var affirmationsFocusGrowthTitle: String { ru ? "Рост" : "Growth" }
    static var affirmationsFocusLoveHint: String {
        ru ? "Контакт, близость, открытость и доверие." : "Contact, closeness, openness, trust."
    }
    static var affirmationsFocusLoveTitle: String { ru ? "Отношения" : "Relationships" }
    static var affirmationsFocusMoneyHint: String {
        ru ? "Опора, изобилие, материальная устойчивость." : "Stability, abundance, material footing."
    }
    static var affirmationsFocusMoneyTitle: String { ru ? "Деньги" : "Money" }
    static var affirmationsFocusSupportHint: String {
        ru ? "Мягкий внутренний голос и восстановление." : "A gentle inner voice and recovery."
    }
    static var affirmationsFocusSupportTitle: String { ru ? "Поддержка" : "Support" }
    static var affirmationsFocusWorkHint: String {
        ru ? "Роль, реализация, решение и действие." : "Role, execution, decisions, action."
    }
    static var affirmationsFocusWorkTitle: String { ru ? "Работа" : "Work" }
    static var affirmationsFocusAllHint: String {
        ru ? "Полная библиотека фраз и опор." : "The full library of phrases and anchors."
    }
    static var affirmationsFocusAllTitle: String { ru ? "Все темы" : "All themes" }
    static var affirmationsKindLabelAffirmation: String { ru ? "Аффирмация" : "Affirmation" }
    static var affirmationsKindLabelMantra: String { ru ? "Мантра" : "Mantra" }
    static var affirmationsKindFilterAffirmation: String { ru ? "Аффирмации" : "Affirmations" }
    static var affirmationsKindFilterAll: String { ru ? "Всё" : "All" }
    static var affirmationsKindFilterMantra: String { ru ? "Мантры" : "Mantras" }
    static var affirmationsLibraryLinkAllTrackers: String { ru ? "Все карты" : "All maps" }
    static var affirmationsLibraryLoadError: String {
        ru ? "Не удалось загрузить библиотеку." : "Couldn’t load the library."
    }
    static var affirmationsLibraryPageEyebrow: String { ru ? "Библиотека" : "Library" }
    static var affirmationsLibraryPageLead: String {
        ru
            ? "Здесь собраны короткие фразы и опорные формулы, которые помогают собраться, удержать состояние, пройти напряжённый момент или мягко закрепить новый внутренний ход."
            : "Short phrases and anchor formulas to steady yourself, hold a state, move through tension, or gently lock in a new inner move."
    }
    static var affirmationsLibraryPageTitle: String {
        ru ? "Библиотека аффирмаций и мантр" : "Affirmations & mantras library"
    }
    static var affirmationsLibraryLinkTracker: String { ru ? "Карта аффирмаций" : "Affirmations map" }
    static func affirmationsMantraPronunciationPrefix(text: String) -> String {
        ru ? "Произношение: \(text)" : "Pronunciation: \(text)"
    }
    static var affirmationsPersonalBadge: String { ru ? "Персонально" : "Personal" }
    static var affirmationsPersonalCta: String { ru ? "Подобрать 3 формулировки" : "Suggest 3 lines" }
    static var affirmationsPersonalEmptyHint: String {
        ru
            ? "Здесь появятся дополнительные формулировки под выбранную тему."
            : "More lines for your theme will show up here."
    }
    static var affirmationsPersonalGenerating: String { ru ? "Собираем..." : "Gathering…" }
    static var affirmationsPersonalSectionBody: String {
        ru
            ? "Если хочется не только библиотеку, но и несколько свежих фраз под текущую тему, можно собрать их отдельно."
            : "Want more than the library? Pull a few fresh lines for the theme you picked."
    }
    static var affirmationsPersonalSectionTitle: String { ru ? "Личные формулировки" : "Personal lines" }
    static var affirmationsSearchPlaceholder: String {
        ru
            ? "Поиск по словам, состоянию, теме или смыслу..."
            : "Search by word, state, theme, or meaning…"
    }

    static var affirmationsTrackerBackToAllTrackers: String { ru ? "← Все карты" : "← All maps" }
    static var affirmationsTrackerBackToCatalog: String { ru ? "← Каталог аффирмаций" : "← Affirmations catalog" }
    static var affirmationsTrackerEntryNotUsed: String { ru ? "○ Не использовано" : "○ Not used" }
    static var affirmationsTrackerEntryStateLabel: String { ru ? "Состояние:" : "State:" }
    static var affirmationsTrackerEntryUsed: String { ru ? "✓ Использовано" : "✓ Used" }
    static var affirmationsTrackerLoginPrompt: String {
        ru ? "Войдите, чтобы открыть карту аффирмаций." : "Sign in to open the affirmations map."
    }
    static var affirmationsTrackerNewEntryTitle: String { ru ? "Новая запись" : "New entry" }
    static var affirmationsTrackerNoEntriesForDate: String { ru ? "Нет записей за эту дату" : "No entries for this date" }
    static var affirmationsTrackerNoteLabel: String { ru ? "Заметка (опционально)" : "Note (optional)" }
    static var affirmationsTrackerNotePlaceholder: String { ru ? "Короткая заметка…" : "Short note…" }
    static var affirmationsTrackerPageLead: String {
        ru
            ? "Короткие фразы для закрепления состояния. Выбери одну аффирмацию на день и отметь использование."
            : "Short phrases to anchor a state. Pick one affirmation for the day and log that you used it."
    }
    static var affirmationsTrackerScaleLabel: String { ru ? "Шкала состояния (1–5)" : "State scale (1–5)" }
    static var affirmationsTrackerSelectLabel: String { ru ? "Аффирмация (короткая фраза)" : "Affirmation (short line)" }
    static var affirmationsTrackerSelectPlaceholder: String { ru ? "Выберите аффирмацию" : "Choose an affirmation" }
    static var affirmationsTrackerStateLabel: String { ru ? "Состояние (1–2 слова)" : "State (1–2 words)" }
    static var affirmationsTrackerStatePlaceholder: String {
        ru ? "например: спокойно, сфокусированно" : "e.g. calm, focused"
    }
    static var affirmationsTrackerToastPickAffirmation: String { ru ? "Выберите аффирмацию" : "Choose an affirmation" }
    static var affirmationsTrackerUsedLabel: String { ru ? "Использовано" : "Used" }

    static var actionCancel: String { ru ? "Отмена" : "Cancel" }
    static var actionSave: String { ru ? "Сохранить" : "Save" }
    static var diaryTitle: String { ru ? "Дневник наблюдений" : "Observation journal" }
    static var diaryIntro: String {
        ru
            ? "Без анализа и драматизации: что заметила, где было сложнее, что оказалось легче."
            : "No drama—what you noticed, what was harder, what felt easier."
    }
    static var diaryNoticedTitle: String { ru ? "Что заметила" : "What you noticed" }
    static var diaryNoticedPrompt: String {
        ru ? "1–2 предложения о главном наблюдении" : "1–2 sentences on the main observation"
    }
    static var diaryHardestTitle: String { ru ? "Где было сложнее всего" : "Where it was hardest" }
    static var diaryHardestPrompt: String { ru ? "Где день начал распадаться" : "Where the day started to slip" }
    static var diaryEasierTitle: String { ru ? "Что оказалось легче" : "What felt easier" }
    static var diaryEasierPrompt: String { ru ? "Что прошло мягче, чем ожидалось" : "What went smoother than expected" }
    static var diaryEasierPlaceholder: String {
        ru ? "1–2 предложения о том, что оказалось легче…" : "1–2 sentences about what felt easier…"
    }
    static var diaryHardestPlaceholder: String {
        ru ? "1–2 предложения о том, где было сложнее всего…" : "1–2 sentences about where it was hardest…"
    }
    static var diaryNoticedPlaceholder: String {
        ru ? "1–2 предложения о том, что заметил…" : "1–2 sentences about what you noticed…"
    }
    static var saveDiary: String { ru ? "Сохранить запись" : "Save entry" }
    static var saveDiarySaving: String { ru ? "Сохранение..." : "Saving…" }
    static var savedForDay: String { ru ? "Сохранено на день" : "Saved for this day" }
    static var summaryNoticed: String { ru ? "Заметила" : "Noticed" }
    static var summaryHardest: String { ru ? "Сложнее всего" : "Hardest" }
    static var summaryEasier: String { ru ? "Легче, чем ожидалось" : "Easier than expected" }
    static var insightsTitle: String { ru ? "Автоинсайты" : "Auto insights" }
    static var insightsIntro: String {
        ru
            ? "Инсайт собирается из отметок календаря и дневника за выбранный день."
            : "Built from calendar entries and journal for the selected day."
    }
    static var generatingInsight: String { ru ? "Собираем инсайт" : "Generating insight" }
    static var generateInsight: String { ru ? "Сгенерировать инсайт" : "Generate insight" }
    static var insightsGenerateErrorFallback: String {
        ru ? "Ошибка при генерации инсайта" : "Couldn’t generate the insight"
    }
    static var insightsGeneratingShort: String { ru ? "Генерация..." : "Generating…" }
    static var insightsEmpty: String {
        ru
            ? "За эту дату инсайтов пока нет. Добавь 1-2 отметки и нажми «Сгенерировать инсайт»."
            : "No insights for this date yet. Add 1–2 entries, then tap Generate insight."
    }
    static var trackingDiaryEasierFieldLabel: String {
        ru ? "Что оказалось легче, чем ожидал" : "What felt easier than expected"
    }
    static var trackingDiaryEntryFormTitle: String { ru ? "Запись наблюдений" : "Observation entry" }
    static var trackingDiaryFillAtLeastOne: String { ru ? "Заполните хотя бы одно поле" : "Fill in at least one field" }
    static var trackingDiaryHardestFieldLabel: String { ru ? "Где было сложнее всего" : "Where it was hardest" }
    static var trackingDiaryLoginPrompt: String {
        ru ? "Войдите, чтобы использовать дневник наблюдений" : "Sign in to use the observation journal"
    }
    static var trackingDiaryNoticedFieldLabel: String { ru ? "Что я заметил" : "What I noticed" }
    static var trackingDiaryPageIntro: String {
        ru
            ? "Не анализ, а отражение. Что заметил, где было сложнее всего, что оказалось легче. Без выводов, без «почему» — просто наблюдение."
            : "Reflection, not analysis—what you noticed, what was hardest, what felt easier. No conclusions, no “why”—just observation."
    }
    static var trackingDiaryReadoutEasier: String { ru ? "Что оказалось легче:" : "What felt easier:" }
    static var trackingDiaryReadoutHardest: String { ru ? "Где было сложнее всего:" : "Where it was hardest:" }
    static var trackingDiaryReadoutNoticed: String { ru ? "Что заметил:" : "What you noticed:" }
    static var trackingDiarySaveError: String { ru ? "Ошибка при сохранении" : "Couldn’t save the entry" }
    static func trackingDiaryEntriesHeading(date: String) -> String {
        ru ? "Записи за \(date)" : "Entries for \(date)"
    }
    static var trackingFormDateLabel: String { ru ? "Дата" : "Date" }
    static var trackingInsightConfidenceHigh: String { ru ? "Высокая уверенность" : "High confidence" }
    static var trackingInsightConfidenceLow: String { ru ? "Низкая уверенность" : "Low confidence" }
    static var trackingInsightConfidenceMedium: String { ru ? "Средняя уверенность" : "Medium confidence" }
    static var trackingInsightDataAvgMood: String { ru ? "Среднее настроение:" : "Average mood:" }
    static var trackingInsightDataClearDecisions: String { ru ? "Ясных решений:" : "Clear decisions:" }
    static var trackingInsightDataDaysReviewed: String { ru ? "Дней в анализе:" : "Days in the window:" }
    static var trackingInsightDataDominantFocus: String { ru ? "Доминирующий фокус:" : "Dominant focus:" }
    static var trackingInsightDataEntries: String { ru ? "Записей:" : "Entries:" }
    static var trackingInsightDataGatheredDays: String { ru ? "Собранных дней:" : "Gathered days:" }
    static var trackingInsightDataRepeatCount: String { ru ? "Повторений:" : "Repeats:" }
    static func trackingInsightDataTotalCountSuffix(n: Int) -> String { ru ? "\(n) всего" : "\(n) total" }
    static var trackingInsightDataUngatheredDays: String { ru ? "Несобранных дней:" : "Ungathered days:" }
    static var trackingInsightDataUnclearDecisions: String { ru ? "Неясных решений:" : "Unclear decisions:" }
    static var trackingInsightDataWeekendEntries: String { ru ? "Выходных записей:" : "Weekend share:" }
    static var trackingInsightTypeCorrelation: String { ru ? "Корреляция" : "Correlation" }
    static var trackingInsightTypePattern: String { ru ? "Паттерн" : "Pattern" }
    static var trackingInsightTypeShift: String { ru ? "Сдвиг" : "Shift" }
    static var trackingInsightTypeSignalClarity: String { ru ? "Ясность решения" : "Decision clarity" }
    static var trackingInsightTypeSignalClosure: String { ru ? "Собранность дня" : "Day closure" }
    static var trackingInsightTypeSignalFocus: String { ru ? "Повторяющийся фокус" : "Recurring focus" }
    static var trackingInsightTypeStreak: String { ru ? "Стрик" : "Streak" }
    static var trackingInsightTypeWeekendPattern: String { ru ? "Паттерн выходных" : "Weekend pattern" }
    static var trackingInsightsEmptyHint: String {
        ru
            ? "Нажми «Сгенерировать инсайт» и добавь 1-2 отметки за день."
            : "Tap “Generate insight” and add 1–2 check-ins for the day."
    }
    static var trackingInsightsEmptyTitle: String { ru ? "Нет инсайтов за эту дату." : "No insights for this date." }
    static var trackingInsightsLoginPrompt: String {
        ru ? "Войдите, чтобы видеть автоматические инсайты" : "Sign in to see automatic insights"
    }
    static var trackingInsightsPageLead: String {
        ru
            ? "Здесь ты видишь короткие наблюдения за день и следующий практичный шаг."
            : "Short observations for the day and a practical next step."
    }
    static var trackingInsightsPageTitle: String { ru ? "Автоматические инсайты" : "Automatic insights" }
    /// Подпись типа инсайта (веб `/tracking/insights` и нативные карточки).
    static func trackingAutoInsightTypeLabel(for raw: String) -> String {
        switch raw {
        case "streak": return trackingInsightTypeStreak
        case "pattern": return trackingInsightTypePattern
        case "shift": return trackingInsightTypeShift
        case "correlation": return trackingInsightTypeCorrelation
        case "weekend_pattern": return trackingInsightTypeWeekendPattern
        case "signal_closure": return trackingInsightTypeSignalClosure
        case "signal_clarity": return trackingInsightTypeSignalClarity
        case "signal_focus": return trackingInsightTypeSignalFocus
        default: return raw.replacingOccurrences(of: "_", with: " ")
        }
    }
    static var weeklyPulseTitle: String { ru ? "Пульс недели" : "Weekly pulse" }
    static var weeklyPulseEmpty: String {
        ru
            ? "Когда накопится несколько дней, здесь появится нативная карта недели по энергии, балансу и фокусу."
            : "After a few days, a native week map for energy, balance, and focus appears here."
    }
    static var energy: String { ru ? "Энергия" : "Energy" }
    static var balance: String { ru ? "Баланс" : "Balance" }
    static var focus: String { ru ? "Фокус" : "Focus" }
    static var rhythmEncouragementFallback: String {
        ru ? "Ритм недели уже виден по накопленным дням." : "Your week rhythm shows in the days you’ve logged."
    }
    static var openGoals: String { ru ? "Открыть цели" : "Open goals" }
    static var trackingFooter: String {
        ru ? "Здесь собирается история твоего ритма." : "Your rhythm story gathers here."
    }
    static var trackingCalendarEmptyState: String { ru ? "Нет данных календаря." : "No calendar data." }
    static var trackingCalendarLoginPrompt: String {
        ru ? "Войдите, чтобы открыть карты." : "Sign in to open your maps."
    }
    /// Веб `/tracking/calendar` — hero; iOS может переиспользовать при паритете экрана.
    static var trackingCalendarPageEyebrow: String { ru ? "Трекинг" : "Tracking" }
    static var trackingCalendarPageTitle: String {
        ru ? "Flow: ритм и действия" : "Flow: rhythm and actions"
    }
    static var trackingCalendarPageIntro: String {
        ru
            ? "Здесь видно, как день за днем складываются цели, привычки и практики. Один экран — вся картина твоего ритма."
            : "See how goals, habits, and practices add up day by day. One screen—the full picture of your rhythm."
    }
    // MARK: Веб `entityTrackerSpec` — категории сводки (зеркало TS)
    static var trackingCategoryAsceticEmpty: String { ru ? "аскез нет" : "no ascetics" }
    static var trackingCategoryAsceticMixed: String {
        ru ? "есть срывы, но трек живой" : "slips, but the track is alive"
    }
    static var trackingCategoryAsceticStrong: String { ru ? "удерживаешь правила" : "you’re keeping the rules" }
    static var trackingCategoryAsceticWeak: String { ru ? "много остановок или срывов" : "many stops or breaks" }
    static var trackingCategoryGoalEmpty: String { ru ? "целей пока нет" : "no goals yet" }
    static var trackingCategoryGoalMixed: String { ru ? "есть движение, но не по всем" : "movement, but not on all" }
    static var trackingCategoryGoalOverloaded: String {
        ru ? "целей слишком много для устойчивого ритма" : "too many goals for a steady rhythm"
    }
    static var trackingCategoryGoalStrong: String { ru ? "по целям есть движение" : "goals are moving" }
    static var trackingCategoryGoalWeak: String { ru ? "много застоя по целям" : "a lot of stagnation on goals" }
    static var trackingCategoryHabitEmpty: String { ru ? "привычек нет" : "no habits" }
    static var trackingCategoryHabitMixed: String { ru ? "кто-то держится, кто-то плавает" : "some hold, some drift" }
    static var trackingCategoryHabitStrong: String { ru ? "большинство держится" : "most are holding" }
    static var trackingCategoryHabitWeak: String { ru ? "много брошенных или слабых линий" : "many dropped or weak lines" }
    static var trackingCategoryPracticeActive: String { ru ? "выполняешь предложенное" : "you’re doing what’s suggested" }
    static var trackingCategoryPracticeEmpty: String { ru ? "практики не подключены" : "practices not connected" }
    static var trackingCategoryPracticeIgnored: String {
        ru ? "системные практики игнорируются" : "system practices are ignored"
    }
    static var trackingCategoryPracticeNeutral: String { ru ? "иногда делаешь" : "you do them sometimes" }
    // MARK: Веб `entityTrackerCompute.categorySummaryLines`
    static var trackingCatSummaryAsceticsZero: String { ru ? "0 активных" : "0 active" }
    static func trackingCatSummaryAsceticsCounts(total: Int, holding: Int, broken: Int) -> String {
        ru
            ? "\(total) активные · \(holding) держится · \(broken) сорвалась"
            : "\(total) active · \(holding) holding · \(broken) slipped"
    }
    static var trackingCatSummaryGoalsZero: String { ru ? "0 активных" : "0 active" }
    static func trackingCatSummaryGoalsCounts(total: Int, inProgress: Int, stalled: Int) -> String {
        ru
            ? "\(total) активные · \(inProgress) в прогрессе · \(stalled) в застое"
            : "\(total) active · \(inProgress) in progress · \(stalled) stalled"
    }
    static var trackingCatSummaryHabitsZero: String { ru ? "0 активных" : "0 active" }
    static func trackingCatSummaryHabitsCounts(total: Int, holding: Int, unstable: Int) -> String {
        ru
            ? "\(total) активные · \(holding) держатся · \(unstable) нестабильны"
            : "\(total) active · \(holding) holding · \(unstable) unstable"
    }
    static var trackingCatSummaryPracticesActive: String { ru ? "выполняется" : "in progress" }
    static var trackingCatSummaryPracticesEmpty: String { ru ? "система предлагает практики" : "system suggests practices" }
    static var trackingCatSummaryPracticesIgnored: String { ru ? "игнорируется" : "ignored" }
    static var trackingCatSummaryPracticesNeutral: String { ru ? "иногда" : "sometimes" }
    static var trackingCatSummaryPracticesPrefix: String { ru ? "система предлагает 1 · " : "system suggests 1 · " }
    // MARK: Веб `entityTrackerCompute` — attention / best lines
    static var trackingAttentionAsceticBreaksLine: String { ru ? "есть срывы" : "has slips" }
    static func trackingAttentionAsceticFailedLine(count: Int) -> String {
        ru ? "\(count) срывов (окно 7 дн.)" : "\(count) slips (7-day window)"
    }
    static func trackingAttentionGoalStalledLine(days: Int) -> String {
        ru ? "застой \(days) дн." : "stalled \(days) d"
    }
    static func trackingAttentionHabitDroppedLine(days: Int) -> String {
        ru ? "брошена · без отметок \(days) дн." : "dropped · no check-ins \(days) d"
    }
    static var trackingAttentionUnstableShort: String { ru ? "нестабильно" : "unstable" }
    static func trackingBestAsceticHoldLine(n: Int) -> String { ru ? "держишься \(n) дн." : "holding \(n) d" }
    static func trackingBestGoalSteps5dLine(n: Int) -> String {
        ru ? "\(n) шага за 5 дней" : "\(n) steps in 5 days"
    }
    static func trackingBestHabitStreakLine(n: Int) -> String {
        ru ? "\(n) дней подряд" : "\(n) days in a row"
    }
    // MARK: Веб `/tracking/progress` — хаб ссылок (iOS при паритете экрана-обзора)
    static var trackingProgressCardAffirmationsDesc: String {
        ru ? "Отдельный поток для аффирмаций." : "A dedicated flow for affirmations."
    }
    static var trackingProgressCardAffirmationsTitle: String {
        ru ? "Карта аффирмаций" : "Affirmations map"
    }
    static var trackingProgressCardAsceticClassicDesc: String {
        ru
            ? "Альтернативный экран только для отметок по аскезам — если привык к старому сценарию."
            : "Alternate screen for ascetic check-ins only—if you prefer the classic flow."
    }
    static var trackingProgressCardAsceticClassicTitle: String {
        ru ? "Карта аскез (классический вид)" : "Ascetics map (classic)"
    }
    static var trackingProgressCardHabitsListDesc: String {
        ru ? "Расширенный обзор и история — создание дублирует календарный мастер." : "Broader overview and history—creation matches the calendar wizard."
    }
    static var trackingProgressCardHabitsListTitle: String { ru ? "Карта привычек" : "Habit map" }
    static var trackingProgressCardMainCalendarDesc: String {
        ru
            ? "Главная точка: карта месяца, цели, привычки, аскезы и практики. Создание целей, привычек и контрактов аскез — прямо здесь, без переходов."
            : "Main hub: month map, goals, habits, ascetics, and practices. Create goals, habits, and ascetic contracts right here—no extra hops."
    }
    static var trackingProgressCardMainCalendarTitle: String {
        ru ? "Карта ритма" : "Rhythm map"
    }
    static var trackingProgressCardQuickAsceticDesc: String {
        ru ? "Выбор из каталога и срок контракта." : "Pick from the catalog and set the contract length."
    }
    static var trackingProgressCardQuickAsceticTitle: String {
        ru ? "Быстро: новая аскеза" : "Quick: new ascetic"
    }
    static var trackingProgressCardQuickGoalDesc: String {
        ru ? "Откроется календарь с мастером создания цели." : "Opens the calendar with the goal creation wizard."
    }
    static var trackingProgressCardQuickGoalTitle: String {
        ru ? "Быстро: новая цель" : "Quick: new goal"
    }
    static var trackingProgressCardQuickHabitDesc: String {
        ru ? "Мастер привычки с подборкой шаблонов." : "Habit wizard with template picks."
    }
    static var trackingProgressCardQuickHabitTitle: String {
        ru ? "Быстро: новая привычка" : "Quick: new habit"
    }
    static var trackingProgressFooterAffirmationsLibrary: String {
        ru ? "Библиотека аффирмаций и мантр" : "Affirmations & mantras library"
    }
    static var trackingProgressFooterAsceticCatalog: String { ru ? "Каталог аскез" : "Ascetics catalog" }
    static var trackingProgressHubEyebrow: String { ru ? "История" : "History" }
    static var trackingProgressHubIntro: String {
        ru
            ? "Здесь собраны карты твоей жизни: ритм месяца, привычки, аскезы и аффирмации. Каждый день в Today добавляет новые точки — узор складывается сам."
            : "Life maps in one place: month rhythm, habits, ascetics, and affirmations. Each day in Today adds a point—the pattern grows on its own."
    }
    static var trackingProgressHubLoginBody: String {
        ru
            ? "Войдите, чтобы открыть карты ритма, привычек, аскез и аффирмаций."
            : "Sign in to open your rhythm, habit, ascetic, and affirmation maps."
    }
    static var trackingProgressHubLoginCta: String { ru ? "Войти" : "Sign in" }
    static var trackingProgressHubLoginTitle: String { ru ? "Мои карты" : "My maps" }
    static var trackingProgressHubTitle: String { ru ? "Мои карты" : "My maps" }
    static var trackingMarkTodayAfterSave: String { ru ? "Сегодня засчитан" : "Today counted" }
    static var trackingMarkTodayFab: String { ru ? "Отметить сегодня" : "Mark today" }
    static var trackingMarkTodayFabEmpty: String { ru ? "Отметь первый день" : "Log your first day" }
    static var trackingMarkTodayModalTitle: String { ru ? "Сегодня" : "Today" }
    static var trackingScreenHeroDroppedSub: String {
        ru ? "Большая часть треков без движения — вернись к простому шагу." : "Most tracks aren’t moving—return to a simple step."
    }
    static var trackingScreenHeroDroppedTitle: String { ru ? "Много линий без опоры" : "Many lines without support" }
    static var trackingScreenHeroEmptySub: String {
        ru ? "Добавь цель, привычку или аскезу — тогда появится общая картина."
            : "Add a goal, habit, or ascetic—then you’ll see the full picture."
    }
    static var trackingScreenHeroEmptyTitle: String { ru ? "Начни с одной линии" : "Start with one line" }
    static var trackingScreenHeroInFlowSub: String { ru ? "Держишь то, что взял на себя." : "You’re holding what you committed to." }
    static var trackingScreenHeroInFlowTitle: String { ru ? "Ты в ритме" : "You’re in rhythm" }
    static var trackingScreenHeroOverloadedSub: String {
        ru ? "Активных треков слишком много, удерживать всё сложно." : "Too many active tracks; holding everything is hard."
    }
    static var trackingScreenHeroOverloadedTitle: String { ru ? "Ты перегружен" : "You’re overloaded" }
    static var trackingScreenHeroUnstableSub: String {
        ru ? "Часть линий держится, часть уже просела." : "Some lines hold, others have slipped."
    }
    static var trackingScreenHeroUnstableTitle: String { ru ? "Ты теряешь ритм" : "You’re losing the rhythm" }
    static var trackingStatusAsceticBreaks: String { ru ? "есть срывы" : "there are slips" }
    static var trackingStatusAsceticFailed: String { ru ? "срывы подряд" : "slips in a row" }
    static var trackingStatusAsceticHolding: String { ru ? "держишься" : "holding on" }
    static var trackingStatusAsceticStopped: String { ru ? "остановлена" : "stopped" }
    static var trackingStatusGoalActiveProgress: String { ru ? "в прогрессе" : "in progress" }
    static var trackingStatusGoalCompleted: String { ru ? "завершена" : "completed" }
    static var trackingStatusGoalStalled: String { ru ? "застой" : "stalled" }
    static var trackingStatusGoalUnstable: String { ru ? "нестабильно" : "unstable" }
    static var trackingStatusHabitActive: String { ru ? "держится" : "holding" }
    static var trackingStatusHabitDropped: String { ru ? "брошена" : "dropped" }
    static var trackingStatusHabitUnstable: String { ru ? "нестабильно" : "unstable" }
    // MARK: Веб мастер сущностей `/tracking/calendar` (`EntityCreateWizard`)
    static var trackingEntityWizardAsceticCatalogLoadError: String {
        ru ? "Не удалось загрузить каталог аскез" : "Couldn’t load the ascetics catalog"
    }
    static var trackingEntityWizardAsceticCreatedSuccess: String { ru ? "Аскеза зафиксирована" : "Ascetic contract saved" }
    static var trackingEntityWizardAsceticDirectionLabel: String { ru ? "Направление" : "Direction" }
    static var trackingEntityWizardAsceticDurationContractLabel: String { ru ? "Длительность контракта" : "Contract length" }
    static var trackingEntityWizardAsceticDurationDays14: String { ru ? "14 дней" : "14 days" }
    static var trackingEntityWizardAsceticDurationDays21: String { ru ? "21 день" : "21 days" }
    static var trackingEntityWizardAsceticDurationDays30: String { ru ? "30 дней" : "30 days" }
    static var trackingEntityWizardAsceticDurationDays7: String { ru ? "7 дней" : "7 days" }
    static var trackingEntityWizardAsceticDurationOpen: String { ru ? "Без срока" : "Open-ended" }
    static var trackingEntityWizardAsceticEmptyCategoryHint: String {
        ru ? "В этой категории ничего не нашлось — выбери «Все»." : "Nothing in this category—pick “All”."
    }
    static var trackingEntityWizardAsceticEndOpenHint: String {
        ru ? "Дата окончания не задана — контракт открытый" : "No end date—this is an open contract"
    }
    static var trackingEntityWizardAsceticEndUntil: String { ru ? "До {{date}} включительно" : "Through {{date}} inclusive" }
    static var trackingEntityWizardAsceticKindDesc: String {
        ru ? "Осознанное ограничение по контракту" : "A mindful limit with a contract"
    }
    static var trackingEntityWizardAsceticKindTitle: String { ru ? "Аскеза" : "Ascetic" }
    static var trackingEntityWizardBack: String { ru ? "Назад" : "Back" }
    static var trackingEntityWizardCategoryLabel: String { ru ? "Категория" : "Category" }
    static var trackingEntityWizardCreateCta: String { ru ? "Создать" : "Create" }
    static var trackingEntityWizardCustomVariantLabel: String { ru ? "Свой вариант" : "Your wording" }
    static var trackingEntityWizardGoalCreatedSuccess: String { ru ? "Цель добавлена" : "Goal added" }
    static var trackingEntityWizardGoalKindDesc: String {
        ru ? "Фокус на неделю или месяц, шаги в календаре" : "Week or month focus with steps on the calendar"
    }
    static var trackingEntityWizardGoalKindTitle: String { ru ? "Цель" : "Goal" }
    static var trackingEntityWizardHabitCreatedSuccess: String { ru ? "Привычка создана" : "Habit created" }
    static var trackingEntityWizardHabitKindDesc: String {
        ru ? "Повторяющееся действие с ритмом день/неделя" : "A repeating action with a day/week rhythm"
    }
    static var trackingEntityWizardHabitKindTitle: String { ru ? "Привычка" : "Habit" }
    static var trackingEntityWizardHabitWeeklyTargetLabel: String { ru ? "Раз в неделю (цель)" : "Times per week (target)" }
    static var trackingEntityWizardHabitWeeklyTimes: String { ru ? "{{n}} раз" : "{{n}}×" }
    static var trackingEntityWizardLoadingAsceticCatalog: String { ru ? "Загрузка каталога…" : "Loading catalog…" }
    static var trackingEntityWizardNeedTitleOrPick: String {
        ru ? "Введите название или выберите вариант" : "Enter a name or pick a suggestion"
    }
    static var trackingEntityWizardNextTimings: String { ru ? "Дальше: сроки" : "Next: timing" }
    static var trackingEntityWizardPeriodLabel: String { ru ? "Период" : "Period" }
    static var trackingEntityWizardPlaceholderCustomTitle: String {
        ru ? "Коротко сформулируй цель или привычку" : "Short wording for your goal or habit"
    }
    static var trackingEntityWizardRhythmLabel: String { ru ? "Ритм" : "Rhythm" }
    static var trackingEntityWizardSaveFailed: String { ru ? "Не удалось сохранить" : "Couldn’t save" }
    static var trackingEntityWizardSaving: String { ru ? "Сохраняем…" : "Saving…" }
    static var trackingEntityWizardStartLabel: String { ru ? "Старт" : "Start" }
    static var trackingEntityWizardStepPickKind: String { ru ? "Что добавляем?" : "What are you adding?" }
    static var trackingEntityWizardStepPickVariant: String { ru ? "Выбор варианта" : "Pick a variant" }
    static var trackingEntityWizardStepProgress: String { ru ? "Шаг {{step}} из 3" : "Step {{step}} of 3" }
    static var trackingEntityWizardStepTimingsCreate: String { ru ? "Сроки и создание" : "Timing and create" }
    static var trackingEntityWizardMonthFrom: String { ru ? "Месяц (с {{date}})" : "Month (from {{date}})" }
    static var trackingEntityWizardWeekFrom: String { ru ? "Неделя (с {{date}})" : "Week (from {{date}})" }
    // MARK: Веб `TrackerView` / модалка «Сегодня»
    static var trackingViewAddAsceticCta: String { ru ? "+ Аскеза" : "+ Ascetic" }
    static var trackingViewAddGoalCta: String { ru ? "+ Цель" : "+ Goal" }
    static var trackingViewAddHabitCta: String { ru ? "+ Привычка" : "+ Habit" }
    static var trackingViewAddToTrackerBody: String {
        ru
            ? "Выбери тип сущности, вариант из подборки и сроки — создание здесь же, без других страниц."
            : "Pick a type, a suggestion, and timing—everything is created here, no extra pages."
    }
    static var trackingViewAddToTrackerTitle: String { ru ? "Добавить на карту" : "Add to map" }
    static var trackingViewAsceticsHintTapDays: String { ru ? "· жми по дням ниже" : "· tap the days below" }
    static var trackingViewAttentionSectionTitle: String { ru ? "Требует внимания" : "Needs attention" }
    static var trackingViewBestSectionTitle: String { ru ? "Лучше всего идёт" : "Going best" }
    static var trackingViewCompleteGoalConfirm: String {
        ru
            ? "Отметить цель выполненной? Новые шаги по ней отмечать не получится."
            : "Mark this goal complete? You won’t be able to log new steps on it."
    }
    static var trackingViewContractHereCta: String { ru ? "зафиксировать контракт здесь" : "set up a contract here" }
    static var trackingViewCreateAsceticCta: String { ru ? "добавить аскезу" : "add an ascetic" }
    static var trackingViewCreateGoalCta: String { ru ? "создать цель" : "create a goal" }
    static var trackingViewCreateHabitCta: String { ru ? "создать привычку" : "create a habit" }
    static var trackingViewCreateHereCta: String { ru ? "создать здесь" : "create here" }
    static var trackingViewEmptyAsceticsLead: String { ru ? "Нет аскез —" : "No ascetics —" }
    static var trackingViewEmptyGoalsLead: String { ru ? "Нет целей —" : "No goals —" }
    static var trackingViewEmptyHabitsLead: String { ru ? "Нет привычек —" : "No habits —" }
    static var trackingViewFlowTodayEyebrow: String { ru ? "Flow сегодня" : "Flow today" }
    static var trackingViewFreeSoftLimitHint: String {
        ru
            ? "Для FREE рекомендуем до {{goals}} цели, {{habits}} привычек и {{ascetics}} аскезы — так проще удержать ритм."
            : "On FREE we recommend up to {{goals}} goal, {{habits}} habits, and {{ascetics}} ascetics—it’s easier to keep rhythm."
    }
    static var trackingViewGoalCompletedSuffix: String { ru ? " · завершена" : " · completed" }
    static var trackingViewGoalNameAriaLabel: String { ru ? "Название цели" : "Goal title" }
    static var trackingViewGoalStatusPrefix: String { ru ? "Статус:" : "Status:" }
    static var trackingViewHabitNameAriaLabel: String { ru ? "Название привычки" : "Habit name" }
    static var trackingViewHabitPauseCta: String { ru ? "пауза" : "pause" }
    static var trackingViewHabitPausedSuffix: String { ru ? " (на паузе)" : " (paused)" }
    static var trackingViewHabitResumeCta: String { ru ? "включить" : "resume" }
    static var trackingViewLimitsHint: String {
        ru
            ? "Слишком много активного — удержать будет сложно. Подумай, что поставить на паузу."
            : "Too much active at once—hard to sustain. Consider pausing something."
    }
    static var trackingViewLast30DaysLegend: String {
        ru ? "Последние 30 дней · ● выполнено · ○ нет · ⚠ срыв / нарушение" : "Last 30 days · ● done · ○ none · ⚠ slip / break"
    }
    static var trackingViewMarkTodayPromptAfterDate: String {
        ru ? "— отметь сегодня по каждой сущности." : "— log today for each entity."
    }
    static var trackingViewNoActiveItemsLead: String { ru ? "Нет активных —" : "None active —" }
    static var trackingViewOpenTodayLink: String { ru ? "Открыть «Сегодня»" : "Open Today" }
    static var trackingViewPracticeAggregatedFootnote: String {
        ru
            ? "Отметки по отдельным практикам из каталога попадают в эту линию автоматически."
            : "Marks from individual catalog practices roll into this line automatically."
    }
    static var trackingViewPracticeAggregatedIntro: String {
        ru
            ? "Одна агрегированная линия: всё, что отмечено как практика за день. Детали — в разделе практик."
            : "One aggregated line: everything logged as practice for the day. Details live in Practices."
    }
    static var trackingViewRenameTitleLink: String { ru ? "название" : "rename" }
    static var trackingViewSystemPracticeToday: String { ru ? "Системная практика сегодня" : "System practice today" }
    static var trackingViewTodayLinkHint: String {
        ru
            ? "После отметок сущности попадают в «Сегодня» как шаги дня (связка onTodayActionComplete — на стороне Today)."
            : "After check-ins, entities show up in Today as day steps (onTodayActionComplete wiring lives on the Today side)."
    }
    static var trackingViewWizardFromTypeStep: String { ru ? "Мастер (с шага типа)" : "Wizard (from type step)" }
    static var trackingToastAsceticLogError: String { ru ? "Не удалось сохранить отметку аскезы." : "Couldn’t save ascetic check-in." }
    static var trackingToastGoalCompleteError: String { ru ? "Не удалось завершить цель." : "Couldn’t complete the goal." }
    static var trackingToastGoalCompleteSuccess: String { ru ? "Цель отмечена выполненной." : "Goal marked complete." }
    static var trackingToastGoalNameEmpty: String { ru ? "Название не может быть пустым." : "Title can’t be empty." }
    static var trackingToastGoalRenameError: String { ru ? "Не удалось сохранить название." : "Couldn’t save the title." }
    static var trackingToastGoalRenameSuccess: String { ru ? "Название цели обновлено." : "Goal title updated." }
    static var trackingToastGoalStepDuplicate: String {
        ru ? "Шаг по этой цели за этот день уже отмечен." : "This goal already has a step logged for that day."
    }
    static var trackingToastGoalStepError: String { ru ? "Не удалось отметить шаг по цели." : "Couldn’t log the goal step." }
    static var trackingToastHabitActive: String { ru ? "Привычка снова активна." : "Habit is active again." }
    static var trackingToastHabitPaused: String { ru ? "Привычка на паузе." : "Habit paused." }
    static var trackingToastHabitRenameSuccess: String { ru ? "Название привычки обновлено." : "Habit name updated." }
    static var trackingToastHabitSaveError: String { ru ? "Не удалось сохранить привычку." : "Couldn’t save habit." }
    static var trackingToastHabitUpdateError: String { ru ? "Не удалось обновить привычку." : "Couldn’t update habit." }
    static var trackingToastPracticeSaveError: String { ru ? "Ошибка при сохранении практики." : "Error saving practice." }
    static var trackingToastPracticeUncheckBlocked: String {
        ru
            ? "Снять отметку практики из календаря пока нельзя — правь в разделе практик."
            : "You can’t remove a practice mark from the calendar yet—change it in Practices."
    }
    static var weekdayFallback: [String] {
        ru
            ? ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            : ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    }

    static func streakTitle(for key: String) -> String {
        switch key {
        case "goal": return ru ? "Цели" : "Goals"
        case "state_phases": return ru ? "Отметки" : "Check-ins"
        case "practice": return ru ? "Практики" : "Practices"
        case "habits": return ru ? "Привычки" : "Habits"
        case "daily_signals": return ru ? "Сигналы" : "Signals"
        case "ritual": return ru ? "Ритуал" : "Ritual"
        case "diary": return ru ? "Дневник" : "Journal"
        case "affirmation": return ru ? "Аффирмации" : "Affirmations"
        default: return key.replacingOccurrences(of: "_", with: " ").capitalized
        }
    }

    static var goalsNavTitle: String { ru ? "Цели" : "Goals" }
    static var syncIssueTitle: String { ru ? "Проблема синхронизации" : "Sync issue" }
    static var stepsForDay: String { ru ? "Шаги для этого дня" : "Steps for this day" }
    static var goalsPickDateHint: String {
        ru
            ? "Выбери дату на вкладке «Календарь», затем отметь шаг цели для этого дня."
            : "Pick a date on the Calendar tab, then log a goal step for that day."
    }
    static var newGoal: String { ru ? "Новая цель" : "New goal" }
    static func weekFrom(_ date: String) -> String { ru ? "Неделя с \(date)" : "Week from \(date)" }
    static func monthFrom(_ date: String) -> String { ru ? "Месяц с \(date)" : "Month from \(date)" }
    static var goalLimitReached: String {
        ru ? "Уже 3 цели на этот период — заверши или смени период." : "Already 3 goals for this period—finish one or switch period."
    }
    // MARK: Веб heatmap `/tracking/calendar` (`CalendarHeatmap`)
    static var heatmapDrillAsceticsLinePrefix: String { ru ? "Аскезы (удержано):" : "Ascetics (held):" }
    static var heatmapDrillDayEyebrow: String { ru ? "День" : "Day" }
    static var heatmapDrillGoalsLinePrefix: String { ru ? "Цели:" : "Goals:" }
    static var heatmapDrillHabitsLinePrefix: String { ru ? "Привычки:" : "Habits:" }
    static var heatmapDrillPracticeDone: String { ru ? "выполнена" : "done" }
    static var heatmapDrillPracticeLabel: String { ru ? "Практика:" : "Practice:" }
    static var heatmapDrillPracticeNo: String { ru ? "нет" : "no" }
    static var heatmapDrillTotalsPrefix: String { ru ? "Всего по трекам:" : "Total across tracks:" }
    static var heatmapDrillDayCaptionEmptyTracks: String {
        ru
            ? "Нет активных треков — добавь цель, привычку или аскезу."
            : "No active tracks—add a goal, habit, or ascetic."
    }
    static var heatmapDrillDayCaptionGoalsNoStep: String {
        ru
            ? "Не было шага по целям — имеет смысл один конкретный шаг по выбранной цели."
            : "No goal step that day—try one concrete step on a chosen goal."
    }
    static var heatmapDrillDayCaptionPartialDay: String {
        ru
            ? "Частично закрыто — видно, куда ещё можно добить."
            : "Partly closed—you can still see where to push."
    }
    static var heatmapDrillDayCaptionQuietDay: String {
        ru ? "Слабый день — почти без движения по трекам." : "Quiet day—almost no movement on tracks."
    }
    static var heatmapDrillDayCaptionStrongDay: String {
        ru ? "Плотный день — хорошая опора по трекам." : "Dense day—solid footing on tracks."
    }
    static var heatmapEntityPickHint: String {
        ru
            ? "Выбери сущность в списке — иначе показывается сводно по типу."
            : "Pick an entity from the list—or the view stays aggregated by type."
    }
    static var heatmapEntityPickPlaceholder: String { ru ? "Выбери…" : "Choose…" }
    static var heatmapUnderMapInsightAllFreeGaps: String {
        ru
            ? "Есть провалы в сетке — это нормально, если заметить их."
            : "There are gaps in the grid—that’s fine if you notice them."
    }
    static var heatmapUnderMapInsightAllFreeSteady: String {
        ru
            ? "Ритм в целом ровный по выбранному фильтру."
            : "Overall rhythm looks steady for the selected filter."
    }
    static var heatmapUnderMapInsightAllPremiumReadable: String {
        ru
            ? "Паттерн месяца читается: видно, где ты набираешь плотность."
            : "The month pattern reads—you can see where density builds."
    }
    static var heatmapUnderMapInsightAllPremiumStutter: String {
        ru
            ? "Ты держишься несколько дней, затем проседаешь — нет устойчивого ритма на весь месяц."
            : "You hold for a few days, then drop—no steady rhythm for the whole month."
    }
    static var heatmapUnderMapInsightAllProSteady: String {
        ru ? "Картина относительно ровная — мало резких провалов." : "Relatively smooth—few sharp drops."
    }
    static var heatmapUnderMapInsightAllProVolatile: String {
        ru
            ? "Ритм нестабильный: плотные дни чередуются с пустыми."
            : "Uneven rhythm: dense days alternate with empty ones."
    }
    static var heatmapUnderMapInsightAsceticsFreeGaps: String {
        ru ? "По аскезам есть дни без удержания." : "Ascetics have days without holding the line."
    }
    static var heatmapUnderMapInsightAsceticsFreeSteady: String {
        ru ? "По аскезам плотность выше." : "Ascetics look denser."
    }
    static var heatmapUnderMapInsightAsceticsPremium: String {
        ru
            ? "Если после насыщенных зон идёт резкий спад — правило может быть жёстким."
            : "If a rich stretch is followed by a sharp drop—the rule may be too harsh."
    }
    static var heatmapUnderMapInsightAsceticsPro: String {
        ru
            ? "Срывы видны как пустые или очень светлые клетки подряд."
            : "Slips show up as empty or very light cells in a row."
    }
    static var heatmapUnderMapInsightGoalsFreeGaps: String {
        ru ? "По целям есть дни без шага." : "Goals have days with no step."
    }
    static var heatmapUnderMapInsightGoalsFreeSteady: String {
        ru ? "По целям движение заметнее." : "Goal movement is more visible."
    }
    static var heatmapUnderMapInsightGoalsPremium: String {
        ru
            ? "Ты не двигаешься по целям регулярно — нет ежедневных шагов; упрости до одного шага в день."
            : "Goals aren’t moving daily—simplify to one step a day."
    }
    static var heatmapUnderMapInsightGoalsPro: String {
        ru ? "Цели без ежедневных шагов дают «рваную» сетку." : "Goals without daily steps make a “patchy” grid."
    }
    static var heatmapUnderMapInsightHabitsFreeGaps: String {
        ru ? "По привычкам есть светлые дни." : "Habits have lighter days."
    }
    static var heatmapUnderMapInsightHabitsFreeSteady: String {
        ru ? "Привычки выглядят стабильнее." : "Habits look more stable."
    }
    static var heatmapUnderMapInsightHabitsPremium: String {
        ru
            ? "Поведенческий слой: выходные или конец недели часто светлее — проверь триггеры."
            : "Behavior layer: weekends or end of week are often lighter—check triggers."
    }
    static var heatmapUnderMapInsightHabitsPro: String {
        ru
            ? "Привычки могут быть не закреплены — смотри на «дырявые» недели."
            : "Habits may not be locked in—watch for “holey” weeks."
    }
    static var heatmapUnderMapInsightPracticesFreeGaps: String {
        ru ? "Системные практики не закрываются каждый день." : "System practices aren’t closed every day."
    }
    static var heatmapUnderMapInsightPracticesFreeSteady: String {
        ru ? "Практики чаще отмечены." : "Practices are logged more often."
    }
    static var heatmapUnderMapInsightPracticesPremium: String {
        ru
            ? "Сравни с ALL: если практики ровные, а ALL рваный — упор на цели и привычки."
            : "Compare with ALL: if practices are steady but ALL is patchy—focus goals and habits."
    }
    static var heatmapUnderMapInsightPracticesPro: String {
        ru
            ? "Практика одна на день — сетка показывает дисциплину «да/нет»."
            : "One practice per day—the grid shows yes/no discipline."
    }
    static var heatmapFilterGoalsRowTitle: String {
        ru ? "Цели (пусто = все активные)" : "Goals (empty = all active)"
    }
    static var heatmapInsightPrefix: String { ru ? "Инсайт" : "Insight" }
    static var heatmapJumpToCurrentMonth: String { ru ? "К текущему" : "This month" }
    static var heatmapLegendEntityDone: String { ru ? "сделано" : "done" }
    static var heatmapLegendEntityMiss: String { ru ? "нет" : "none" }
    static var heatmapLegendIntensity0: String { ru ? "0%" : "0%" }
    static var heatmapLegendIntensityHigh: String { ru ? "70–100%" : "70–100%" }
    static var heatmapLegendIntensityLow: String { ru ? "1–30%" : "1–30%" }
    static var heatmapLegendIntensityMid: String { ru ? "30–70%" : "30–70%" }
    static var heatmapLegendNoData: String { ru ? "нет данных" : "no data" }
    static var heatmapMapExplainer: String {
        ru
            ? "Один день — одна клетка, цвет = доля закрытых активных треков (ALL) или выбранного типа. Серый — нет данных или будущее. Без цифр внутри."
            : "One day, one cell—color shows the share of closed active tracks (ALL) or the selected type. Gray means no data or a future day. No numbers inside cells."
    }
    static var heatmapModeAll: String { "ALL" }
    static var heatmapNextMonthA11y: String { ru ? "Следующий месяц" : "Next month" }
    static var heatmapPrevMonthA11y: String { ru ? "Предыдущий месяц" : "Previous month" }
    static var heatmapRowModeAggregate: String { ru ? "Сводно (доля)" : "Aggregate (share)" }
    static var heatmapRowModeLabel: String { ru ? "Режим строки:" : "Row mode:" }
    static var heatmapRowModeOneEntity: String { ru ? "Одна сущность" : "One entity" }
    static var heatmapSelectAllShort: String { ru ? "все" : "all" }
    static var heatmapUnderMapEyebrowPrefix: String { ru ? "Под картой" : "Under the map" }

    static var horizonPicker: String { ru ? "Горизонт" : "Horizon" }
    static var yourGoals: String { ru ? "Твои цели" : "Your goals" }
    static var noGoalsYet: String { ru ? "Пока нет целей — создай выше." : "No goals yet—create one above." }
    static var done: String { ru ? "Сделано" : "Done" }
    static var markStep: String { ru ? "Отметить шаг" : "Log step" }
    static var reopenGoal: String { ru ? "Снова в работе" : "Reopen" }
    static var completeGoal: String { ru ? "Завершить" : "Complete" }
    static var openCalendarForDay: String {
        ru ? "Открыть календарь для отметок дня" : "Open calendar for day entries"
    }
    static var goalQuickPeriodNote: String {
        ru ? "Период привязан к выбранному дню в календаре Flow — как на сайте." : "Period follows the day selected in Flow calendar—same as the site."
    }
    static var asceticLoadingCatalog: String { ru ? "Загружаю каталог…" : "Loading catalog…" }
    static var asceticCatalogEmpty: String { ru ? "Каталог аскез пуст или недоступен." : "Ascetic catalog is empty or unavailable." }
    static var asceticDurationSection: String { ru ? "Срок" : "Duration" }
    /// Подпись для `Picker` доступности.
    static var asceticDurationPicker: String { asceticDurationSection }
    static var asceticPracticeSection: String { ru ? "Практика" : "Practice" }
    static var createContract: String { ru ? "Создать контракт" : "Create contract" }
    static var asceticNavTitle: String { ru ? "Аскеза" : "Ascetic" }
    static var asceticFallbackTitle: String { asceticNavTitle }

    static func asceticDurationTitle(for raw: String) -> String {
        switch raw {
        case "open": return ru ? "Без фиксированного срока" : "No fixed end"
        case "d7": return ru ? "7 дней" : "7 days"
        case "d14": return ru ? "14 дней" : "14 days"
        case "d21": return ru ? "21 день" : "21 days"
        case "d30": return ru ? "30 дней" : "30 days"
        default: return raw
        }
    }
}

// MARK: - Practices tab

enum PracticesExperienceChromeCopy {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var loadingPractices: String { ru ? "Загружаю практики…" : "Loading practices…" }
    static var sequencesTitle: String { ru ? "Серии практик" : "Practice sequences" }
    static var sequencesSubtitle: String {
        ru
            ? "Пошаговые недельные треки — те же данные, что `GET /practices/sequences`."
            : "Weekly step tracks—same data as `GET /practices/sequences`."
    }
    static var catalogSection: String { ru ? "Каталог" : "Catalog" }
    static var emptyFiltered: String { ru ? "Пока нет практик по выбранным фильтрам." : "No practices match these filters." }
    static var navPractices: String { ru ? "Практики" : "Practices" }
    static var a11yHistory: String { ru ? "История практик" : "Practice history" }
    static var a11yRefresh: String { ru ? "Обновить" : "Refresh" }
    static var nativeHubTitle: String { ru ? "Нативный хаб" : "Native hub" }
    static var nativeHubBody: String {
        ru
            ? "Все основные вызовы `/practices/*` подключены; оформление экранов можно донастроить отдельно."
            : "Core `/practices/*` calls are wired; UI polish can follow."
    }
    static var filtersTitle: String { ru ? "Фильтры" : "Filters" }
    static var categoryLabel: String { ru ? "Категория" : "Category" }
    static var forYouNow: String { ru ? "Сейчас для тебя" : "For you now" }
    static var shortAlternatives: String { ru ? "Короткие альтернативы" : "Short alternatives" }
    static var shortAlternativesSubtitle: String {
        ru ? "Подбор коротких практик под твой запрос" : "Short practices matched to your request"
    }
    static var asceticsBlock: String { ru ? "Аскезы" : "Ascetics" }
    static var asceticsSubtitle: String { ru ? "Практики сдержанности из каталога" : "Restraint practices from the catalog" }
    static var affirmationsApi: String { ru ? "Аффирмации (API практик)" : "Affirmations (practices API)" }
    static var affirmationsSubtitle: String {
        ru ? "До 25 аффирмаций из подборки практик" : "Up to 25 affirmations from the practice set"
    }
    static var interpretationTitle: String { ru ? "Смысл и практика дня" : "Meaning and practice of the day" }
    static func dayLine(_ day: Int) -> String { ru ? "День \(day)" : "Day \(day)" }
    static var openPractice: String { ru ? "Открыть практику" : "Open practice" }
    static var weeklyLimitTitle: String { ru ? "Лимит на неделю" : "Weekly limit" }
    static var planLabel: String { ru ? "План" : "Plan" }
    static var personalizedLine: String { ru ? "Персональные практики" : "Personalized practices" }
    static var remainingLabel: String { ru ? "Осталось" : "Left" }
    static var unlimitedShort: String { ru ? "без ограничений" : "unlimited" }
    static func usedCount(_ n: Int) -> String { ru ? "использовано \(n)" : "used \(n)" }
    static func weekWith(_ date: String) -> String { ru ? "Неделя с \(date)" : "Week of \(date)" }

    static var filterAll: String { ru ? "Все" : "All" }
    static var filterDaily: String { ru ? "Ежедневные" : "Daily" }
    static var filterWeekly: String { ru ? "Недельные" : "Weekly" }
    static var filterMonthly: String { ru ? "Месячные" : "Monthly" }
    static var filterCycle: String { ru ? "Цикличные" : "Cyclic" }
    static var durationAny: String { ru ? "Любая" : "Any" }
    static var durationShort: String { ru ? "1–5 мин" : "1–5 min" }
    static var durationMedium: String { ru ? "6–10 мин" : "6–10 min" }
    static var durationLong: String { ru ? "10+ мин" : "10+ min" }

    static var loadingHistory: String { ru ? "Загружаю историю…" : "Loading history…" }
    static var historyProgressTitle: String { ru ? "История и прогресс" : "History and progress" }
    static var historyProgressSubtitle: String {
        ru
            ? "Те же данные, что на вебе: `GET /practices/history`, `GET /practices/progress`."
            : "Same as web: `GET /practices/history`, `GET /practices/progress`."
    }
    static var navHistory: String { ru ? "История" : "History" }
    static var emptyHistoryTitle: String { ru ? "Пока нет истории" : "No history yet" }
    static var emptyHistoryBody: String {
        ru
            ? "Начни выполнять практики с вкладки «Практики», чтобы видеть прогресс здесь."
            : "Complete practices from the Practices tab to see progress here."
    }
    static var toCatalog: String { ru ? "К каталогу практик" : "Back to catalog" }
    static var statistics: String { ru ? "Статистика" : "Statistics" }
    static var statTotalDone: String { ru ? "Всего выполнено" : "Total completed" }
    static var statPersonalized: String { ru ? "Персонализированных" : "Personalized" }
    static var statCurrentStreak: String { ru ? "Текущая серия" : "Current streak" }
    static var statBestStreak: String { ru ? "Лучшая серия" : "Best streak" }
    static var statWeeksActive: String { ru ? "Недель активно" : "Active weeks" }
    static var byCategory: String { ru ? "По категориям" : "By category" }
    static func practicesCount(_ n: Int) -> String { ru ? "\(n) практик" : "\(n) practices" }
    static var completedPractices: String { ru ? "Выполненные практики" : "Completed practices" }
    static var forYouBadge: String { ru ? "Для тебя" : "For you" }
    static func sequenceStep(_ step: Int) -> String { ru ? "Серия · шаг \(step)" : "Sequence · step \(step)" }
    static var repeatCta: String { ru ? "Повторить" : "Repeat" }
    static var seriesBadge: String { ru ? "Серия" : "Series" }
    static var minutesShort: String { ru ? "мин" : "min" }
    static var audioSection: String { ru ? "Аудио" : "Audio" }
    static var hintSection: String { ru ? "Подсказка" : "Hint" }
    static var stepsSection: String { ru ? "Шаги" : "Steps" }
    static func stepLine(_ n: Int, _ title: String) -> String { ru ? "Шаг \(n). \(title)" : "Step \(n). \(title)" }
    static var howToSection: String { ru ? "Как сделать" : "How to do it" }
    static var reflectionSection: String { ru ? "Вопросы для рефлексии" : "Reflection prompts" }
    static var relatedSection: String { ru ? "Связанные практики" : "Related practices" }
    static var sequenceComplete: String {
        ru ? "Серия завершена — шаги сохранены в истории." : "Sequence complete—steps saved to history."
    }
    static var saving: String { ru ? "Сохраняю…" : "Saving…" }
    static func completeStep(_ n: Int) -> String { ru ? "Завершить шаг \(n)" : "Complete step \(n)" }
    static var markComplete: String { ru ? "Отметить выполненной" : "Mark complete" }
    static var savedToHistory: String { ru ? "Сохранено в истории практик." : "Saved to practice history." }
    static var sequenceProgressTitle: String { ru ? "Прогресс по серии" : "Sequence progress" }
    static var stepsDoneLabel: String { ru ? "Выполнено шагов" : "Steps done" }
    static func nextStep(_ name: String) -> String { ru ? "Следующий шаг: \(name)" : "Next: \(name)" }
    static var practiceFallbackTitle: String { ru ? "Практика" : "Practice" }

    static func daysStreak(_ days: Int) -> String {
        if days == 0 { return ru ? "0 дней" : "0 days" }
        if !ru {
            return days == 1 ? "1 day" : "\(days) days"
        }
        let n = abs(days) % 100
        let last = n % 10
        let word: String
        if last == 1, n != 11 {
            word = "день"
        } else if (2 ... 4).contains(last), !(12 ... 14).contains(n) {
            word = "дня"
        } else {
            word = "дней"
        }
        return "\(days) \(word)"
    }

    static func categoryDisplay(_ raw: String) -> String {
        switch raw.lowercased() {
        case "meditation": return ru ? "Медитация" : "Meditation"
        case "breathing": return ru ? "Дыхание" : "Breathing"
        case "gratitude": return ru ? "Благодарность" : "Gratitude"
        case "affirmation": return ru ? "Аффирмация" : "Affirmation"
        case "ritual": return ru ? "Ритуал" : "Ritual"
        case "reflection": return ru ? "Рефлексия" : "Reflection"
        case "emotional", "emotions": return ru ? "Эмоции" : "Emotions"
        case "focus": return ru ? "Фокус" : "Focus"
        default: return raw.capitalized
        }
    }

    static func difficultyDisplay(_ raw: String) -> String {
        switch raw.lowercased() {
        case "easy", "beginner": return ru ? "Лёгкая" : "Easy"
        case "medium", "intermediate": return ru ? "Средняя" : "Medium"
        case "hard", "advanced": return ru ? "Сложная" : "Hard"
        default: return raw.capitalized
        }
    }

    static var errorPractice403Head: String {
        ru ? "Доступ к этой практике сейчас недоступен (403)." : "This practice isn’t available right now (403)."
    }
    static var errorPractice403Tail: String {
        ru
            ? "На вкладке «Практики» открой карточку «Лимит на неделю» — там остаток персональных практик на неделю и тариф."
            : "On the Practices tab, open the Weekly limit card—remaining personalized practices and your plan are there."
    }

    static var practicesCatalogBack: String { ru ? "← Назад" : "← Back" }
    static var practicesCatalogChooseDirection: String { ru ? "Выбери направление" : "Choose a direction" }
    static var practicesCatalogDifficultyAdvanced: String { ru ? "Продвинутый" : "Advanced" }
    static var practicesCatalogDifficultyBeginner: String { ru ? "Начинающий" : "Beginner" }
    static var practicesCatalogDifficultyIntermediate: String { ru ? "Средний" : "Intermediate" }
    static var practicesCatalogDurationBadgeAny: String { ru ? "Любая" : "Any" }
    static var practicesCatalogDurationBadgeLong: String { ru ? "Длинная" : "Long" }
    static var practicesCatalogDurationBadgeMedium: String { ru ? "Средняя" : "Medium" }
    static var practicesCatalogDurationBadgeShort: String { ru ? "Короткая" : "Short" }
    static var practicesCatalogDurationPickAnyHint: String { ru ? "Показывать весь каталог" : "Show the full catalog" }
    static var practicesCatalogDurationPickAnyLabel: String { ru ? "Неважно" : "No preference" }
    static var practicesCatalogDurationPickLongHint: String { ru ? "10+ минут и последовательности" : "10+ minutes and sequences" }
    static var practicesCatalogDurationPickLongLabel: String { ru ? "Длинные" : "Long" }
    static var practicesCatalogDurationPickMediumHint: String { ru ? "6–10 минут" : "6–10 minutes" }
    static var practicesCatalogDurationPickMediumLabel: String { ru ? "Средние" : "Medium" }
    static var practicesCatalogDurationPickShortHint: String { ru ? "1–5 минут" : "1–5 minutes" }
    static var practicesCatalogDurationPickShortLabel: String { ru ? "Короткие" : "Short" }
    static var practicesCatalogEmptyFilter: String {
        ru
            ? "В этом фильтре нет практик. Попробуй выбрать другой формат."
            : "No practices in this filter. Try another format."
    }
    static var practicesCatalogFormatLabel: String { ru ? "Формат практики" : "Practice format" }
    static var practicesCatalogGoalPrompt: String { ru ? "Какую цель ты хочешь достичь?" : "What do you want to work toward?" }
    static var practicesCatalogLoadError: String { ru ? "Не удалось загрузить практики" : "Couldn’t load practices" }
    static var practicesCatalogLongMorningBody: String {
        ru
            ? "Если тебе ближе не микро-паузы, а более длинная медитация, ходьба или целая последовательность, теперь это можно явно выбирать прямо в каталоге."
            : "If you prefer more than micro-pauses—longer meditation, walking, or a full sequence—you can choose that explicitly in the catalog."
    }
    static var practicesCatalogLongMorningTitle: String { ru ? "Длинные утренние форматы" : "Longer morning formats" }
    static var practicesCatalogMusicBody: String {
        ru
            ? "Следующий слой для расширения уже очевиден: отдельные медитации и музыка для практики. Сейчас каталог подготовлен так, чтобы этот слой можно было встроить естественно."
            : "The next layer is clear: dedicated meditations and music for practice. The catalog is structured so that layer can land naturally."
    }
    static var practicesCatalogMusicTitle: String { ru ? "Музыка и медитации" : "Music and meditations" }
    static var practicesCatalogOtherPractices: String { ru ? "Другие практики в этом направлении" : "More practices in this direction" }
    static var practicesCatalogPageSubtitle: String {
        ru
            ? "Практики для осознанного развития. Выбери цель и направление, и мы подберем формат, который лучше встраивается в твой ритм."
            : "Practices for mindful growth. Pick a goal and direction, and we’ll suggest a format that fits your rhythm."
    }
    static var practicesCatalogPageTitle: String { ru ? "Практики" : "Practices" }
    static var practicesCatalogPeriodicityBadgeCycle: String { ru ? "Цикличная" : "Cyclic" }
    static var practicesCatalogPeriodicityBadgeDaily: String { ru ? "Ежедневная" : "Daily" }
    static var practicesCatalogPeriodicityBadgeMonthly: String { ru ? "Месячная" : "Monthly" }
    static var practicesCatalogPeriodicityBadgeWeekly: String { ru ? "Недельная" : "Weekly" }
    static var practicesCatalogPersonalizedWhyPrefix: String { ru ? "Почему эта практика:" : "Why this practice:" }
    static var practicesCatalogPracticeForYou: String { ru ? "Практика для тебя" : "A practice for you" }
    static var practicesCatalogStartPractice: String { ru ? "Начать практику" : "Start practice" }
    static var practicesCatalogTimeQuestion: String {
        ru ? "Сколько времени ты реально готов дать этой практике?" : "How much time can you honestly give this practice?"
    }
    static var practicesCatalogWizardStepDirection: String { ru ? "Направление" : "Direction" }
    static var practicesCatalogWizardStepGoal: String { ru ? "Цель" : "Goal" }
    static var practicesCatalogWizardStepPractice: String { ru ? "Практика" : "Practice" }
    static var practicesCatalogTodayLabel: String { ru ? "Сегодня" : "Today" }
    static var practicesCatalogProgressOf: String { ru ? "из" : "of" }
    static var practicesCatalogCategoriesAria: String { ru ? "Категории практик" : "Practice categories" }
    static var practicesCatalogTabAll: String { ru ? "Все" : "All" }
    static var practicesCatalogTabBreath: String { ru ? "Дыхание" : "Breath" }
    static var practicesCatalogTabMeditation: String { ru ? "Медитации" : "Meditations" }
    static var practicesCatalogTabAffirmation: String { ru ? "Аффirmации" : "Affirmations" }
    static var practicesCatalogTabAscetic: String { ru ? "Аскезы" : "Ascetics" }
    static var practicesCatalogMinutesShort: String { ru ? "мин" : "min" }
    static var practicesCatalogPersonalizedBadge: String { ru ? "Персонально для тебя" : "Personalized for you" }
    static var practicesCatalogWizardStepsAria: String { ru ? "Шаги подбора практики" : "Practice selection steps" }
    static var practicesRailMyStreak: String { ru ? "Моя серия" : "My streak" }
    static var practicesRailActiveCount: String { ru ? "Активных практик:" : "Active practices:" }
    static var practicesRailBestStreak: String { ru ? "Лучший результат:" : "Best streak:" }
    static var practicesRailWeeklyRhythm: String { ru ? "Недельный ритм" : "Weekly rhythm" }
    static var practicesRailDaysSuffix: String { ru ? "дней" : "days" }

    static var practiceDetailAccessFree: String { ru ? "Бесплатно" : "Free" }
    static var practiceDetailAccessSubscription: String { ru ? "По подписке" : "Subscription" }
    static var practiceDetailAudioUnsupported: String {
        ru ? "Ваш браузер не поддерживает аудио." : "Your browser does not support audio."
    }
    static var practiceDetailAuthOnlyTitle: String {
        ru
            ? "Эта практика доступна только для зарегистрированных пользователей"
            : "This practice is only available for signed-in users"
    }
    static var practiceDetailBackLink: String { ru ? "← Вернуться к практикам" : "← Back to practices" }
    static var practiceDetailBackToPracticesCta: String { ru ? "Вернуться к практикам" : "Back to practices" }
    static var practiceDetailCompleteErrorFallback: String { ru ? "Ошибка при отметке практики" : "Couldn’t mark the practice complete" }
    static var practiceDetailCompletedFallbackBody: String { ru ? "Практика завершена." : "Practice completed." }
    static func practiceDetailCompleteStepCta(n: Int) -> String { ru ? "Завершить шаг \(n)" : "Complete step \(n)" }
    static var practiceDetailCompletionWorkedPattern: String { ru ? "Ты только что поработал с паттерном" : "You just worked with the pattern" }
    static func practiceDetailDurationValue(n: Int) -> String { ru ? "\(n) минут" : "\(n) minutes" }
    static var practiceDetailFreeLimitBody: String {
        ru ? "Зарегистрируйся, чтобы получить доступ ко всем практикам" : "Sign up to access all practices"
    }
    static var practiceDetailFreeLimitTitle: String { ru ? "Лимит бесплатных практик исчерпан" : "You’ve used your free practices" }
    static var practiceDetailHowToTitle: String { ru ? "Как практиковать" : "How to practice" }
    static var practiceDetailJournalFixFeelingCta: String { ru ? "Зафиксировать ощущение →" : "Capture how it felt →" }
    static var practiceDetailMarkCompleteCta: String { ru ? "Отметить как выполненное" : "Mark as done" }
    static var practiceDetailMarkingShort: String { ru ? "Отмечаю..." : "Marking…" }
    static var practiceDetailMetaAccess: String { ru ? "Доступ" : "Access" }
    static var practiceDetailMetaDuration: String { ru ? "Длительность" : "Duration" }
    static var practiceDetailMetaLevel: String { ru ? "Уровень" : "Level" }
    static var practiceDetailNextStepPrefix: String { ru ? "Следующий шаг:" : "Next step:" }
    static var practiceDetailNotFoundTitle: String { ru ? "Практика не найдена" : "Practice not found" }
    static var practiceDetailOpenProfileRewardsCta: String { ru ? "Открыть профиль и награды →" : "Open profile and rewards →" }
    static var practiceDetailPatternExploreCta: String {
        ru ? "Посмотреть, как это связано с тобой →" : "See how this connects to you →"
    }
    static var practiceDetailReflectionQuestionsTitle: String { ru ? "Вопросы для размышления" : "Reflection questions" }
    static var practiceDetailSequenceDoneShort: String { ru ? "✨ Серия завершена!" : "✨ Series complete!" }
    static var practiceDetailSequenceProgressHeading: String { ru ? "Прогресс по серии" : "Series progress" }
    static func practiceDetailSequenceStepsTitle(count: Int) -> String {
        ru ? "Шаги серии (\(count) дней)" : "Series steps (\(count) days)"
    }
    static var practiceDetailSignUpCta: String { ru ? "Зарегистрироваться" : "Sign up" }
    static var practiceDetailStepCompleteErrorFallback: String { ru ? "Ошибка при завершении шага" : "Couldn’t complete the step" }
    static func practiceDetailStepDoneToast(n: Int) -> String { ru ? "Шаг \(n) завершен!" : "Step \(n) complete!" }
    static func practiceDetailStepDurationValue(n: Int) -> String { ru ? "\(n) минут" : "\(n) minutes" }
    static var practiceDetailStepQuestionsLabel: String { ru ? "Вопросы:" : "Questions:" }
    static var practiceDetailTodaysTaskTitle: String { ru ? "Задание на сегодня" : "Today’s prompt" }
    static var practicePatternAxisA1: String { ru ? "Ориентация идентичности" : "Identity orientation" }
    static var practicePatternAxisA2: String { ru ? "Эмоциональная обработка" : "Emotional processing" }
    static var practicePatternAxisA3: String { ru ? "Принятие решений" : "Decision-making" }
    static var practicePatternAxisA4: String { ru ? "Стабильность и изменения" : "Stability and change" }
    static var practicePatternAxisA5: String { ru ? "Ориентация контроля" : "Control orientation" }
    static var practicePatternAxisA6: String { ru ? "Реляционная ориентация" : "Relational orientation" }
    static var practicePatternAxisA7: String { ru ? "Управление энергией" : "Energy management" }

    static var practicesHistoryAuthRequired: String { ru ? "Требуется авторизация" : "Sign in required" }
    static var practicesHistoryBrowseCta: String { ru ? "Перейти к практикам" : "Go to practices" }
    static var practicesHistoryByCategoryHeading: String { ru ? "Прогресс по категориям" : "Progress by category" }
    static var practicesHistoryCategoryAffirmation: String { ru ? "Аффирмация" : "Affirmation" }
    static var practicesHistoryCategoryBreathing: String { ru ? "Дыхание" : "Breathing" }
    static var practicesHistoryCategoryEmotions: String { ru ? "Эмоции" : "Emotions" }
    static var practicesHistoryCategoryFocus: String { ru ? "Фокус" : "Focus" }
    static var practicesHistoryCategoryGratitude: String { ru ? "Благодарность" : "Gratitude" }
    static var practicesHistoryCategoryMeditation: String { ru ? "Медитация" : "Meditation" }
    static var practicesHistoryCategoryOther: String { ru ? "Другое" : "Other" }
    static var practicesHistoryCategoryReflection: String { ru ? "Рефлексия" : "Reflection" }
    static var practicesHistoryCategoryRitual: String { ru ? "Ритуал" : "Ritual" }
    static var practicesHistoryEmptyBody: String {
        ru
            ? "Начните выполнять практики, чтобы отслеживать свой прогресс."
            : "Complete practices to see your progress here."
    }
    static var practicesHistoryEmptyTitle: String {
        ru ? "У вас пока нет истории практик" : "No practice history yet"
    }
    static var practicesHistoryErrorTitle: String { ru ? "Ошибка загрузки" : "Couldn’t load" }
    static var practicesHistoryLoadFailed: String {
        ru ? "Не удалось загрузить данные о практиках" : "Couldn’t load practice data"
    }
    static var practicesHistoryPageSubtitle: String {
        ru ? "Отслеживайте свой прогресс и историю выполненных практик" : "Track your progress and completed practice history"
    }
    static var practicesHistoryPersonalizedBadge: String { ru ? "Персонализированная" : "Personalized" }
    static var practicesHistoryPersonalizedShort: String { ru ? "перс." : "pers." }
    static var practicesHistoryProgressStatsHeading: String { ru ? "Статистика прогресса" : "Progress statistics" }
    static var practicesHistorySectionProgress: String { ru ? "Прогресс" : "Progress" }
    static var practicesHistorySeriesStepLabel: String { ru ? "Серия: шаг" : "Series: step" }
    static var practicesHistoryUnitDay1: String { ru ? "день" : "day" }
    static var practicesHistoryUnitDayN: String { ru ? "дней" : "days" }
    static var practicesHistoryUnitPractice1: String { ru ? "практика" : "practice" }
    static var practicesHistoryUnitPracticeN: String { ru ? "практик" : "practices" }

    static var pickerPeriodicity: String { ru ? "Периодичность" : "Periodicity" }
    static var pickerDuration: String { ru ? "Длительность" : "Duration" }
}

// MARK: - Guidance history (web `/guidance/history`)

enum GuidanceHistoryChromeCopy {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var guidanceHistoryNavHub: String { ru ? "Центр разборов" : "Guidance hub" }
    static var guidanceHistoryBackToday: String { ru ? "← Сегодня" : "← Today" }
    static var guidanceHistoryTitle: String { ru ? "История" : "History" }
    static var guidanceHistoryHeroLead: String {
        ru
            ? "Здесь сохраняются разборы с того же экрана — вопрос, расклад и карты — плюс быстрые ответы без таро и карты дня. Одна лента, чтобы проще замечать повторяющиеся темы."
            : "Readings from the same screen—your question, spread, and cards—plus quick answers without tarot and your card-of-the-day draws. One feed to spot recurring themes."
    }
    static var guidanceHistoryNewSpreadCta: String { ru ? "Новый расклад" : "New spread" }
    static var guidanceHistoryLinkHub: String { ru ? "К центру разборов" : "Guidance hub" }
    static var guidanceHistoryTopNavAria: String { ru ? "История — навигация" : "History — navigation" }
    static var guidanceHistoryFiltersAria: String { ru ? "Фильтр записей" : "Filter entries" }
    static var guidanceHistoryFilterAll: String { ru ? "Все" : "All" }
    static var guidanceHistoryFilterGuidance: String { ru ? "Разбор" : "Guidance" }
    static var guidanceHistoryFilterQuestions: String { ru ? "Вопросы" : "Questions" }
    static var guidanceHistoryFilterDecisions: String { ru ? "Решения" : "Decisions" }
    static var guidanceHistoryFilterTarot: String { ru ? "Таро" : "Tarot" }
    static var guidanceHistoryLoading: String { ru ? "Загружаем историю…" : "Loading history…" }
    static var guidanceHistoryError: String { ru ? "Не удалось загрузить историю." : "Couldn’t load history." }
    static var guidanceHistoryEmptyCategory: String {
        ru ? "Пока нет записей в этой категории." : "No entries in this filter yet."
    }
    static var guidanceHistoryListAria: String { ru ? "Записи истории" : "History entries" }
    static var guidanceHistoryKindGuidance: String { ru ? "Разбор" : "Guidance" }
    static var guidanceHistoryKindClarify: String { ru ? "Уточнение к разбору" : "Guidance · clarify" }
    static var guidanceHistoryKindDecision: String { ru ? "Решение" : "Decision" }
    static var guidanceHistoryKindQuestion: String { ru ? "Вопрос" : "Question" }
    static var guidanceHistoryKindTarot: String { ru ? "Таро" : "Tarot" }
    static var guidanceHistoryRouteOpenReading: String { ru ? "Открыть разбор" : "Open Guidance" }
    static var guidanceHistoryRouteDecisionMode: String { ru ? "Режим решения" : "Decision mode" }
    static var guidanceHistoryRouteQuestionMode: String { ru ? "Режим вопроса" : "Question mode" }
    static var guidanceHistoryRouteCardOfDay: String { ru ? "Карта дня" : "Card of the day" }
    static var guidanceHistoryRouteTarot: String { ru ? "Таро" : "Tarot" }
    static var guidanceHistoryTarotSpreadNoBody: String {
        ru ? "Расклад сохранён без текста разбора." : "Spread saved without an in-app reading text."
    }
    static var guidanceHistoryTarotDailyNextStep: String {
        ru
            ? "Проверь, как этот мотив проявляется в одном конкретном действии сегодня."
            : "Notice how this theme shows up in one concrete action today."
    }
    static var guidanceHistoryTarotNextStepCta: String {
        ru
            ? "Если нужен разбор по вопросу — открой «Центр разборов» на одном экране, собери расклад и нажми «Получить разбор»."
            : "If you want a reading for a question, open the Guidance hub on one screen, lay the spread, and tap “Get reading”."
    }
    static var guidanceHistoryFocusFallback: String {
        ru ? "Фокус уточняется по последним ответам." : "Focus sharpens from your latest answers."
    }
    static var guidanceHistoryNextStepFallback: String {
        ru ? "Сделай один небольшой шаг по теме вопроса." : "Take one small step on the topic of your question."
    }
    static var guidanceHistoryMetaTopic: String { ru ? "Тема:" : "Topic:" }
    static var guidanceHistoryMetaSpread: String { ru ? "Расклад:" : "Spread:" }
    static var guidanceHistoryMetaLeadCard: String { ru ? "Главная карта:" : "Lead card:" }
    static var guidanceHistoryMetaShort: String { ru ? "Коротко:" : "In short:" }
    static var guidanceHistoryMetaNextStep: String { ru ? "Следующий шаг:" : "Next step:" }
}

// MARK: - Guidance hub (web `/guidance`)

enum GuidanceHubChromeCopy {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var guidanceHubNavHub: String { ru ? "Центр разборов" : "Guidance hub" }
    static var guidanceHubBackToday: String { ru ? "← Сегодня" : "← Today" }
    static var guidanceHubHeroTitle: String { ru ? "Разбор ситуации с картами" : "A grounded reading with cards" }
    static var guidanceHubHeroLead: String {
        ru
            ? "Всё на одной странице: прокручивай сверху вниз — расклад, вопрос, по желанию контекст, затем карты и запрос текста разбора."
            : "Everything on one page: scroll top to bottom—spread, question, optional context, then cards and your reading request."
    }
    static var guidanceHubHistoryLink: String { ru ? "История" : "History" }
    static var guidanceHubStartOver: String { ru ? "С начала" : "Start over" }
    static var guidanceHubTopNavAria: String { ru ? "Центр разборов — навигация" : "Guidance — navigation" }
    static var guidanceHubCompatHint: String {
        ru
            ? "Для пары есть ещё раздел «Совместимость» — здесь разбор тоже умеет отношения."
            : "For couples there’s also Compatibility—this reading flow still handles relationship dynamics well."
    }
    static var guidanceHubUnauthTitle: String { ru ? "Разбор ситуации с картами" : "A grounded reading with cards" }
    static var guidanceHubUnauthLead: String {
        ru
            ? "Войди, чтобы собрать расклад на одном экране и получить персональный ответ с учётом профиля."
            : "Sign in to lay a spread on one screen and get a personal answer that respects your profile."
    }
    static var guidanceHubPlansLink: String { ru ? "Планы" : "Plans" }
    static var guidanceHubSectionSpreadTitle: String { ru ? "Формат расклада" : "Spread format" }
    static var guidanceHubSpreadField: String { ru ? "Расклад" : "Spread" }
    static var guidanceHubCatalogSectionQuick: String { ru ? "Быстрые расклады" : "Quick spreads" }
    static var guidanceHubCatalogSectionMedium: String { ru ? "Средние расклады" : "Medium spreads" }
    static var guidanceHubCatalogSectionDeep: String { ru ? "Глубокие расклады" : "Deep spreads" }
    static var guidanceHubSectionSpreadLead: String {
        ru
            ? "Короткий или развёрнутый — от сложности ситуации. Смена формата сбрасывает уже разданные карты."
            : "Short or expanded—match the situation. Changing the format clears any cards you already dealt."
    }
    private static var guidanceHubClarifyOneCardLockedNoteTemplate: String {
        ru
            ? "Сейчас только уточняющая «одна карта» — формат основного расклада заблокирован до завершения или «{startOver}»."
            : "Right now only the clarifying “one card” spread is available—the main spread stays locked until you finish or choose “{startOver}”."
    }
    static func guidanceHubClarifyOneCardLockedNote(startOver: String) -> String {
        guidanceHubClarifyOneCardLockedNoteTemplate.replacingOccurrences(of: "{startOver}", with: startOver)
    }
    static var guidanceHubSectionQuestionTitle: String { ru ? "Твой вопрос" : "Your question" }
    static var guidanceHubSectionQuestionLead: String {
        ru
            ? "Про ясность и действие, не про гарантию будущего. Чем конкретнее формулировка, тем полезнее ответ."
            : "Ask for clarity and action—not a guaranteed outcome. The more concrete the wording, the more useful the answer."
    }
    static var guidanceHubQuestionPlaceholder: String {
        ru
            ? "Примеры:\n• Что мне важно понять в этой ситуации?\n• Как мне лучше поступить?\n• Чего я не вижу в своей реакции?"
            : "Examples:\n• What's important for me to understand here?\n• What's the wisest move for me right now?\n• What am I missing in my own reaction?"
    }
    static var guidanceHubQuestionAriaLabel: String { ru ? "Твой вопрос для расклада" : "Your question for the spread" }
    private static var guidanceHubQuestionLockedMainTemplate: String {
        ru
            ? "Основной вопрос уже зафиксирован в разборе: «{question}»"
            : "The main question is locked for this reading: “{question}”"
    }
    static func guidanceHubQuestionLockedMain(question: String) -> String {
        guidanceHubQuestionLockedMainTemplate.replacingOccurrences(of: "{question}", with: question)
    }
    static var guidanceHubQuestionAvoidHint: String {
        ru
            ? "Избегай «он точно…?» и «я точно получу…?» — здесь не про предсказание исхода."
            : "Avoid “will they definitely…” and “will I definitely get…”—this isn’t about predicting outcomes."
    }
    static var guidanceHubSectionContextTitle: String { ru ? "Контекст по желанию" : "Context (optional)" }
    static var guidanceHubSectionContextLead: String {
        ru
            ? "Тема и ожидание помогают точнее собрать разбор. Можно ничего не выбирать."
            : "Topic and intent help tailor the reading. You can leave everything unset."
    }
    static var guidanceHubFieldTopic: String { ru ? "Тема" : "Topic" }
    static var guidanceHubFieldOutcome: String { ru ? "Что хочешь получить" : "What you want from this" }
    static var guidanceHubFieldRelationshipRole: String { ru ? "Кто этот человек для тебя" : "Who this person is to you" }
    static var guidanceHubFieldIntimacyFocus: String { ru ? "Что сильнее всего волнует" : "What worries you most" }
    static var guidanceHubClarifyGoalTitle: String { ru ? "Цель уточняющей карты" : "Goal of the clarifying card" }
    static var guidanceHubClarifyGoalLead: String {
        ru
            ? "Выбери один узкий фокус — так разбор не превращается в бесконечное перетягивание."
            : "Pick one narrow focus—so the reading doesn't turn into endless back-and-forth."
    }
    static var guidanceHubClarifySectionGlyph: String { "→" }
    static var guidanceHubSectionCardsTitle: String { ru ? "Карты" : "Cards" }
    static var guidanceHubCardsLeadClarify: String {
        ru
            ? "Одна карта в позиции «Фокус». Раздай и открой её — затем запроси уточнение (сервер примет не больше одного раза к этому основному разбору)."
            : "One card in the “Focus” position. Deal and reveal it—then request clarification (the server allows at most one per main reading)."
    }
    private static var guidanceHubCardsLeadNormalTemplate: String {
        ru
            ? "Раздай колоду для «{spreadTitle}», затем открывай позиции по одной. Когда всё открыто и вопрос готов — запроси разбор."
            : "Shuffle for “{spreadTitle}”, then reveal each position one at a time. When everything is open and your question is ready—request the reading."
    }
    static func guidanceHubCardsLeadNormal(spreadTitle: String) -> String {
        guidanceHubCardsLeadNormalTemplate.replacingOccurrences(of: "{spreadTitle}", with: spreadTitle)
    }
    static var guidanceHubDealDrawing: String { ru ? "Раскладываем…" : "Shuffling…" }
    static var guidanceHubDealReshuffle: String { ru ? "Пересдать карты" : "Re-deal cards" }
    static var guidanceHubDealShuffle: String { ru ? "Раздать карты" : "Deal cards" }
    static var guidanceHubDealReadyHint: String {
        ru
            ? "Нажми «Раздать карты», когда будешь готов сфокусироваться на вопросе."
            : "Tap “Deal cards” when you're ready to focus on your question."
    }
    static var guidanceHubCardsRevealHint: String {
        ru
            ? "Открой каждую позицию — затем появится активная кнопка «Получить разбор»."
            : "Reveal every position—then the “Get reading” button becomes active."
    }
    static var guidanceHubSubmitClarify: String { ru ? "Получить уточнение" : "Get clarification" }
    static var guidanceHubSubmitReading: String { ru ? "Получить разбор" : "Get reading" }
    static var guidanceHubSubmitHintClarify: String {
        ru ? "Выбери цель уточнения выше и открой карту." : "Pick a clarification goal above and reveal the card."
    }
    static var guidanceHubSubmitHintQuestion: String {
        ru
            ? "Сначала уточни вопрос выше (минимум три символа)."
            : "Refine your question above first (at least three characters)."
    }
    static var guidanceHubLoadingTitle: String { ru ? "Собираем разбор…" : "Building your reading…" }
    static var guidanceHubLoadingLeadClarify: String {
        ru
            ? "Связываем одну карту с твоим основным разбором и выбранной целью уточнения."
            : "We're linking one card to your main reading and the goal you chose."
    }
    static var guidanceHubLoadingLeadMain: String {
        ru
            ? "Учитываем вопрос, позиции и профиль — это связный текст под ситуацию, не справочник значений."
            : "We weigh your question, positions, and profile—it's a coherent take for your situation, not a dictionary of meanings."
    }
    static var guidanceHubResultSectionGlyph: String { "✓" }
    static var guidanceHubResultTitle: String { ru ? "Разбор" : "Reading" }
    static var guidanceHubNewSpreadCta: String { ru ? "Новый расклад" : "New spread" }
    static var guidanceHubToastNoSessionToken: String {
        ru
            ? "Нет токена сессии в браузере. Выйди и войди снова — без заголовка Authorization API отвечает 401."
            : "No session token in the browser. Sign out and back in—without an Authorization header the API returns 401."
    }
    static var guidanceHubToastSessionExpired: String {
        ru ? "Сессия недействительна или истекла. Войди заново." : "Session invalid or expired. Please sign in again."
    }
    static var guidanceHubToastDealFailed: String { ru ? "Не удалось раздать карты. Попробуй ещё раз." : "Could not deal the cards. Try again." }
    static var guidanceHubToastQuestionVague: String {
        ru ? "Сформулируй вопрос чуть конкретнее" : "Make your question a bit more specific"
    }
    static var guidanceHubToastRevealAllFirst: String {
        ru ? "Сначала открой все карты расклада" : "Reveal every position in the spread first"
    }
    static var guidanceHubToastNoSessionReading: String {
        ru ? "Нет активной сессии для запроса разбора. Войди снова." : "No active session to request a reading. Sign in again."
    }
    static var guidanceHubToastClarifyOneCardOnly: String {
        ru
            ? "Уточнение — только расклад «одна карта» и одна открытая позиция"
            : "Clarification is only for the “one card” spread with one open position"
    }
    static var guidanceHubToastClarifyAlready409: String {
        ru
            ? "Уточнение к этому разбору уже было — начни новую сессию с раскладом."
            : "You already used a clarification for this reading—start a new session with a spread."
    }
    static var guidanceHubToastReadingFailed: String {
        ru
            ? "Не удалось собрать разбор. Проверь сеть и попробуй снова."
            : "Could not assemble the reading. Check your network and try again."
    }
    static var guidanceHubToastFeedbackSavedHelpful: String { ru ? "Сигнал сохранён" : "Feedback saved" }
    static var guidanceHubToastFeedbackSavedUnclear: String {
        ru ? "Отметили, что нужно больше ясности" : "Noted that you need more clarity"
    }
    static var guidanceHubToastFeedbackSaveFailed: String {
        ru ? "Не удалось сохранить отзыв" : "Could not save feedback"
    }
    static var guidanceHubToastNeedMainReading: String {
        ru ? "Сначала получи основной разбор" : "Get the main reading first"
    }
    static var guidanceHubToastClarifyAlreadyUsed: String {
        ru
            ? "Уточнение к этому разбору уже использовано"
            : "Clarification for this reading was already used"
    }
}
