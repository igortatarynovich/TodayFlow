import SwiftUI

enum TodayFlowTheme {
    /// Терракота / rose gold — основной продуктовый акцент (паритет с веб `#d68e7a`)
    static let accent = Color(red: 214 / 255, green: 142 / 255, blue: 122 / 255)
    /// Мягкое золото для метрик / вторичных маркеров (не дублировать rose gold везде)
    static let mutedGold = Color(red: 184 / 255, green: 148 / 255, blue: 108 / 255)
    /// Тёплый amber для предупреждений — не «кровавый» красный
    static let warmAmber = Color(red: 212 / 255, green: 152 / 255, blue: 72 / 255)
    /// Тёплый сепия-чернильный текст
    static let ink = Color(red: 45 / 255, green: 36 / 255, blue: 28 / 255)
    static let secondaryInk = ink.opacity(0.62)
    static let contour = Color.black.opacity(0.10)
    static let cardStrong = Color.white.opacity(0.88)
    static let accentSoft = accent.opacity(0.35)

    // MARK: Семантика палитры (calm premium wellness — один словарь для экранов)

    /// Фон страницы / холста
    static var background: Color { paper }
    /// Главные карточки и панели
    static var surface: Color { cardStrong }
    /// Активные состояния, ключевые обводки
    static var primaryAccent: Color { accent }
    /// Проценты, важные числовые маркеры
    static var secondaryAccent: Color { mutedGold }
    /// Основной текст (cacao / espresso)
    static var textPrimary: Color { ink }
    /// Подписи, вторичный текст
    static var textSecondary: Color { secondaryInk }
    /// Бордеры в духе rose gold, низкая непрозрачность
    static var borderRoseSubtle: Color { accent.opacity(0.22) }
    static let sky = Color(red: 0.55, green: 0.72, blue: 0.82)
    static let card = Color.white.opacity(0.72)
    /// Кремовый фон экрана `#fff9f5`
    static let paper = Color(red: 255 / 255, green: 249 / 255, blue: 245 / 255)
    /// Лёгкий персиковый туман под карточки
    static let mist = Color(red: 252 / 255, green: 238 / 255, blue: 232 / 255)
    static let sand = Color(red: 0.55, green: 0.42, blue: 0.35)
    static let gold = accent
    static let sunset = Color(red: 214 / 255, green: 142 / 255, blue: 122 / 255)
    static let ember = Color(red: 0.67, green: 0.28, blue: 0.26)
    static let moss = Color(red: 0.39, green: 0.54, blue: 0.42)
    static let sage = moss
    static let twilight = Color(red: 0.32, green: 0.40, blue: 0.66)
    static let roseClay = Color(red: 0.60, green: 0.30, blue: 0.24)

    // Третий слой: единая сетка внутренних отступов (12 / 16 / 20 / 24)
    enum Layout {
        static let s1: CGFloat = 12
        static let s2: CGFloat = 16
        static let s3: CGFloat = 20
        static let s4: CGFloat = 24
        /// Внутри карточек и панелей
        static let inset: CGFloat = s3
        static let insetTight: CGFloat = s2
        static let blockGap: CGFloat = s2
        /// Радиус главных карточек (мобильный канон 24–32)
        static let cardRadiusLarge: CGFloat = 28
        static let cardRadiusMedium: CGFloat = 24
    }

    /// Длительности и пружина без bounce — единые правила motion по продукту
    enum Motion {
        static let microSeconds: Double = 0.15
        static let cardSeconds: Double = 0.32
        static let pageSeconds: Double = 0.42
        static let revealSeconds: Double = 0.28
        static let staggerCardPick: Double = 0.045

        static var cardSpring: Animation {
            .spring(response: cardSeconds, dampingFraction: 0.88, blendDuration: 0.02)
        }

        static var pageSpring: Animation {
            .spring(response: pageSeconds, dampingFraction: 0.9, blendDuration: 0.02)
        }

        static var revealEase: Animation {
            .easeOut(duration: revealSeconds)
        }

        static var microEase: Animation {
            .easeOut(duration: microSeconds)
        }
    }

