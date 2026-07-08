import SwiftUI

// MARK: - Screen chrome (RU / EN, aligned with API `Accept-Language`)

enum CompatibilityScreenChrome {
    static var useRussian: Bool {
        if let code = Locale.current.language.languageCode?.identifier.lowercased() {
            if code == "ru" { return true }
            if code == "en" { return false }
        }
        return Bundle.main.preferredLocalizations.first?.lowercased().hasPrefix("ru") == true
    }

    static var heroEyebrow: String { useRussian ? "Про связи" : "Relationships" }
    static var heroTitle: String { useRussian ? "Совместимость" : "Compatibility" }
    static var heroSubtitle: String {
        useRussian
            ? "Два человека, тип связи и честный разбор — без лишнего шума."
            : "Two people, connection type, and a grounded read — without the noise."
    }
    static var navTitle: String { heroTitle }
    static var pickerCompatibilityMode: String { useRussian ? "Режим совместимости" : "Compatibility mode" }
    static var pickerCompareDepth: String { useRussian ? "Глубина разбора" : "Reading depth" }
    static var relationModeSection: String { useRussian ? "Режим связи" : "Connection mode" }
    static var cardYou: String { useRussian ? "Ты" : "You" }
    static var cardPartner: String { useRussian ? "Партнёр" : "Partner" }
    static var primaryProfileFallback: String { useRussian ? "Основной профиль" : "Primary profile" }
    static var compareProfilePlaceholder: String { useRussian ? "Выбери второй профиль" : "Choose second profile" }
    static var compareProfileDetailPlaceholder: String {
        useRussian ? "Подключи второй профиль для расчёта." : "Add a second profile to calculate."
    }
    static var loadingProfiles: String { useRussian ? "Загружаю профили..." : "Loading profiles..." }
    static var whoWeCompare: String { useRussian ? "Кого сравниваем" : "Who we compare" }
    static var pickProfile: String { useRussian ? "Выбери профиль" : "Choose profile" }
    static var pickerPrimaryProfileA11y: String { useRussian ? "Первый профиль" : "First profile" }
    static var pickerSecondProfileA11y: String { useRussian ? "Второй профиль" : "Second profile" }
    static var calculateCompatibility: String { useRussian ? "Рассчитать совместимость" : "Calculate compatibility" }
    static var comparing: String { useRussian ? "Сравниваю..." : "Comparing..." }
    static var profilesLoadErrorTitle: String {
        useRussian ? "Совместимость не может загрузить профили" : "Couldn't load profiles"
    }
    static var retryLoad: String { useRussian ? "Повторить загрузку" : "Retry" }
    static var needSecondProfileTitle: String { useRussian ? "Нужен ещё один профиль" : "One more profile needed" }
    static var needSecondProfileBody: String {
        useRussian
            ? "Добавь второго человека в профили — тогда станет доступен расчёт."
            : "Add another person in profiles to unlock this calculation."
    }
    static var openProfileAddPerson: String {
        useRussian ? "Открыть профиль и добавить человека" : "Open profiles and add someone"
    }
    static var addPersonHere: String { useRussian ? "Добавить человека здесь" : "Add someone here" }
    static var sunSignsSection: String { useRussian ? "По солнечным знакам" : "By Sun signs" }
    static var pickerYourSign: String { useRussian ? "Твой знак" : "Your sign" }
    static var pickerPartnerSign: String { useRussian ? "Знак партнёра" : "Partner sign" }
    static var pickerBetweenYou: String { useRussian ? "Между вами сейчас" : "Between you now" }
    static var contextUnspecified: String { useRussian ? "Не указывать" : "Not specified" }
    static var calculating: String { useRussian ? "Считаю..." : "Calculating..." }
    static var calculateBySigns: String { useRussian ? "Рассчитать по знакам" : "Calculate by signs" }
    static var birthdatesSection: String { useRussian ? "По датам рождения" : "By birth dates" }
    static var pickerYourBirthdate: String { useRussian ? "Твоя дата рождения" : "Your birth date" }
    static var pickerPartnerBirthdate: String { useRussian ? "Дата партнёра" : "Partner birth date" }
    static func sunSignsLine(_ a: String, _ b: String) -> String {
        useRussian ? "Солнечные знаки: \(a) и \(b)" : "Sun signs: \(a) and \(b)"
    }
    static var signFromDatesError: String {
        useRussian ? "Не удалось определить знаки по датам." : "Could not resolve signs from dates."
    }
    static var calculateByDates: String { useRussian ? "Рассчитать по датам" : "Calculate by dates" }
    static var depthFull: String { useRussian ? "Глубоко" : "Deep" }
    static var depthQuick: String { useRussian ? "Быстро" : "Quick" }
    static var entryProfiles: String { useRussian ? "Профили" : "Profiles" }
    static var entrySigns: String { useRussian ? "Знаки" : "Signs" }
    static var entryDates: String { useRussian ? "Даты" : "Dates" }
    static var modeRomantic: String { useRussian ? "Любовь" : "Love" }
    static var modeFamily: String { useRussian ? "Семья" : "Family" }
    static var modeParentChild: String { useRussian ? "Родитель/ребёнок" : "Parent / child" }
    static var modeBusiness: String { useRussian ? "Работа" : "Work" }
    static var ctxJustMet: String {
        useRussian ? "Только познакомились / начинаем общение" : "Just met / starting to talk"
    }
    static var ctxAttraction: String { useRussian ? "Есть притяжение" : "Mutual attraction" }
    static var ctxInRelationship: String { useRussian ? "Уже в отношениях" : "In a relationship" }
    static var ctxUnclear: String { useRussian ? "Непонятная ситуация" : "Unclear situation" }
    static var ctxConflict: String { useRussian ? "Конфликт или дистанция" : "Conflict or distance" }
    static var ctxSplitPull: String { useRussian ? "Расстались, но тянет" : "Split but still pulled" }
    static var resultTitle: String { useRussian ? "Результат" : "Result" }
    static var resultSummaryFallback: String {
        useRussian ? "Краткий смысл связи — ниже." : "The gist of this bond — below."
    }
    static var strongestLayer: String { useRussian ? "Сильнейший слой" : "Strongest layer" }
    static var whatToDoWithBond: String {
        useRussian ? "Что делать с этой связью" : "What to do with this connection"
    }
    static var step: String { useRussian ? "Шаг" : "Step" }
    static var dimensionsTitle: String { useRussian ? "Измерения связи" : "Relationship dimensions" }
    static var openGuidanceCta: String { useRussian ? "Открыть разбор" : "Open Guidance" }
    static var legacyMoreText: String { useRussian ? "Ещё текст" : "More text" }
    static var legacyFullPaywall: String {
        useRussian ? "Полный разбор — в подписке." : "Full reading — included with subscription."
    }
    static var analyzeBack: String { useRussian ? "← Все уровни" : "← All topics" }
    static var analyzeInvestigation: String { useRussian ? "Исследование" : "Exploration" }
    static var analyzeTitle: String { useRussian ? "Разобрать совместимость" : "Analyze compatibility" }
    static var analyzeQuickEntry: String { useRussian ? "Быстрый вход" : "Quick entry" }
    static var analyzePreciseEntry: String { useRussian ? "Точный разбор" : "Precise reading" }
    static var analyzeRun: String { useRussian ? "Получить разбор" : "Get reading" }
    static var analyzeLoadError: String {
        useRussian ? "Не удалось загрузить разбор." : "Could not load the reading."
    }
    static var analyzeNameYou: String { useRussian ? "Твоё имя (необязательно)" : "Your name (optional)" }
    static var analyzeNamePartner: String { useRussian ? "Имя партнёра (необязательно)" : "Partner name (optional)" }
    static var echoLabel: String { useRussian ? "Это про вас?" : "About you?" }
    static var echoYes: String { useRussian ? "точно" : "yes" }
    static var echoPartial: String { useRussian ? "частично" : "partly" }
    static var echoNo: String { useRussian ? "мимо" : "miss" }
    static var echoGiveback: String {
        useRussian ? "Запомним — учтём в следующем разборе." : "Saved — we’ll use this next time."
    }
    static var rebuildWithMarks: String {
        useRussian ? "Уточнить разбор с учётом отметок" : "Refine with your marks"
    }
    static var rebuilding: String { useRussian ? "Уточняем…" : "Refining…" }
    static var hubPassScenario: String { useRussian ? "Не сейчас" : "Not now" }
    static var profileLensEyebrow: String { useRussian ? "Через твой профиль" : "From your profile" }
}

