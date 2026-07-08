import SwiftUI

private enum ExploreHubChrome {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var navTitle: String { ru ? "Обзор" : "Overview" }
    static var heroTitle: String { ru ? "Куда идти дальше" : "Where to go next" }
    static var heroBody: String {
        ru
            ? "Быстрые входы в ключевые сценарии. Если блок ещё в работе, он помечен «Скоро»."
            : "Quick entry points. If a block is still in progress, it’s marked “Coming soon”."
    }
    static var sectionRhythm: String { ru ? "Ритм и карты" : "Rhythm and maps" }
    static var sectionGuidance: String { ru ? "Разбор и практики" : "Guidance and practices" }
    static var sectionAstro: String { ru ? "Астро и связи" : "Astro and relationships" }
    static var sectionAccount: String { ru ? "Вопросы и профиль" : "Questions and profile" }
    static var comingSoon: String { ru ? "Скоро" : "Soon" }
}

struct ExploreHubView: View {
    let openRoute: (String) -> Void

    private let columns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12),
    ]

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 22) {
                    header

                    hubSection(title: ExploreHubChrome.sectionRhythm, items: Self.rhythmItems)
                    hubSection(title: ExploreHubChrome.sectionGuidance, items: Self.tarotItems)
                    hubSection(title: ExploreHubChrome.sectionAstro, items: Self.astroItems)
                    hubSection(title: ExploreHubChrome.sectionAccount, items: Self.accountItems)
                }
                .padding(.horizontal, 18)
                .padding(.top, 8)
                .padding(.bottom, 32)
            }
        }
        .navigationTitle(ExploreHubChrome.navTitle)
        .todayflowNavigationBarTitleDisplayModeLarge()
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(ExploreHubChrome.heroTitle)
                .font(.title2.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(ExploreHubChrome.heroBody)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 26, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .stroke(TodayFlowTheme.contour, lineWidth: 1)
        )
    }

    private func hubSection(title: String, items: [NativeHubItem]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
                .tracking(0.5)

            LazyVGrid(columns: columns, spacing: 12) {
                ForEach(items) { item in
                    Button {
                        if item.isEnabled {
                            openRoute(item.routeKey)
                        }
                    } label: {
                        VStack(alignment: .leading, spacing: 8) {
                            ZStack {
                                Circle()
                                    .fill(item.tint.opacity(0.2))
                                    .frame(width: 40, height: 40)
                                Image(systemName: item.systemImage)
                                    .font(.body.weight(.semibold))
                                    .foregroundStyle(item.tint)
                            }
                            Text(item.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                                .multilineTextAlignment(.leading)
                                .lineLimit(2)
                                .fixedSize(horizontal: false, vertical: true)
                            Text(item.subtitle)
                                .font(.caption2)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                .multilineTextAlignment(.leading)
                                .lineLimit(2)
                            if !item.isEnabled {
                                Text(ExploreHubChrome.comingSoon)
                                    .font(.caption2.weight(.semibold))
                                    .foregroundStyle(item.tint)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(14)
                        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20, style: .continuous)
                                .stroke(TodayFlowTheme.contour.opacity(0.9), lineWidth: 1)
                        )
                        .shadow(color: Color.black.opacity(0.04), radius: 8, x: 0, y: 4)
                    }
                    .buttonStyle(.plain)
                    .opacity(item.isEnabled ? 1 : 0.7)
                }
            }
        }
    }
}

private struct NativeHubItem: Identifiable {
    var id: String { routeKey + title }
    let routeKey: String
    let title: String
    let subtitle: String
    let systemImage: String
    let tint: Color
    let isEnabled: Bool
}

extension ExploreHubView {
    fileprivate static var rhythmItems: [NativeHubItem] {
        let ru = ExploreHubChrome.ru
        return [
            .init(
                routeKey: "today",
                title: ru ? "Сегодня" : "Today",
                subtitle: ru ? "Главный дневной поток, кольца, карты, чек-ины" : "Main daily flow, rings, cards, check-ins",
                systemImage: "sun.max.fill",
                tint: TodayFlowTheme.accent,
                isEnabled: true
            ),
            .init(
                routeKey: "calendar",
                title: ru ? "Календарь" : "Calendar",
                subtitle: ru ? "Месяц, стрики, привычки, аскезы, аффирмации" : "Month, streaks, habits, ascetics, affirmations",
                systemImage: "calendar",
                tint: TodayFlowTheme.accent,
                isEnabled: true
            ),
            .init(
                routeKey: "goals",
                title: ru ? "Цели" : "Goals",
                subtitle: ru ? "Недельные и месячные фокусы" : "Weekly and monthly focus",
                systemImage: "scope",
                tint: Color(red: 0.2, green: 0.45, blue: 0.55),
                isEnabled: true
            ),
            .init(
                routeKey: "calendar",
                title: ru ? "Прогресс и дневник" : "Progress and diary",
                subtitle: ru
                    ? "Дневник, автоинсайты и недельный пульс — внутри календаря"
                    : "Journal, auto-insights, and weekly pulse—inside Calendar",
                systemImage: "chart.line.uptrend.xyaxis",
                tint: Color(red: 0.85, green: 0.55, blue: 0.2),
                isEnabled: true
            ),
            .init(
                routeKey: "calendar",
                title: ru ? "Привычки" : "Habits",
                subtitle: ru ? "Уже ведутся нативно в календаре" : "Logged natively inside Calendar",
                systemImage: "repeat.circle.fill",
                tint: TodayFlowTheme.accent,
                isEnabled: true
            ),
            .init(
                routeKey: "calendar",
                title: ru ? "Аффирмации" : "Affirmations",
                subtitle: ru ? "Каталог в блоке карт" : "Catalog in the maps block",
                systemImage: "text.quote",
                tint: Color(red: 0.55, green: 0.35, blue: 0.65),
                isEnabled: true
            ),
        ]
    }