    static let screenGradient = LinearGradient(
        colors: [
            Color(red: 255 / 255, green: 249 / 255, blue: 245 / 255),
            Color(red: 255 / 255, green: 242 / 255, blue: 234 / 255),
            Color(red: 253 / 255, green: 232 / 255, blue: 223 / 255)
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )

    // Экран «Сегодня»: мягкие слои без лишней плотности карточек
    static let todayHeroSurface = Color.white.opacity(0.42)
    static let todaySoftCard = Color.white.opacity(0.46)
    static let todayPanelGradient = LinearGradient(
        colors: [Color.white.opacity(0.82), paper.opacity(0.74)],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    static let aurora = LinearGradient(
        colors: [
            Color.white.opacity(0.96),
            Color(red: 1, green: 0.95, blue: 0.91).opacity(0.92),
            Color(red: 0.98, green: 0.88, blue: 0.82).opacity(0.85)
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
}

// Важно: вызовы `navigationBarTitleDisplayMode` должны жить только в `#if os(iOS)` —
// иначе компилятор macOS иногда всё равно ругается, даже внутри `#else`.

#if os(iOS)
extension View {
    func todayflowNavigationBarTitleDisplayModeLarge() -> some View {
        self.navigationBarTitleDisplayMode(.large)
    }

    func todayflowNavigationBarTitleDisplayModeInline() -> some View {
        self.navigationBarTitleDisplayMode(.inline)
    }
}
#endif

#if !os(iOS)
extension View {
    func todayflowNavigationBarTitleDisplayModeLarge() -> some View { self }
    func todayflowNavigationBarTitleDisplayModeInline() -> some View { self }
}
#endif

struct TodayFlowScreenBackground: View {
    var body: some View {
        TodayFlowTheme.screenGradient
            .ignoresSafeArea()
    }
}

extension View {
    func todayFlowCard(cornerRadius: CGFloat = 20) -> some View {
        self
            .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(TodayFlowTheme.contour.opacity(0.55), lineWidth: 1)
            )
    }

    /// Единый контейнер контента для всех основных экранов iOS:
    /// одинаковая ширина, безопасные горизонтальные поля и вертикальный ритм.
    func todayFlowContentContainer(
        maxWidth: CGFloat = 1240,
        horizontal: CGFloat = 20,
        top: CGFloat = 10,
        bottom: CGFloat = 16
    ) -> some View {
        self
            .padding(.horizontal, horizontal)
            .padding(.top, top)
            .padding(.bottom, bottom)
            .frame(maxWidth: maxWidth)
            .frame(maxWidth: .infinity)
    }

    /// Главная премиальная поверхность для верхнеуровневых блоков.
    func todayFlowSurfacePrimary(cornerRadius: CGFloat = 24) -> some View {
        self
            .background(
                LinearGradient(
                    colors: [Color.white.opacity(0.92), TodayFlowTheme.paper.opacity(0.82)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
            }
            .shadow(color: TodayFlowTheme.gold.opacity(0.08), radius: 14, y: 5)
    }

    /// Вложенные карточки внутри секций.
    func todayFlowSurfaceSoft(cornerRadius: CGFloat = 18) -> some View {
        self
            .background(Color.white.opacity(0.68))
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.12), lineWidth: 1)
            }
    }

    func todayFlowSurfaceEthereal(cornerRadius: CGFloat = 24) -> some View {
        self
            .background(TodayFlowTheme.aurora)
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(Color.white.opacity(0.45), lineWidth: 1)
            }
            .shadow(color: TodayFlowTheme.gold.opacity(0.10), radius: 18, y: 8)
    }

    /// Стандартные внутренние поля для блоков внутри экрана.
    func todayFlowInset(
        _ amount: CGFloat = TodayFlowTheme.Layout.inset
    ) -> some View {
        self.padding(amount)
    }

    /// Узкий инсет (подпункты, вложенные зоны).
    func todayFlowInsetTight(
        _ amount: CGFloat = TodayFlowTheme.Layout.insetTight
    ) -> some View {
        self.padding(amount)
    }
}

extension Font {
    /// Подзаголовок-«бровь» (верхние метки секций)
    static var todayFlowEyebrow: Font { .caption.weight(.semibold) }
    /// Крупный заголовок героя экрана
    static var todayFlowHeroTitle: Font { .system(size: 28, weight: .bold, design: .serif) }
    /// Заголовок ритуала Today — паритет с веб `clamp(1.45rem–2rem)`, без «плаката»
    static var todayFlowRitualHeroTitle: Font { .system(size: 22, weight: .semibold, design: .serif) }
    /// Крупная метрика в центре героя (энергия / число)
    static var todayFlowHeroMetric: Font { .system(size: 32, weight: .bold, design: .rounded) }
    /// Заголовок смысловой секции
    static var todayFlowSectionTitle: Font { .title2.weight(.bold) }
}

#if os(iOS)
enum TodayFlowToolbar {
    static var trailing: ToolbarItemPlacement { .topBarTrailing }
}
#else
enum TodayFlowToolbar {
    static var trailing: ToolbarItemPlacement { .automatic }
}
#endif

/// Системная локаль для пользовательского chrome (паритет с `CompatibilityScreenChrome` / `AuthScreenChrome`).
enum IOSAppLocale {
    static var prefersRussian: Bool {
        if let code = Locale.current.language.languageCode?.identifier.lowercased() {
            if code == "ru" { return true }
            if code == "en" { return false }
        }
        return Bundle.main.preferredLocalizations.first?.lowercased().hasPrefix("ru") == true
    }
}