private enum ZodiacSunSign: String, CaseIterable, Identifiable {
    case aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces

    var id: String { rawValue }

    var title: String {
        CompatibilityScreenChrome.useRussian ? russianTitle : englishTitle
    }

    private var russianTitle: String {
        switch self {
        case .aries: return "Овен"
        case .taurus: return "Телец"
        case .gemini: return "Близнецы"
        case .cancer: return "Рак"
        case .leo: return "Лев"
        case .virgo: return "Дева"
        case .libra: return "Весы"
        case .scorpio: return "Скорпион"
        case .sagittarius: return "Стрелец"
        case .capricorn: return "Козерог"
        case .aquarius: return "Водолей"
        case .pisces: return "Рыбы"
        }
    }

    private var englishTitle: String {
        switch self {
        case .aries: return "Aries"
        case .taurus: return "Taurus"
        case .gemini: return "Gemini"
        case .cancer: return "Cancer"
        case .leo: return "Leo"
        case .virgo: return "Virgo"
        case .libra: return "Libra"
        case .scorpio: return "Scorpio"
        case .sagittarius: return "Sagittarius"
        case .capricorn: return "Capricorn"
        case .aquarius: return "Aquarius"
        case .pisces: return "Pisces"
        }
    }
}

private enum QuickCompatibilityContext: String, CaseIterable, Identifiable {
    case justMet = "just_met"
    case mutualAttraction = "mutual_attraction"
    case inRelationship = "in_relationship"
    case unclear
    case conflictDistance = "conflict_distance"
    case splitButPull = "split_but_pull"

    var id: String { rawValue }

    var menuTitle: String {
        switch self {
        case .justMet:
            return CompatibilityScreenChrome.ctxJustMet
        case .mutualAttraction:
            return CompatibilityScreenChrome.ctxAttraction
        case .inRelationship:
            return CompatibilityScreenChrome.ctxInRelationship
        case .unclear:
            return CompatibilityScreenChrome.ctxUnclear
        case .conflictDistance:
            return CompatibilityScreenChrome.ctxConflict
        case .splitButPull:
            return CompatibilityScreenChrome.ctxSplitPull
        }
    }
}

private enum SolarSignFromUTCDate {
    /// Как на вебе `zodiacFromDate`: месяц/день в UTC.
    static func sign(for date: Date) -> ZodiacSunSign? {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0) ?? .gmt
        let month = calendar.component(.month, from: date)
        let day = calendar.component(.day, from: date)
        if (month == 3 && day >= 21) || (month == 4 && day <= 19) { return .aries }
        if (month == 4 && day >= 20) || (month == 5 && day <= 20) { return .taurus }
        if (month == 5 && day >= 21) || (month == 6 && day <= 20) { return .gemini }
        if (month == 6 && day >= 21) || (month == 7 && day <= 22) { return .cancer }
        if (month == 7 && day >= 23) || (month == 8 && day <= 22) { return .leo }
        if (month == 8 && day >= 23) || (month == 9 && day <= 22) { return .virgo }
        if (month == 9 && day >= 23) || (month == 10 && day <= 22) { return .libra }
        if (month == 10 && day >= 23) || (month == 11 && day <= 21) { return .scorpio }
        if (month == 11 && day >= 22) || (month == 12 && day <= 21) { return .sagittarius }
        if (month == 12 && day >= 22) || (month == 1 && day <= 19) { return .capricorn }
        if (month == 1 && day >= 20) || (month == 2 && day <= 18) { return .aquarius }
        if (month == 2 && day >= 19) || (month == 3 && day <= 20) { return .pisces }
        return nil
    }
}

struct CompatibilityView: View {
    enum CompareDepth: String, CaseIterable, Identifiable {
        case full
        case quick

        var id: String { rawValue }

        var title: String {
            switch self {
            case .full: return CompatibilityScreenChrome.depthFull
            case .quick: return CompatibilityScreenChrome.depthQuick
            }
        }

        var requestType: CompatibilityRequestType {
            switch self {
            case .full: return .deep
            case .quick: return .quick
            }
        }
    }

    enum CompatibilityEntryMode: String, CaseIterable, Identifiable {
        case profiles
        case signs
        case birthdates

        var id: String { rawValue }

        var title: String {
            switch self {
            case .profiles: return CompatibilityScreenChrome.entryProfiles
            case .signs: return CompatibilityScreenChrome.entrySigns
            case .birthdates: return CompatibilityScreenChrome.entryDates
            }
        }
    }

    enum RelationMode: String, CaseIterable, Identifiable {
        case romantic
        case family
        case parentChild
        case business

        var id: String { rawValue }

        var title: String {
            switch self {
            case .romantic: return CompatibilityScreenChrome.modeRomantic
            case .family: return CompatibilityScreenChrome.modeFamily
            case .parentChild: return CompatibilityScreenChrome.modeParentChild
            case .business: return CompatibilityScreenChrome.modeBusiness
            }
        }

    }

    let store: TodayFlowStore
    var onOpenProfile: (() -> Void)? = nil
    var onOpenGuidance: (() -> Void)? = nil

    @State private var relationMode: RelationMode = .romantic
    @State private var compareDepth: CompareDepth = .full
    @State private var profiles: [StoredAstroProfile] = []
    @State private var primaryProfileID: Int?
    @State private var compareProfileID: Int?
    @State private var isLoadingProfiles = false
    @State private var isComparing = false
    @State private var errorMessage: String?
    @State private var result: CompatibilityComparisonResponse?
    @State private var isAddProfilePresented = false
    @State private var compatibilityEntry: CompatibilityEntryMode = .profiles
    @State private var signFrom: ZodiacSunSign = .aries
    @State private var signTo: ZodiacSunSign = .libra
    @State private var birthDateA = Calendar.current.date(from: DateComponents(year: 1992, month: 3, day: 21)) ?? .now
    @State private var birthDateB = Calendar.current.date(from: DateComponents(year: 1994, month: 10, day: 15)) ?? .now
    @State private var signApiResult: SignCompatibilityAPIResponse?
    @State private var isLoadingSignApi = false
    @State private var signApiError: String?
    @State private var quickCompatibilityContext: QuickCompatibilityContext?
    @State private var encyclopediaCatalog: CompatibilityEncyclopediaResponse?
    @State private var encyclopediaLoading = false
    @State private var pairScenarioId: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    if let catalog = encyclopediaCatalog {
                        CompatibilityEncyclopediaHubSection(
                            catalog: catalog,
                            store: store,
                            canRunPairExplore: profiles.count >= 2 && primaryProfileID != nil && compareProfileID != nil,
                            onPairScenarioExplore: { scenarioId in
                                compatibilityEntry = .profiles
                                pairScenarioId = scenarioId
                                runComparison(formatId: scenarioId)
                            }
                        )
                    } else {
                        if encyclopediaLoading {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                        }
                        VStack(alignment: .leading, spacing: 6) {
                            Text(CompatibilityScreenChrome.heroEyebrow)
                                .font(.caption.weight(.semibold))
                                .textCase(.uppercase)
                                .tracking(0.6)
                                .foregroundStyle(TodayFlowTheme.sand)
                            Text(CompatibilityScreenChrome.heroTitle)
                                .font(.system(size: 30, weight: .bold, design: .rounded))
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(CompatibilityScreenChrome.heroSubtitle)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                        }
                        .padding(22)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .todayFlowSurfacePrimary(cornerRadius: 28)
                    }