    fileprivate static var tarotItems: [NativeHubItem] {
        let ru = ExploreHubChrome.ru
        return [
            .init(
                routeKey: "tarot",
                title: ru ? "Центр разборов" : "Guidance",
                subtitle: ru ? "Вопросы, карта дня и таро в одном контуре" : "Questions, daily card, and tarot in one lane",
                systemImage: "suit.club.fill",
                tint: Color(red: 0.35, green: 0.25, blue: 0.45),
                isEnabled: true
            ),
            .init(
                routeKey: "tarot",
                title: ru ? "Карта дня" : "Daily card",
                subtitle: ru ? "Нативный вход в ежедневную карту" : "Native entry to the daily card",
                systemImage: "sparkles",
                tint: TodayFlowTheme.accent,
                isEnabled: true
            ),
            .init(
                routeKey: "practices",
                title: ru ? "Практики" : "Practices",
                subtitle: ru ? "Каталог, серии, лимиты и подборки" : "Catalog, series, limits, and picks",
                systemImage: "figure.mind.and.body",
                tint: Color(red: 0.2, green: 0.5, blue: 0.55),
                isEnabled: true
            ),
            .init(
                routeKey: "practices_history",
                title: ru ? "История практик" : "Practice history",
                subtitle: ru ? "Прогресс и выполненные практики" : "Progress and completed practices",
                systemImage: "clock.arrow.circlepath",
                tint: Color(red: 0.35, green: 0.45, blue: 0.5),
                isEnabled: true
            ),
            .init(
                routeKey: "questions",
                title: ru ? "Наблюдения в дневнике" : "Journal prompts",
                subtitle: ru ? "Вопросы и рефлексия" : "Questions and reflection",
                systemImage: "square.and.pencil",
                tint: Color(red: 0.4, green: 0.35, blue: 0.3),
                isEnabled: true
            ),
        ]
    }

    fileprivate static var astroItems: [NativeHubItem] {
        let ru = ExploreHubChrome.ru
        return [
            .init(
                routeKey: "compatibility",
                title: ru ? "Совместимость" : "Compatibility",
                subtitle: ru ? "Полный сценарий по двум профилям" : "Full flow with two profiles",
                systemImage: "heart.circle.fill",
                tint: Color(red: 0.75, green: 0.3, blue: 0.4),
                isEnabled: true
            ),
            .init(
                routeKey: "profile",
                title: ru ? "Профиль" : "Profile",
                subtitle: ru ? "Персональный слой, аккаунт и данные" : "Personal layer, account, and data",
                systemImage: "person.crop.circle.fill",
                tint: TodayFlowTheme.accent,
                isEnabled: true
            ),
            .init(
                routeKey: "natal",
                title: ru ? "Натальная карта" : "Natal chart",
                subtitle: ru ? "Колесо и интерпретации в профиле" : "Wheel and interpretations in Profile",
                systemImage: "circle.hexagongrid.fill",
                tint: Color(red: 0.55, green: 0.35, blue: 0.2),
                isEnabled: true
            ),
            .init(
                routeKey: "calendar",
                title: ru ? "Цикл и неделя" : "Cycle and weekly",
                subtitle: ru ? "Обзор недели и цикла — в разработке" : "Week and cycle overview—next layer",
                systemImage: "calendar.day.timeline.left",
                tint: Color(red: 0.35, green: 0.4, blue: 0.65),
                isEnabled: false
            ),
        ]
    }

    fileprivate static var accountItems: [NativeHubItem] {
        let ru = ExploreHubChrome.ru
        return [
            .init(
                routeKey: "questions",
                title: ru ? "Вопросы" : "Questions",
                subtitle: ru ? "Любовь, деньги, состояние и паттерны" : "Love, money, state, and patterns",
                systemImage: "questionmark.circle.fill",
                tint: Color(red: 0.35, green: 0.45, blue: 0.65),
                isEnabled: true
            ),
            .init(
                routeKey: "profile",
                title: ru ? "Аккаунт и профиль" : "Account and profile",
                subtitle: ru ? "Подписка, данные, персональный слой" : "Subscription, identity, personal layer",
                systemImage: "gearshape.fill",
                tint: Color(red: 0.4, green: 0.42, blue: 0.48),
                isEnabled: true
            ),
            .init(
                routeKey: "profile_summary",
                title: ru ? "Сводка профиля" : "Profile summary",
                subtitle: ru ? "Быстрый вход перед «Сегодня»: главное за день" : "Quick stop before Today: the day’s essentials",
                systemImage: "person.text.rectangle",
                tint: Color(red: 0.65, green: 0.5, blue: 0.25),
                isEnabled: true
            ),
            .init(
                routeKey: "today",
                title: ru ? "Прогресс" : "Progress",
                subtitle: ru ? "Кольца в «Я сегодня». Раздел расширяется" : "Rings in Today—section growing",
                systemImage: "circle.circle",
                tint: Color(red: 0.65, green: 0.5, blue: 0.25),
                isEnabled: false
            ),
            .init(
                routeKey: "profile",
                title: ru ? "Каталог и отчёты" : "Catalog and reports",
                subtitle: ru ? "Как на сайте — нативный слой в разработке" : "Like the site—native layer in progress",
                systemImage: "books.vertical.fill",
                tint: Color(red: 0.4, green: 0.35, blue: 0.55),
                isEnabled: false
            ),
        ]
    }
}

#Preview {
    NavigationStack {
        ExploreHubView(openRoute: { _ in })
    }
}