                    Picker(CompatibilityScreenChrome.pickerCompatibilityMode, selection: $compatibilityEntry) {
                        ForEach(CompatibilityEntryMode.allCases) { mode in
                            Text(mode.title).tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)
                    .onChange(of: compatibilityEntry) { _, newValue in
                        if newValue != .profiles {
                            result = nil
                            errorMessage = nil
                        }
                        if newValue != .signs && newValue != .birthdates {
                            signApiResult = nil
                            signApiError = nil
                        }
                    }

                    if compatibilityEntry == .profiles {
                        profilesDeepSection
                    } else if compatibilityEntry == .signs {
                        signPairQuickSection
                    } else {
                        birthdateQuickSection
                    }
                }
                .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .navigationTitle(CompatibilityScreenChrome.navTitle)
            .task {
                await loadProfiles()
                await loadEncyclopedia()
            }
            .sheet(isPresented: $isAddProfilePresented) {
                AddProfileView(store: store) {
                    await loadProfiles(force: true)
                }
            }
            .toolbar {
                ToolbarItem(placement: toolbarTrailingPlacement) {
                    Button {
                        Task {
                            await loadProfiles(force: true)
                        }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
    }

    @ViewBuilder
    private var profilesDeepSection: some View {
        Picker(CompatibilityScreenChrome.pickerCompareDepth, selection: $compareDepth) {
            ForEach(CompareDepth.allCases) { depth in
                Text(depth.title).tag(depth)
            }
        }
        .pickerStyle(.segmented)

        VStack(alignment: .leading, spacing: 12) {
            Text(CompatibilityScreenChrome.relationModeSection)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            ForEach(RelationMode.allCases) { mode in
                Button {
                    withAnimation(.spring(response: 0.34, dampingFraction: 0.86)) {
                        relationMode = mode
                    }
                } label: {
                    RelationModeRow(
                        mode: mode,
                        isSelected: relationMode == mode
                    )
                }
                .buttonStyle(.plain)
                .foregroundStyle(TodayFlowTheme.ink)
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatSurface()

        HStack(spacing: 12) {
            CompatibilityProfileCard(
                title: CompatibilityScreenChrome.cardYou,
                subtitle: primaryProfile?.label ?? (store.user.firstName.isEmpty ? CompatibilityScreenChrome.primaryProfileFallback : store.user.firstName),
                detail: primaryProfileDetail
            )
            CompatibilityProfileCard(
                title: CompatibilityScreenChrome.cardPartner,
                subtitle: compareProfile?.label ?? CompatibilityScreenChrome.compareProfilePlaceholder,
                detail: compareProfileDetail
            )
        }

        if isLoadingProfiles {
            ProgressView(CompatibilityScreenChrome.loadingProfiles)
                .tint(TodayFlowTheme.sunset)
        } else         if profiles.count >= 2 {
            VStack(alignment: .leading, spacing: 12) {
                Text(CompatibilityScreenChrome.whoWeCompare)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)

                if let pairScenarioId {
                    let skin = CompatibilityScenarioRegistry.skin(for: pairScenarioId)
                    Text(CompatibilityScreenChrome.useRussian
                         ? "Сценарий: \(skin.poster)"
                         : "Scenario: \(skin.poster)")
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(TodayFlowTheme.sand)
                }

                Picker(CompatibilityScreenChrome.pickerPrimaryProfileA11y, selection: $primaryProfileID) {
                    Text(CompatibilityScreenChrome.pickProfile).tag(Optional<Int>.none)
                    ForEach(profiles) { profile in
                        Text(profile.label).tag(Optional(profile.id))
                    }
                }

                Picker(CompatibilityScreenChrome.pickerSecondProfileA11y, selection: $compareProfileID) {
                    Text(CompatibilityScreenChrome.pickProfile).tag(Optional<Int>.none)
                    ForEach(filteredCompareProfiles) { profile in
                        Text(profile.label).tag(Optional(profile.id))
                    }
                }

                Button {
                    runComparison(formatId: pairScenarioId)
                } label: {
                    Label(isComparing ? CompatibilityScreenChrome.comparing : CompatibilityScreenChrome.calculateCompatibility, systemImage: "person.2.wave.2.fill")
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.plain)
                .foregroundStyle(.white)
                .background(
                    LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
                )
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                .disabled(isComparing || primaryProfileID == nil || compareProfileID == nil)
            }
            .padding(22)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowCompatSurface()
        } else if profiles.isEmpty, let errorMessage {
            VStack(alignment: .leading, spacing: 10) {
                Text(CompatibilityScreenChrome.profilesLoadErrorTitle)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(errorMessage)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))

                Button(CompatibilityScreenChrome.retryLoad) {
                    Task { await loadProfiles(force: true) }
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }
            .padding(22)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowCompatSurface()
        } else {
            VStack(alignment: .leading, spacing: 10) {
                Text(CompatibilityScreenChrome.needSecondProfileTitle)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(CompatibilityScreenChrome.needSecondProfileBody)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))

                Button(CompatibilityScreenChrome.openProfileAddPerson) {
                    onOpenProfile?()
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)

                Button(CompatibilityScreenChrome.addPersonHere) {
                    isAddProfilePresented = true
                }
                .buttonStyle(.bordered)
            }
            .padding(22)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowCompatSurface()
        }

        if let errorMessage {
            Text(errorMessage)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.roseClay)
                .padding(.horizontal, 4)
        }

        if let result {
            CompatibilityResultSection(
                result: result,
                relationMode: relationMode,
                activeFormatId: activePairFormatId,
                store: store,
                onOpenGuidance: onOpenGuidance,
                onScenarioSwitch: { newId in
                    pairScenarioId = newId
                    runComparison(formatId: newId)
                },
                onRefresh: { runComparison(formatId: pairScenarioId) },
                refreshing: isComparing
            )
        }
    }

    private var activePairFormatId: String {
        CompatibilityScenarioRegistry.formatFromRelationMode(relationMode.backendValue, override: pairScenarioId)
    }

    @ViewBuilder
    private var signPairQuickSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(CompatibilityScreenChrome.sunSignsSection)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            Picker(CompatibilityScreenChrome.pickerYourSign, selection: $signFrom) {
                ForEach(ZodiacSunSign.allCases) { sign in
                    Text(sign.title).tag(sign)
                }
            }

            Picker(CompatibilityScreenChrome.pickerPartnerSign, selection: $signTo) {
                ForEach(ZodiacSunSign.allCases) { sign in
                    Text(sign.title).tag(sign)
                }
            }

            Picker(CompatibilityScreenChrome.pickerBetweenYou, selection: $quickCompatibilityContext) {
                Text(CompatibilityScreenChrome.contextUnspecified).tag(Optional<QuickCompatibilityContext>.none)
                ForEach(QuickCompatibilityContext.allCases) { ctx in
                    Text(ctx.menuTitle).tag(Optional(ctx))
                }
            }

            Button {
                runSignCompatibility(from: signFrom.rawValue, to: signTo.rawValue)
            } label: {
                Label(isLoadingSignApi ? CompatibilityScreenChrome.calculating : CompatibilityScreenChrome.calculateBySigns, systemImage: "sparkles")
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.white)
            .background(
                LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
            )
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .disabled(isLoadingSignApi)

            if let signApiError {
                Text(signApiError)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.roseClay)
            }

            if let signApiResult {
                SignCompatibilityPanel(response: signApiResult)
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatSurface()
    }

    @ViewBuilder
    private var birthdateQuickSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(CompatibilityScreenChrome.birthdatesSection)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            DatePicker(CompatibilityScreenChrome.pickerYourBirthdate, selection: $birthDateA, displayedComponents: .date)
            DatePicker(CompatibilityScreenChrome.pickerPartnerBirthdate, selection: $birthDateB, displayedComponents: .date)

            if let a = SolarSignFromUTCDate.sign(for: birthDateA), let b = SolarSignFromUTCDate.sign(for: birthDateB) {
                Text(CompatibilityScreenChrome.sunSignsLine(a.title, b.title))
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.8))
            }

            Button {
                guard let a = SolarSignFromUTCDate.sign(for: birthDateA)?.rawValue,
                      let b = SolarSignFromUTCDate.sign(for: birthDateB)?.rawValue else {
                    signApiError = CompatibilityScreenChrome.signFromDatesError
                    signApiResult = nil
                    return
                }
                runSignCompatibility(from: a, to: b)
            } label: {
                Label(isLoadingSignApi ? CompatibilityScreenChrome.calculating : CompatibilityScreenChrome.calculateByDates, systemImage: "calendar")
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.white)
            .background(
                LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
            )
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .disabled(isLoadingSignApi)

            if let signApiError {
                Text(signApiError)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.roseClay)
            }

            if let signApiResult {
                SignCompatibilityPanel(response: signApiResult)
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatSurface()
    }

    private func runSignCompatibility(from: String, to: String) {
        isLoadingSignApi = true
        signApiError = nil
        Task {
            do {
                let response = try await TodayFlowAPIClient.shared.fetchSignCompatibility(
                    fromSign: from,
                    toSign: to,
                    relationshipContext: quickCompatibilityContext?.rawValue
                )
                await MainActor.run {
                    signApiResult = response
                    isLoadingSignApi = false
                }
            } catch {
                await MainActor.run {
                    signApiResult = nil
                    signApiError = error.localizedDescription
                    isLoadingSignApi = false
                }
            }
        }
    }

    private var primaryProfile: StoredAstroProfile? {
        profiles.first(where: { $0.id == primaryProfileID })
    }

    private var compareProfile: StoredAstroProfile? {
        profiles.first(where: { $0.id == compareProfileID })
    }

    private var filteredCompareProfiles: [StoredAstroProfile] {
        profiles.filter { $0.id != primaryProfileID }
    }

    private var primaryProfileDetail: String {
        [primaryProfile?.locationName, primaryProfile?.birthDate].compactMap { $0 }.joined(separator: " · ")
    }

    private var compareProfileDetail: String {
        guard let compareProfile else {
            return CompatibilityScreenChrome.compareProfileDetailPlaceholder
        }
        return [compareProfile.locationName, compareProfile.birthDate].compactMap { $0 }.joined(separator: " · ")
    }

    private func loadProfiles(force: Bool = false) async {
        if isLoadingProfiles { return }
        if !force, !profiles.isEmpty { return }
        isLoadingProfiles = true
        errorMessage = nil

        do {
            let loaded = try await store.loadAstroProfiles()
            await MainActor.run {
                profiles = loaded
                primaryProfileID = loaded.first(where: { $0.isPrimary == true })?.id ?? loaded.first?.id
                compareProfileID = loaded.first(where: { $0.id != primaryProfileID })?.id
                isLoadingProfiles = false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
                isLoadingProfiles = false
            }
        }
    }

    private func loadEncyclopedia() async {
        if encyclopediaLoading { return }
        encyclopediaLoading = true
        defer { encyclopediaLoading = false }
        do {
            let loc = CompatibilityScreenChrome.useRussian ? "ru" : "en"
            let catalog = try await TodayFlowAPIClient.shared.fetchCompatibilityEncyclopedia(locale: loc)
            await MainActor.run {
                encyclopediaCatalog = catalog
            }
            await store.trackCompatibilityEvent(
                eventType: "compatibility_encyclopedia_view",
                payload: [
                    "content_locale": .string(catalog.contentLocale),
                    "catalog_version": .string(catalog.version),
                ]
            )
        } catch {
            // Calculator modes remain available without catalog.
        }
    }

    private func runComparison(formatId: String? = nil) {
        guard let primaryProfileID, let compareProfileID else { return }
        isComparing = true
        errorMessage = nil

        let resolvedFormat = formatId ?? pairScenarioId ?? activePairFormatId

        Task {
            do {
                let response = try await store.compareCompatibility(
                    profileID1: primaryProfileID,
                    profileID2: compareProfileID,
                    relationMode: relationMode.backendValue,
                    type: compareDepth.requestType,
                    formatID: resolvedFormat
                )
                await MainActor.run {
                    result = response
                    pairScenarioId = response.scenarioContext?.formatId ?? resolvedFormat
                    isComparing = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isComparing = false
                }
            }
        }
    }
}

private extension CompatibilityView.RelationMode {
    var backendValue: String {
        switch self {
        case .romantic:
            return "romantic"
        case .family:
            return "family"
        case .parentChild:
            return "parent_child"
        case .business:
            return "business"
        }
    }
}

private struct CompatibilityEncyclopediaHubSection: View {
    let catalog: CompatibilityEncyclopediaResponse
    let store: TodayFlowStore
    var canRunPairExplore: Bool = false
    var onPairScenarioExplore: ((String) -> Void)? = nil

    private var isRu: Bool { catalog.contentLocale.lowercased().hasPrefix("ru") }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 8) {
                Text(catalog.hero.eyebrow)
                    .font(.caption.weight(.semibold))
                    .textCase(.uppercase)
                    .tracking(0.6)
                    .foregroundStyle(TodayFlowTheme.sand)
                Text(catalog.hero.title)
                    .font(.system(size: 26, weight: .bold, design: .rounded))
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(catalog.hero.lead)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfacePrimary(cornerRadius: 28)

            Text(isRu ? "Что можно исследовать" : "What you can explore")
                .font(.headline)
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                ForEach(catalog.categories.prefix(12)) { item in
                    scenarioHubLink(
                        title: item.title,
                        subtitle: item.subtitle,
                        emoji: item.emoji,
                        scenarioId: CompatibilityScenarioRegistry.resolveScenarioId(
                            topic: item.analyzeParams.topic ?? item.id,
                            series: item.analyzeParams.series,
                            reading: item.analyzeParams.reading
                        ),
                        analyzeSelection: item.analyzeSelection(),
                        trackPayload: item.topicSelectPayload(kind: "category")
                    )
                }
            }

            Text(isRu ? "Самые популярные разборы" : "Popular readings")
                .font(.headline)
            ForEach(catalog.popularReadings.prefix(6)) { reading in
                NavigationLink {
                    CompatibilityEncyclopediaAnalyzeView(selection: reading.analyzeSelection(), store: store)
                } label: {
                    Text(reading.title)
                        .font(.subheadline.weight(.medium))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .todayFlowCompatInsetCard(cornerRadius: 14)
                }
                .buttonStyle(.plain)
                .simultaneousGesture(TapGesture().onEnded {
                    Task {
                        await store.trackCompatibilityEvent(
                            eventType: "compatibility_topic_select",
                            payload: reading.topicSelectPayload(kind: "reading")
                        )
                    }
                })
            }

            Text(isRu ? "Серии" : "Series")
                .font(.headline)
            ForEach(catalog.series.prefix(8)) { series in
                HStack(alignment: .center, spacing: 8) {
                    scenarioHubLink(
                        title: series.title,
                        subtitle: series.subtitle,
                        emoji: nil,
                        scenarioId: series.id,
                        analyzeSelection: series.analyzeSelection(),
                        trackPayload: series.topicSelectPayload(kind: "series"),
                        inline: true
                    )
                    Button(CompatibilityScreenChrome.hubPassScenario) {
                        Task {
                            await store.trackCompatibilityEvent(
                                eventType: "compatibility_echo",
                                payload: [
                                    "surface": .string("hub"),
                                    "target": .string("scenario:\(series.id)"),
                                    "echo": .string("no"),
                                    "format_id": .string(series.id),
                                    "scenario_id": .string(series.id),
                                ]
                            )
                        }
                    }
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                }
            }
        }
    }

    @ViewBuilder
    private func scenarioHubLink(
        title: String,
        subtitle: String,
        emoji: String?,
        scenarioId: String,
        analyzeSelection: CompatibilityEncyclopediaAnalyzeSelection,
        trackPayload: [String: JSONValue],
        inline: Bool = false
    ) -> some View {
        let cardLabel: some View = Group {
            if inline {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(.subheadline.weight(.semibold))
                    Text(subtitle).font(.caption).foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                }
            } else {
                VStack(alignment: .leading, spacing: 6) {
                    if let emoji { Text(emoji).font(.title2) }
                    Text(title).font(.subheadline.weight(.semibold))
                    Text(subtitle).font(.caption).foregroundStyle(TodayFlowTheme.ink.opacity(0.6))
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .todayFlowCompatInsetCard(cornerRadius: inline ? 14 : 16)

        if canRunPairExplore, let onPairScenarioExplore {
            Button {
                onPairScenarioExplore(scenarioId)
                Task {
                    await store.trackCompatibilityEvent(eventType: "compatibility_topic_select", payload: trackPayload)
                }
            } label: {
                cardLabel
            }
            .buttonStyle(.plain)
        } else {
            NavigationLink {
                CompatibilityEncyclopediaAnalyzeView(selection: analyzeSelection, store: store)
            } label: {
                cardLabel
            }
            .buttonStyle(.plain)
            .simultaneousGesture(TapGesture().onEnded {
                Task {
                    await store.trackCompatibilityEvent(eventType: "compatibility_topic_select", payload: trackPayload)
                }
            })
        }
    }
}

struct CompatibilityEncyclopediaAnalyzeView: View {
    let selection: CompatibilityEncyclopediaAnalyzeSelection
    let store: TodayFlowStore

    @State private var entryMode: AnalyzeEntryMode = .quick
    @State private var signFrom: ZodiacSunSign = .aries
    @State private var signTo: ZodiacSunSign = .libra
    @State private var birthDateA = Calendar.current.date(from: DateComponents(year: 1992, month: 3, day: 21)) ?? .now
    @State private var birthDateB = Calendar.current.date(from: DateComponents(year: 1994, month: 10, day: 15)) ?? .now
    @State private var name1 = ""
    @State private var name2 = ""
    @State private var quickCompatibilityContext: QuickCompatibilityContext?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var result: SignCompatibilityAPIResponse?
    @State private var echoByTarget: [String: BlockEcho] = [:]
    @State private var blockFeedback: [String: BlockEcho] = [:]
    @State private var deepOpenTracked = false

    private enum AnalyzeEntryMode: String, CaseIterable, Identifiable {
        case quick
        case precise

        var id: String { rawValue }

        var title: String {
            switch self {
            case .quick: return CompatibilityScreenChrome.analyzeQuickEntry
            case .precise: return CompatibilityScreenChrome.analyzePreciseEntry
            }
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                selectionBanner

                VStack(alignment: .leading, spacing: 14) {
                    Text(CompatibilityScreenChrome.analyzeTitle)
                        .font(.title2.bold())
                        .foregroundStyle(TodayFlowTheme.ink)

                    Picker("", selection: $entryMode) {
                        ForEach(AnalyzeEntryMode.allCases) { mode in
                            Text(mode.title).tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)

                    if entryMode == .quick {
                        quickEntryFields
                    } else {
                        preciseEntryFields
                    }

                    Button {
                        resetLearningMarks()
                        runDynamics()
                    } label: {
                        Label(isLoading ? CompatibilityScreenChrome.calculating : CompatibilityScreenChrome.analyzeRun, systemImage: "sparkles")
                            .font(.subheadline.weight(.semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(.white)
                    .background(
                        LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                    .disabled(isLoading)

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.roseClay)
                    }

                    if let result,
                       let model = CompatibilityExplorationModelBuilder.fromDynamics(response: result, selection: selection) {
                        CompatibilityExplorationResultView(
                            model: model,
                            store: store,
                            dynamicsResponse: result,
                            learning: SignCompatibilityLearningContext(
                                store: store,
                                surface: "analyze_dynamics",
                                formatId: selection.seriesId ?? selection.topicId ?? selection.readingId,
                                scenarioId: selection.seriesId ?? selection.topicId ?? selection.readingId,
                                fromSign: result.fromSign,
                                toSign: result.toSign,
                                score: Double(result.score),
                                echoByTarget: $echoByTarget,
                                blockFeedback: $blockFeedback,
                                deepOpenTracked: $deepOpenTracked,
                                onRebuild: { rebuildWithFeedback() },
                                isRebuilding: isLoading
                            )
                        )
                    } else if let result {
                        SignCompatibilityPanel(response: result)
                    }
                }
                .padding(22)
                .frame(maxWidth: .infinity, alignment: .leading)
                .todayFlowCompatSurface()
            }
            .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
        }
        .background(TodayBackground())
        .navigationTitle(selection.label)
        .navigationBarTitleDisplayMode(.inline)
    }

    @ViewBuilder
    private var selectionBanner: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(CompatibilityScreenChrome.analyzeInvestigation)
                .font(.caption.weight(.semibold))
                .textCase(.uppercase)
                .tracking(0.6)
                .foregroundStyle(TodayFlowTheme.sand)
            Text(selection.label)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(Array(selection.introBlocks.enumerated()), id: \.offset) { _, block in
                encyclopediaIntroBlock(block)
            }
            if !selection.scenarioBullets.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(selection.scenarioBullets, id: \.self) { bullet in
                        Text("• \(bullet)")
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 22)
    }

    @ViewBuilder
    private func encyclopediaIntroBlock(_ block: CompatibilityEncyclopediaIntroBlock) -> some View {
        switch block.kind {
        case "question":
            if let text = block.text, !text.isEmpty {
                Text(text)
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .fixedSize(horizontal: false, vertical: true)
            }
        case "bullet_list":
            if let items = block.items {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(items, id: \.self) { item in
                        Text("• \(item)")
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    }
                }
            }
        default:
            if let text = block.text, !text.isEmpty {
                Text(text)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    @ViewBuilder
    private var quickEntryFields: some View {
        Picker(CompatibilityScreenChrome.pickerYourSign, selection: $signFrom) {
            ForEach(ZodiacSunSign.allCases) { sign in
                Text(sign.title).tag(sign)
            }
        }
        Picker(CompatibilityScreenChrome.pickerPartnerSign, selection: $signTo) {
            ForEach(ZodiacSunSign.allCases) { sign in
                Text(sign.title).tag(sign)
            }
        }
        Picker(CompatibilityScreenChrome.pickerBetweenYou, selection: $quickCompatibilityContext) {
            Text(CompatibilityScreenChrome.contextUnspecified).tag(Optional<QuickCompatibilityContext>.none)
            ForEach(QuickCompatibilityContext.allCases) { ctx in
                Text(ctx.menuTitle).tag(Optional(ctx))
            }
        }
        optionalNameFields
    }

    @ViewBuilder
    private var preciseEntryFields: some View {
        DatePicker(CompatibilityScreenChrome.pickerYourBirthdate, selection: $birthDateA, displayedComponents: .date)
        DatePicker(CompatibilityScreenChrome.pickerPartnerBirthdate, selection: $birthDateB, displayedComponents: .date)
        if let a = SolarSignFromUTCDate.sign(for: birthDateA), let b = SolarSignFromUTCDate.sign(for: birthDateB) {
            Text(CompatibilityScreenChrome.sunSignsLine(a.title, b.title))
                .font(.subheadline.weight(.medium))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.8))
        }
        optionalNameFields
    }

    @ViewBuilder
    private var optionalNameFields: some View {
        TextField(CompatibilityScreenChrome.analyzeNameYou, text: $name1)
            .textFieldStyle(.roundedBorder)
        TextField(CompatibilityScreenChrome.analyzeNamePartner, text: $name2)
            .textFieldStyle(.roundedBorder)
    }

    private func resetLearningMarks() {
        echoByTarget = [:]
        blockFeedback = [:]
        deepOpenTracked = false
    }

    private func rebuildWithFeedback() {
        guard !blockFeedback.isEmpty else { return }
        runDynamics(includeBlockFeedback: true)
    }

    private func runDynamics(includeBlockFeedback: Bool = false) {
        isLoading = true
        errorMessage = nil
        let locale = CompatibilityScreenChrome.useRussian ? "ru" : "en"
        let trimmedName1 = name1.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedName2 = name2.trimmingCharacters(in: .whitespacesAndNewlines)
        let relationshipContext = quickCompatibilityContext?.rawValue
        let requestMode = entryMode
        let feedbackPayload: [String: String]? = includeBlockFeedback && !blockFeedback.isEmpty
            ? Dictionary(uniqueKeysWithValues: blockFeedback.map { ($0.key, $0.value.rawValue) })
            : nil

        let body: CompatibilityDynamicsRequestBody
        if entryMode == .precise {
            body = CompatibilityDynamicsRequestBody(
                mode: "precise",
                from_sign: nil,
                to_sign: nil,
                relationship_context: relationshipContext,
                generation: "llm",
                name_1: trimmedName1.isEmpty ? nil : trimmedName1,
                name_2: trimmedName2.isEmpty ? nil : trimmedName2,
                birth_date_1: Self.birthDateFormatter.string(from: birthDateA),
                birth_date_2: Self.birthDateFormatter.string(from: birthDateB),
                include_personalized: true,
                locale: locale,
                topic_id: selection.topicId,
                reading_id: selection.readingId,
                series_id: selection.seriesId,
                block_feedback: feedbackPayload
            )
        } else {
            body = CompatibilityDynamicsRequestBody(
                mode: "quick",
                from_sign: signFrom.rawValue,
                to_sign: signTo.rawValue,
                relationship_context: relationshipContext,
                generation: "llm",
                name_1: trimmedName1.isEmpty ? nil : trimmedName1,
                name_2: trimmedName2.isEmpty ? nil : trimmedName2,
                birth_date_1: nil,
                birth_date_2: nil,
                include_personalized: true,
                locale: locale,
                topic_id: selection.topicId,
                reading_id: selection.readingId,
                series_id: selection.seriesId,
                block_feedback: feedbackPayload
            )
        }

        Task {
            do {
                let response = try await TodayFlowAPIClient.shared.postCompatibilityDynamics(body: body)
                await MainActor.run {
                    result = response
                    isLoading = false
                }
                var payload: [String: JSONValue] = [
                    "selection_kind": .string(selection.selectionKind),
                    "selection_id": .string(selection.selectionId),
                    "mode": .string(requestMode.rawValue),
                    "from_sign": .string(response.fromSign),
                    "to_sign": .string(response.toSign),
                    "score": .number(Double(response.score)),
                    "surface": .string("analyze_dynamics"),
                ]
                if let topicId = selection.topicId { payload["topic_id"] = .string(topicId) }
                if let readingId = selection.readingId { payload["reading_id"] = .string(readingId) }
                if let seriesId = selection.seriesId { payload["series_id"] = .string(seriesId) }
                await store.trackCompatibilityEvent(eventType: "compatibility_view", payload: payload)
            } catch {
                await MainActor.run {
                    errorMessage = CompatibilityScreenChrome.analyzeLoadError
                    result = nil
                    isLoading = false
                }
            }
        }
    }

    private static let birthDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()
}

private extension CompatibilityEncyclopediaCategory {
    func analyzeSelection() -> CompatibilityEncyclopediaAnalyzeSelection {
        CompatibilityEncyclopediaAnalyzeSelection(
            label: title,
            selectionKind: "category",
            selectionId: id,
            topicId: analyzeParams.topic,
            readingId: analyzeParams.reading,
            seriesId: analyzeParams.series,
            introBlocks: introBlocks ?? [],
            scenarioBullets: []
        )
    }

    func topicSelectPayload(kind: String) -> [String: JSONValue] {
        var payload: [String: JSONValue] = [
            "selection_kind": .string(kind),
            "selection_id": .string(id),
        ]
        if let topic = analyzeParams.topic { payload["topic_id"] = .string(topic) }
        if let reading = analyzeParams.reading { payload["reading_id"] = .string(reading) }
        if let series = analyzeParams.series { payload["series_id"] = .string(series) }
        return payload
    }
}

private extension CompatibilityEncyclopediaReading {
    func analyzeSelection() -> CompatibilityEncyclopediaAnalyzeSelection {
        CompatibilityEncyclopediaAnalyzeSelection(
            label: title,
            selectionKind: "reading",
            selectionId: id,
            topicId: analyzeParams.topic,
            readingId: analyzeParams.reading,
            seriesId: analyzeParams.series,
            introBlocks: introBlocks ?? [],
            scenarioBullets: []
        )
    }

    func topicSelectPayload(kind: String) -> [String: JSONValue] {
        var payload: [String: JSONValue] = [
            "selection_kind": .string(kind),
            "selection_id": .string(id),
        ]
        if let topic = analyzeParams.topic { payload["topic_id"] = .string(topic) }
        if let reading = analyzeParams.reading { payload["reading_id"] = .string(reading) }
        if let series = analyzeParams.series { payload["series_id"] = .string(series) }
        return payload
    }
}

private extension CompatibilityEncyclopediaSeries {
    func analyzeSelection() -> CompatibilityEncyclopediaAnalyzeSelection {
        CompatibilityEncyclopediaAnalyzeSelection(
            label: title,
            selectionKind: "series",
            selectionId: id,
            topicId: analyzeParams.topic,
            readingId: analyzeParams.reading,
            seriesId: analyzeParams.series,
            introBlocks: introBlocks ?? [],
            scenarioBullets: scenarioBullets ?? []
        )
    }

    func topicSelectPayload(kind: String) -> [String: JSONValue] {
        var payload: [String: JSONValue] = [
            "selection_kind": .string(kind),
            "selection_id": .string(id),
        ]
        if let topic = analyzeParams.topic { payload["topic_id"] = .string(topic) }
        if let reading = analyzeParams.reading { payload["reading_id"] = .string(reading) }
        if let series = analyzeParams.series { payload["series_id"] = .string(series) }
        return payload
    }
}

private var toolbarTrailingPlacement: ToolbarItemPlacement {
    TodayFlowToolbar.trailing
}

private extension View {
    /// Основные панели на экране совместимости: как у полированного профиля/Today.
    func todayFlowCompatSurface(cornerRadius: CGFloat = 28) -> some View {
        self
            .background(
                LinearGradient(
                    colors: [Color.white.opacity(0.9), TodayFlowTheme.paper.opacity(0.74)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
            }
            .shadow(color: TodayFlowTheme.gold.opacity(0.08), radius: 12, y: 4)
    }

    /// Вложенные карточки внутри панелей.
    func todayFlowCompatInsetCard(cornerRadius: CGFloat = 20) -> some View {
        self
            .background(
                LinearGradient(
                    colors: [Color.white.opacity(0.86), TodayFlowTheme.paper.opacity(0.62)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.12), lineWidth: 1)
            }
    }
}

private struct CompatibilityProfileCard: View {
    let title: String
    let subtitle: String
    let detail: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(subtitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(detail)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.66))
        }
        .padding(18)
        .frame(maxWidth: .infinity, minHeight: 160, alignment: .topLeading)
        .todayFlowCompatSurface(cornerRadius: 24)
    }
}

private struct RelationModeRow: View {
    let mode: CompatibilityView.RelationMode
    let isSelected: Bool

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Circle()
                .fill(isSelected ? TodayFlowTheme.sunset : Color.black.opacity(0.08))
                .frame(width: 10, height: 10)
                .padding(.top, 7)

            Text(mode.title)
                .font(.subheadline.weight(.semibold))

            Spacer()
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(isSelected ? TodayFlowTheme.sunset.opacity(0.1) : Color.white.opacity(0.62))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct CompatibilityInsightRow: View {
    let title: String
    let text: String

    var bodyView: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatInsetCard(cornerRadius: 18)
    }

    var body: some View { bodyView }
}

#Preview {
    CompatibilityView(store: TodayFlowStore())
}

/// UI chrome for sign compatibility panel — follows API `content_locale` (matches Accept-Language).
private enum SignCompatPanelChrome {
    static func isRu(_ locale: String?) -> Bool {
        (locale ?? "").lowercased().hasPrefix("ru")
    }

    static func eyebrow(_ locale: String?) -> String { isRu(locale) ? "Совместимость" : "Compatibility" }
    static func overallIndex(_ locale: String?) -> String { isRu(locale) ? "общий индекс" : "overall index" }
    static func attraction(_ locale: String?) -> String { isRu(locale) ? "Притяжение" : "Attraction" }
    static func stability(_ locale: String?) -> String { isRu(locale) ? "Стабильность" : "Stability" }
    static func conflicts(_ locale: String?) -> String {
        isRu(locale) ? "Конфликты (чинят ли контакт)" : "Conflicts (repair)"
    }
    static func sexuality(_ locale: String?) -> String { isRu(locale) ? "Сексуальность" : "Sexuality" }
    static func betweenYou(_ locale: String?) -> String { isRu(locale) ? "Что между вами происходит" : "What is happening between you" }
    static func layers(_ locale: String?) -> String { isRu(locale) ? "Основные слои" : "Core layers" }
    static func risk(_ locale: String?) -> String { isRu(locale) ? "Риск" : "Risk" }
    static func action(_ locale: String?) -> String { isRu(locale) ? "Как действовать" : "What to do" }
    static func roles(_ locale: String?) -> String { isRu(locale) ? "Роли в паре" : "Roles in the pair" }
    static func you(_ locale: String?) -> String { isRu(locale) ? "Ты" : "You" }
    static func partner(_ locale: String?) -> String { isRu(locale) ? "Партнёр" : "Partner" }
    static func whatNext(_ locale: String?) -> String { isRu(locale) ? "Что с этим делать" : "What to do with this" }
    static func fullTextPaywall(_ locale: String?) -> String {
        isRu(locale) ? "Полный текст абзацев — в подписке." : "Full paragraph text is included with subscription."
    }
    static func strength(_ locale: String?) -> String { isRu(locale) ? "Сильная сторона" : "Strength" }
    static func tension(_ locale: String?) -> String { isRu(locale) ? "Напряжение" : "Tension" }
    static func nextStep(_ locale: String?) -> String { isRu(locale) ? "Следующий шаг" : "Next step" }
    static func funnelTitle(_ locale: String?) -> String { isRu(locale) ? "Воронка точности" : "Accuracy funnel" }
    static func funnelDomains(_ locale: String?) -> String { isRu(locale) ? "Сферы" : "Life areas" }
    static func funnelDynamics(_ locale: String?) -> String { isRu(locale) ? "Асимметрия" : "Asymmetry" }
    static func funnelTime(_ locale: String?) -> String { isRu(locale) ? "Время" : "Timeline" }
    static func funnelRisk(_ locale: String?) -> String { isRu(locale) ? "Пороги риска" : "Risk bands" }
    static func funnelRiskBandOk(_ locale: String?) -> String { isRu(locale) ? "Норма" : "Stable" }
    static func funnelRiskBandShift(_ locale: String?) -> String { isRu(locale) ? "Сдвиг" : "Shift" }
    static func funnelRiskBandBreak(_ locale: String?) -> String { isRu(locale) ? "Риск" : "Break" }
    static func confidenceShort(_ locale: String?) -> String { isRu(locale) ? "уверенность" : "confidence" }
    static func funnelTodayTitle(_ locale: String?) -> String {
        isRu(locale) ? "Согласовано с дневным ритмом (Today)" : "Aligned with your daily rhythm (Today)"
    }
    static func funnelTodayFocus(_ locale: String?) -> String { isRu(locale) ? "Фокус дня" : "Today focus" }
    static func funnelTodayDo(_ locale: String?) -> String { isRu(locale) ? "Усилить" : "Lean into" }
    static func funnelTodayAvoid(_ locale: String?) -> String { isRu(locale) ? "Осторожнее" : "Go easy on" }
    static func funnelBaseModel(_ locale: String?) -> String {
        isRu(locale) ? "Глубинный слой (Base Model)" : "Deep layer (Base Model)"
    }
    static func funnelBasePull(_ locale: String?) -> String { isRu(locale) ? "Притяжение и напряжение" : "Pull vs tension" }
    static func funnelBaseAttrDep(_ locale: String?) -> String { isRu(locale) ? "Притяжение и зависимость" : "Attraction vs dependency" }
    static func funnelBaseConflict(_ locale: String?) -> String { isRu(locale) ? "Цикл конфликта" : "Conflict cycle" }
    static func funnelBaseSex(_ locale: String?) -> String { isRu(locale) ? "Сексуальный мотор" : "Sexual engine" }
    static func funnelBaseActions(_ locale: String?) -> String { isRu(locale) ? "Действия в ладу с днём" : "Actions aligned with today" }
}

private struct CompatibilityScoreRing: View {
    let score: Int
    let overallLabel: String

    var body: some View {
        let pct = min(100, max(0, score))
        ZStack {
            Circle()
                .stroke(Color.black.opacity(0.07), lineWidth: 10)
                .frame(width: 104, height: 104)
            Circle()
                .trim(from: 0, to: CGFloat(pct) / 100)
                .stroke(TodayFlowTheme.sunset, style: StrokeStyle(lineWidth: 10, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .frame(width: 104, height: 104)
            Circle()
                .fill(
                    LinearGradient(
                        colors: [Color(red: 1, green: 0.992, blue: 0.984), Color(red: 0.973, green: 0.949, blue: 0.910)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(width: 74, height: 74)
            VStack(spacing: 2) {
                Text("\(pct)%")
                    .font(.system(size: 20, weight: .bold, design: .rounded))
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(overallLabel.uppercased())
                    .font(.system(size: 9, weight: .semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .multilineTextAlignment(.center)
            }
        }
        .frame(width: 104, height: 104)
    }
}

@ViewBuilder
func compatibilityFunnelArtifactSection(_ fa: CompatibilityFunnelArtifact, locale: String?) -> some View {
    DisclosureGroup {
        VStack(alignment: .leading, spacing: 12) {
            Text(fa.accuracyLabel)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(fa.scoreSemantics)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
            Text(fa.confidenceNote)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                .fixedSize(horizontal: false, vertical: true)

            if let ta = fa.todayAlignment {
                let showToday = !ta.focusLabel.isEmpty || !ta.doEcho.isEmpty || !ta.avoidEcho.isEmpty || !ta.syncNote.isEmpty
                if showToday {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(SignCompatPanelChrome.funnelTodayTitle(locale))
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Color(red: 0.09, green: 0.45, blue: 0.21))
                        if !ta.syncNote.isEmpty {
                            Text(ta.syncNote)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !ta.focusLabel.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelTodayFocus(locale)): \(ta.focusLabel)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !ta.doEcho.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelTodayDo(locale)): \(ta.doEcho)")
                                .font(.footnote)
                                .foregroundStyle(Color(red: 0.08, green: 0.33, blue: 0.18))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !ta.avoidEcho.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelTodayAvoid(locale)): \(ta.avoidEcho)")
                                .font(.footnote)
                                .foregroundStyle(Color(red: 0.6, green: 0.2, blue: 0.07))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.green.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                }
            }

            if let bm = fa.llmBaseModel {
                let showBase = !bm.pullVsTension.isEmpty || !bm.attractionOrDependency.isEmpty
                    || !bm.conflictCycle.isEmpty || !bm.sexualDynamic.isEmpty || !bm.alignedActionsHint.isEmpty
                if showBase {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(SignCompatPanelChrome.funnelBaseModel(locale))
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sunset)
                        if !bm.pullVsTension.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelBasePull(locale)): \(bm.pullVsTension)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !bm.attractionOrDependency.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelBaseAttrDep(locale)): \(bm.attractionOrDependency)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !bm.conflictCycle.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelBaseConflict(locale)): \(bm.conflictCycle)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !bm.sexualDynamic.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelBaseSex(locale)): \(bm.sexualDynamic)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if !bm.alignedActionsHint.isEmpty {
                            Text("\(SignCompatPanelChrome.funnelBaseActions(locale)): \(bm.alignedActionsHint)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.55))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                }
            }

            Text(SignCompatPanelChrome.funnelDomains(locale))
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(fa.domainScores.filter(\.applicable), id: \.domainId) { d in
                let confPct = Int((d.confidence * 100).rounded())
                VStack(alignment: .leading, spacing: 4) {
                    HStack(alignment: .firstTextBaseline) {
                        Text(d.label)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                        Spacer(minLength: 8)
                        Text("\(d.scorePct)% · \(confPct)% \(SignCompatPanelChrome.confidenceShort(locale))")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sunset)
                    }
                    Text(d.basis)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                    Text("↑ \(d.raises.joined(separator: " "))")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                        .fixedSize(horizontal: false, vertical: true)
                    Text("↓ \(d.lowers.joined(separator: " "))")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                        .fixedSize(horizontal: false, vertical: true)
                    Text("\(SignCompatPanelChrome.action(locale)): \(d.improve.joined(separator: " "))")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.5))
                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            }

            Text(SignCompatPanelChrome.funnelDynamics(locale))
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(fa.dynamicCore.youLine)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
            Text(fa.dynamicCore.partnerLine)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
            Text(fa.dynamicCore.controlPattern)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                .fixedSize(horizontal: false, vertical: true)
            Text(fa.dynamicCore.clarityNote)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)

            Text(SignCompatPanelChrome.funnelTime(locale))
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(fa.timeline, id: \.phaseId) { t in
                VStack(alignment: .leading, spacing: 4) {
                    Text(t.headline).font(.subheadline.weight(.semibold))
                    Text(t.body).font(.caption).foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.vertical, 4)
            }

            Text(SignCompatPanelChrome.funnelRisk(locale))
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(fa.riskBands, id: \.level) { b in
                VStack(alignment: .leading, spacing: 4) {
                    Text(b.headline).font(.caption.weight(.semibold))
                    Text("\(SignCompatPanelChrome.funnelRiskBandOk(locale)): \(b.whenOk)").font(.caption2).foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                    Text("\(SignCompatPanelChrome.funnelRiskBandShift(locale)): \(b.whenShifts)").font(.caption2).foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                    Text("\(SignCompatPanelChrome.funnelRiskBandBreak(locale)): \(b.whenBreaks)").font(.caption2).foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                }
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.42))
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
        }
        .padding(.top, 8)
    } label: {
        Text(SignCompatPanelChrome.funnelTitle(locale))
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(TodayFlowTheme.ink)
    }
    .padding(12)
    .background(Color.white.opacity(0.35))
    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
}

private struct SignCompatibilityPanel: View {
    let response: SignCompatibilityAPIResponse

    private var loc: String? { response.contentLocale }

    var body: some View {
        Group {
            if let surface = response.productSurface {
                productSurfaceContent(surface)
            } else {
                legacyContent
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatInsetCard(cornerRadius: 22)
    }

    @ViewBuilder
    private func productSurfaceContent(_ surface: SignCompatibilityProductSurface) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 14) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(SignCompatPanelChrome.eyebrow(loc))
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text("\(response.fromSignName) × \(response.toSignName)")
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 8)
                VStack(spacing: 8) {
                    CompatibilityScoreRing(score: response.score, overallLabel: SignCompatPanelChrome.overallIndex(loc))
                    Text(surface.scoreTagline)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                        .frame(maxWidth: 132)
                }
            }

            LazyVGrid(columns: [GridItem(.flexible(), spacing: 8), GridItem(.flexible(), spacing: 8)], spacing: 8) {
                subscoreMetric(title: SignCompatPanelChrome.attraction(loc), value: surface.subscores.attraction)
                subscoreMetric(title: SignCompatPanelChrome.stability(loc), value: surface.subscores.stability)
                subscoreMetric(title: SignCompatPanelChrome.conflicts(loc), value: surface.subscores.conflicts)
                subscoreMetric(title: SignCompatPanelChrome.sexuality(loc), value: surface.subscores.sexuality)
            }

            if let funnel = response.funnelArtifact {
                funnelArtifactSection(funnel)
            }

            VStack(alignment: .leading, spacing: 8) {
                Text(SignCompatPanelChrome.betweenYou(loc))
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                ForEach(Array(surface.overviewParagraphs.enumerated()), id: \.offset) { _, line in
                    Text(line)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                Text(SignCompatPanelChrome.layers(loc))
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                ForEach(surface.blocks, id: \.key) { block in
                    DisclosureGroup {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(block.takeaway)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(block.detail)
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                            Text("\(SignCompatPanelChrome.risk(loc)): \(block.risk)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.roseClay.opacity(0.9))
                                .fixedSize(horizontal: false, vertical: true)
                            Text("\(SignCompatPanelChrome.action(loc)): \(block.action)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(.top, 6)
                    } label: {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(block.title)
                                .font(.subheadline.weight(.semibold))
                            Text(block.subtitle)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                        }
                    }
                    .padding(10)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(block.key == "sexuality" ? TodayFlowTheme.sunset.opacity(0.08) : Color.white.opacity(0.38))
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(block.key == "sexuality" ? TodayFlowTheme.sunset.opacity(0.42) : Color.clear, lineWidth: 1.5)
                    )
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Text(SignCompatPanelChrome.roles(loc))
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                HStack(alignment: .top, spacing: 12) {
                    bulletColumn(title: SignCompatPanelChrome.you(loc), lines: surface.roles.youBullets)
                    bulletColumn(title: SignCompatPanelChrome.partner(loc), lines: surface.roles.partnerBullets)
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                Text(SignCompatPanelChrome.whatNext(loc))
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                ForEach(surface.scenarios, id: \.id) { group in
                    VStack(alignment: .leading, spacing: 6) {
                        Text(group.title)
                            .font(.subheadline.weight(.semibold))
                        ForEach(Array(group.bullets.enumerated()), id: \.offset) { _, bullet in
                            Text("• \(bullet)")
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.55))
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                }
            }

            legacyParagraphs

            if !response.isPaid, !response.fullParagraphs.isEmpty {
                Text(SignCompatPanelChrome.fullTextPaywall(loc))
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
            }
        }
    }

    private func funnelArtifactSection(_ fa: CompatibilityFunnelArtifact) -> some View {
        compatibilityFunnelArtifactSection(fa, locale: loc)
    }

    private func subscoreMetric(title: String, value: Int) -> some View {
        let v = min(100, max(0, value))
        return VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .fixedSize(horizontal: false, vertical: true)
            Text("\(v)%")
                .font(.subheadline.weight(.bold))
                .foregroundStyle(TodayFlowTheme.sunset)
            TodayFlowSphereSliderTrack(
                value: v,
                tint: TodayFlowTheme.sunset,
                accessibilityTitle: title,
                density: .compact
            )
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func bulletColumn(title: String, lines: [String]) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            ForEach(Array(lines.enumerated()), id: \.offset) { _, line in
                Text("• \(line)")
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.white.opacity(0.45))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    @ViewBuilder
    private var legacyContent: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("\(response.fromSignName) · \(response.toSignName)")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(response.summary)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                }
                Spacer()
                Text("\(response.score)%")
                    .font(.system(size: 32, weight: .bold, design: .rounded))
                    .foregroundStyle(TodayFlowTheme.sunset)
            }

            if let q = response.quickReading {
                VStack(alignment: .leading, spacing: 8) {
                    if let headline = q.headline, !headline.isEmpty {
                        Text(headline)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                    }
                    if let s = q.strongest, !s.isEmpty {
                        CompatibilityInsightRow(title: SignCompatPanelChrome.strength(loc), text: s)
                    }
                    if let f = q.friction, !f.isEmpty {
                        CompatibilityInsightRow(title: SignCompatPanelChrome.tension(loc), text: f)
                    }
                    if let n = q.nextStep, !n.isEmpty {
                        CompatibilityInsightRow(title: SignCompatPanelChrome.nextStep(loc), text: n)
                    }
                }
            }

            legacyParagraphs

            if !response.isPaid, !response.fullParagraphs.isEmpty {
                Text(CompatibilityScreenChrome.legacyFullPaywall)
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
            }
        }
    }

    @ViewBuilder
    private var legacyParagraphs: some View {
        let paragraphs = response.isPaid ? response.fullParagraphs : (response.freeParagraphs.isEmpty ? response.fullParagraphs : response.freeParagraphs)
        if !paragraphs.isEmpty {
            VStack(alignment: .leading, spacing: 10) {
                Text(CompatibilityScreenChrome.legacyMoreText)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                ForEach(Array(paragraphs.prefix(6).enumerated()), id: \.offset) { _, line in
                    Text(line)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }
}

private struct CompatibilityResultSection: View {
    let result: CompatibilityComparisonResponse
    let relationMode: CompatibilityView.RelationMode
    let activeFormatId: String
    let store: TodayFlowStore
    var onOpenGuidance: (() -> Void)? = nil
    var onScenarioSwitch: ((String) -> Void)? = nil
    var onRefresh: (() -> Void)? = nil
    var refreshing: Bool = false

    var body: some View {
        let model = CompatibilityExplorationModelBuilder.fromPairCompare(
            result: result,
            formatId: activeFormatId
        )
        VStack(alignment: .leading, spacing: 14) {
            CompatibilityExplorationResultView(
                model: model,
                store: store,
                pairResponse: result,
                onPairScenarioSwitch: onScenarioSwitch,
                onPairRefresh: onRefresh,
                pairRefreshing: refreshing
            )

            if onOpenGuidance != nil {
                Button(CompatibilityScreenChrome.openGuidanceCta) {
                    let l1 = result.profile1?.label.flatMap { $0.isEmpty ? nil : $0 } ?? (CompatibilityScreenChrome.useRussian ? "Профиль 1" : "Profile 1")
                    let l2 = result.profile2?.label.flatMap { $0.isEmpty ? nil : $0 } ?? (CompatibilityScreenChrome.useRussian ? "Профиль 2" : "Profile 2")
                    let pair = "\(l1) × \(l2)"
                    let thesis = (result.compatibility.editorial?.pairThesis ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                    let summaryLine = (result.compatibility.summary ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                    let displayScore = result.scenarioContext?.displayScore ?? result.compatibility.overallScore
                    let tag: String = {
                        if !thesis.isEmpty { return String(thesis.prefix(400)) }
                        if !summaryLine.isEmpty { return String(summaryLine.prefix(400)) }
                        return CompatibilityScreenChrome.useRussian ? "Краткий вектор связи." : "Connection snapshot."
                    }()
                    let ru = CompatibilityScreenChrome.useRussian
                    var lines: [String] = []
                    lines.append(
                        ru
                            ? "Совместимость: \(pair). \(tag) (общий индекс \(displayScore)%)."
                            : "Compatibility: \(pair). \(tag) (overall index \(displayScore)%)."
                    )
                    if let fa = result.funnelArtifact {
                        let label = fa.accuracyLabel.trimmingCharacters(in: .whitespacesAndNewlines)
                        if !label.isEmpty {
                            lines.append(ru ? "Уровень: \(label)." : "Tier: \(label).")
                        }
                    }
                    lines.append(
                        ru
                            ? "Мой вопрос к раскладу: что мне важно понять в нашей динамике на ближайшие 2–3 недели и какой один шаг сейчас наиболее честный?"
                            : "My question for the spread: what do I need to understand about our dynamic over the next 2–3 weeks, and what one step is most honest right now?"
                    )
                    let q = lines.joined(separator: "\n")
                    let role: String? = relationMode == .romantic ? "partner" : nil
                    store.stageGuidanceHubCompatPrefill(
                        TodayFlowStore.GuidanceHubCompatPrefill(
                            suggestedQuestion: q,
                            spreadId: "guidance_relationship_five",
                            topicId: "relationships",
                            relationshipRoleId: role,
                            outcomeId: "next_step"
                        )
                    )
                    onOpenGuidance?()
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatSurface()
    }
}

private struct CompatibilityAspectCard: View {
    let title: String
    let text: String
    let score: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                Spacer()
                Text("\(score)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCompatInsetCard(cornerRadius: 20)
    }
}
