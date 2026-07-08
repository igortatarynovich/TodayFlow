import SwiftUI
import UIKit

private enum RitualPickHaptics {
    static func light() {
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }

    static func medium() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
    }
}

// MARK: - Вход (макет шаг 1)

struct RitualDesertEntryCard: View {
    let formattedDate: String
    let dateISO: String
    let energyScore: Int
    let onStart: () -> Void

    @State private var headerImage: UIImage?

    var body: some View {
        VStack(alignment: .center, spacing: 0) {
            ZStack(alignment: .bottom) {
                Color(red: 0.992, green: 0.973, blue: 0.949)
                    .aspectRatio(2, contentMode: .fit)
                Group {
                    if let headerImage {
                        Image(uiImage: headerImage)
                            .resizable()
                            .scaledToFill()
                    } else {
                        RitualDesertEntryVectorHero(energyScore: energyScore)
                    }
                }
                .aspectRatio(2, contentMode: .fit)
                .frame(maxWidth: .infinity)
                .clipped()
                LinearGradient(
                    colors: [
                        Color.black.opacity(0),
                        Color(red: 0.99, green: 0.96, blue: 0.93).opacity(0.5),
                        Color(red: 0.99, green: 0.95, blue: 0.91),
                    ],
                    startPoint: .center,
                    endPoint: .bottom
                )
                .aspectRatio(2, contentMode: .fit)
                .allowsHitTesting(false)
                VStack(alignment: .center, spacing: 12) {
                    Text(TodayRitualCopy.ritualEntryEyebrow(displayDate: formattedDate))
                        .font(.todayFlowEyebrow)
                        .foregroundStyle(TodayFlowTheme.sand)
                        .multilineTextAlignment(.center)
                    Text(TodayRitualCopy.ritualEntryTitle)
                        .font(.todayFlowRitualHeroTitle)
                        .foregroundStyle(TodayFlowTheme.ink)
                        .multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                    HStack(spacing: 10) {
                        Rectangle()
                            .fill(TodayFlowTheme.gold.opacity(0.32))
                            .frame(height: 1)
                        Image(systemName: "sparkle")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sunset.opacity(0.55))
                        Rectangle()
                            .fill(TodayFlowTheme.gold.opacity(0.32))
                            .frame(height: 1)
                    }
                    .padding(.horizontal, 8)
                    Text(TodayRitualCopy.ritualEntryBody)
                        .font(.body)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .lineSpacing(4)
                        .multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .frame(maxWidth: .infinity)
                .padding(.horizontal, 22)
                .padding(.top, 10)
                .padding(.bottom, 20)
            }
            .frame(maxWidth: .infinity)

            Button(action: onStart) {
                Text(TodayRitualCopy.ritualEntryCta)
                    .font(.headline)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(RitualRoseGoldProminentButtonStyle())
            .padding(.top, 16)

            Text(TodayRitualCopy.ritualEntryTiming)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.48))
                .frame(maxWidth: .infinity)
                .multilineTextAlignment(.center)
                .padding(.top, 8)
        }
        .onAppear {
            headerImage = TodayRitualEntryIllustration.loadUIImage(dateISO: dateISO, energyScore: energyScore)
        }
        .onChange(of: dateISO) { _, newISO in
            headerImage = TodayRitualEntryIllustration.loadUIImage(dateISO: newISO, energyScore: energyScore)
        }
        .onChange(of: energyScore) { _, newScore in
            headerImage = TodayRitualEntryIllustration.loadUIImage(dateISO: dateISO, energyScore: newScore)
        }
    }
}

// MARK: - Таро: рубашка → сетка 2×3 → раскрытие (макет 2–4)

private enum RitualTarotMiniPhase {
    case idle, grid, reveal
}

struct RitualTarotPickMiniFlow: View {
    let anchorCardId: Int
    /// После фиксации main на родителе — тот же экземпляр переходит к раскрытию (паритет с веб `resumeCommittedId`).
    let committedMainId: Int?
    let cardTitleRu: String
    let tagLabels: [String]
    let onCommitMain: () -> Void
    let onContinue: () -> Void

    @State private var phase: RitualTarotMiniPhase
    @State private var gridOpen = false
    @State private var pickedSlot: Int?
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    init(
        anchorCardId: Int,
        committedMainId: Int?,
        cardTitleRu: String,
        tagLabels: [String],
        onCommitMain: @escaping () -> Void,
        onContinue: @escaping () -> Void
    ) {
        self.anchorCardId = anchorCardId
        self.committedMainId = committedMainId
        self.cardTitleRu = cardTitleRu
        self.tagLabels = tagLabels
        self.onCommitMain = onCommitMain
        self.onContinue = onContinue
        _phase = State(initialValue: committedMainId != nil ? .reveal : .idle)
    }

    private var backURL: URL { TodayTarotDeckImageURLs.cardBackURL() }
    private var faceCardId: Int { committedMainId ?? anchorCardId }
    private var faceURL: URL? { TodayTarotDeckImageURLs.deckFaceURL(cardId: faceCardId) }

    var body: some View {
        Group {
            switch phase {
            case .idle:
                idleView
            case .grid:
                gridView
            case .reveal:
                revealView
            }
        }
        .frame(maxWidth: .infinity)
        .onChange(of: committedMainId) { _, new in
            guard new != nil, phase != .reveal else { return }
            if reduceMotion {
                phase = .reveal
            } else {
                withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                    phase = .reveal
                }
            }
        }
    }

    private var idleView: some View {
        VStack(spacing: 14) {
            Button {
                RitualPickHaptics.light()
                // Сразу делаем клетки интерактивными: иначе gridOpacity=0 и вложенный ScrollView
                // родителя часто «съедают» тапы по сетке (симулятор).
                gridOpen = true
                if reduceMotion {
                    phase = .grid
                } else {
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.82)) {
                        phase = .grid
                    }
                }
            } label: {
                ZStack {
                    Ellipse()
                        .fill(
                            RadialGradient(
                                colors: [
                                    Color(red: 1, green: 0.86, blue: 0.65).opacity(0.62),
                                    Color(red: 1, green: 0.93, blue: 0.82).opacity(0.25),
                                    Color.clear,
                                ],
                                center: .center,
                                startRadius: 2,
                                endRadius: 95
                            )
                        )
                        .frame(width: 200, height: 160)
                        .blur(radius: 14)
                        .offset(y: 8)
                        .allowsHitTesting(false)
                    ZStack {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(Color(red: 0.98, green: 0.96, blue: 0.93))
                            .shadow(color: Color.orange.opacity(0.2), radius: 18, y: 8)
                        AsyncImage(url: backURL) { phase in
                            switch phase {
                            case .success(let img):
                                img.resizable().scaledToFit()
                            default:
                                Color.clear
                            }
                        }
                        .padding(6)
                    }
                    .frame(width: min(168, max(124, ((UIApplication.shared.connectedScenes.first as? UIWindowScene)?.screen.bounds.width ?? 390) * 0.44)))
                    .aspectRatio(TodayTarotDeckImageURLs.cardPixelWidth / TodayTarotDeckImageURLs.cardPixelHeight, contentMode: .fit)
                    .overlay {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(TodayFlowTheme.gold.opacity(0.38), lineWidth: 1)
                    }
                    .shadow(color: Color(red: 1, green: 0.8, blue: 0.58).opacity(0.45), radius: 20, y: 4)
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            HStack(spacing: 5) {
                Image(systemName: "sparkle")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sunset.opacity(0.75))
                Text(TodayRitualCopy.tarotIdleHint)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            Button {
                RitualPickHaptics.light()
                onCommitMain()
                if reduceMotion {
                    phase = .reveal
                } else {
                    withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                        phase = .reveal
                    }
                }
            } label: {
                Text(TodayRitualCopy.tarotSkipAnimationCta)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sunset)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.plain)
        }
    }

    private let gridColumns = [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)]

    private var gridView: some View {
        VStack(spacing: 12) {
            Text(TodayRitualCopy.tarotGridLead)
                .font(.title2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .frame(maxWidth: .infinity)
            Text(TodayRitualCopy.tarotGridSub)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .frame(maxWidth: .infinity)
            LazyVGrid(columns: gridColumns, spacing: 12) {
                ForEach(0 ..< 6, id: \.self) { i in
                    Button {
                        guard pickedSlot == nil else { return }
                        pickedSlot = i
                        RitualPickHaptics.medium()
                        let delay: Double = reduceMotion ? 0.05 : 0.28
                        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                            withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                                phase = .reveal
                            }
                            onCommitMain()
                        }
                    } label: {
                        ZStack {
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(Color(red: 0.98, green: 0.96, blue: 0.93))
                            AsyncImage(url: backURL) { ph in
                                switch ph {
                                case .success(let img):
                                    img.resizable().scaledToFit()
                                default:
                                    Color.clear
                                }
                            }
                            .padding(4)
                        }
                        .aspectRatio(TodayTarotDeckImageURLs.cardPixelWidth / TodayTarotDeckImageURLs.cardPixelHeight, contentMode: .fit)
                        .opacity(gridOpacity(for: i))
                        .scaleEffect(gridScale(for: i))
                        .overlay {
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .stroke(TodayFlowTheme.gold.opacity(pickedSlot == i ? 0.55 : 0.22), lineWidth: pickedSlot == i ? 2 : 1)
                        }
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                }
            }
            .onAppear {
                if reduceMotion {
                    gridOpen = true
                } else {
                    withAnimation(.easeOut(duration: 0.38)) {
                        gridOpen = true
                    }
                }
            }
            VStack(alignment: .leading, spacing: 10) {
                HStack(alignment: .top, spacing: 8) {
                    Text("ⓘ")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sunset.opacity(0.85))
                    VStack(alignment: .leading, spacing: 4) {
                        Text(TodayRitualCopy.tarotGridPickHintPrimary)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                        Text(TodayRitualCopy.tarotGridPickHintSecondary)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                    }
                    .fixedSize(horizontal: false, vertical: true)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.78))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                }
                Text(TodayRitualCopy.tarotGridPickFooter)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.48))
                    .frame(maxWidth: .infinity)
                    .multilineTextAlignment(.center)
                    .padding(.top, 2)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func gridOpacity(for index: Int) -> Double {
        guard gridOpen else { return 0 }
        if let p = pickedSlot, p != index { return 0.35 }
        return 1
    }

    private func gridScale(for index: Int) -> CGFloat {
        guard gridOpen else { return 0.92 }
        return 1
    }

    private var revealView: some View {
        VStack(spacing: 12) {
            Text(TodayRitualCopy.tarotRevealScreenTitle)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            if let faceURL {
                let screenW = (UIApplication.shared.connectedScenes.first as? UIWindowScene)?.screen.bounds.width ?? 390
                AsyncImage(url: faceURL) { phase in
                    switch phase {
                    case .success(let img):
                        img
                            .resizable()
                            .scaledToFit()
                            .frame(maxWidth: min(TodayTarotDeckImageURLs.ritualRevealMaxWidth, screenW * 0.58))
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .overlay {
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .stroke(TodayFlowTheme.gold.opacity(0.35), lineWidth: 1)
                            }
                    default:
                        Color.clear.frame(height: 120)
                    }
                }
            }
            Text(cardTitleRu)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            if !tagLabels.isEmpty {
                FlowTagRow(tags: tagLabels)
            }
            Button {
                RitualPickHaptics.medium()
                onContinue()
            } label: {
                Text(TodayRitualCopy.tarotRevealContinueCta)
                    .font(.headline)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(RitualRoseGoldProminentButtonStyle())
            .padding(.top, 6)
        }
    }
}

private struct FlowTagRow: View {
    let tags: [String]
    var body: some View {
        VStack {
            FlexibleTagWrap(tags: tags)
        }
    }
}

/// Простая переносимая строка тегов.
private struct FlexibleTagWrap: View {
    let tags: [String]
    var body: some View {
        VStack(alignment: .center, spacing: 6) {
            HStack(spacing: 6) {
                ForEach(tags, id: \.self) { t in
                    Text(t)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color(red: 1, green: 0.93, blue: 0.89).opacity(0.85))
                        .clipShape(Capsule())
                        .overlay {
                            Capsule().stroke(TodayFlowTheme.sunset.opacity(0.28), lineWidth: 1)
                        }
                }
            }
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Число: цветок жизни + выбор (макет 5)

struct RitualNumberFlowerPick: View {
    let systemDigit: String
    let onReveal: () -> Void

    @State private var digitChosen = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(spacing: 14) {
            if !digitChosen {
                GeometryReader { geo in
                    let cx = geo.size.width / 2
                    let cy = geo.size.height / 2
                    ZStack {
                        FlowerOfLifeBackdrop()
                            .frame(width: min(geo.size.width, 240), height: min(geo.size.height, 240))
                            .position(x: cx, y: cy)
                            .opacity(0.35)
                        ForEach(1 ... 6, id: \.self) { n in
                            numberButton(n, center: CGPoint(x: cx, y: cy))
                        }
                    }
                }
                .frame(height: 260)
            }
            if digitChosen {
                ZStack {
                    Circle()
                        .fill(TodayFlowTheme.sunset.opacity(0.2))
                        .frame(width: 120, height: 120)
                        .blur(radius: 12)
                    Text(systemDigit)
                        .font(.system(size: 52, weight: .bold, design: .rounded))
                        .foregroundStyle(TodayFlowTheme.ink)
                }
                .padding(.top, 4)
                .transition(.scale.combined(with: .opacity))
                Button {
                    RitualPickHaptics.medium()
                    onReveal()
                } label: {
                    Text(TodayRitualCopy.numberRevealDoneCta)
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(RitualRoseGoldProminentButtonStyle())
                .padding(.top, 8)
            }
            if !digitChosen {
                VStack(alignment: .leading, spacing: 10) {
                    HStack(alignment: .top, spacing: 8) {
                        Text("ⓘ")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(TodayFlowTheme.sunset.opacity(0.85))
                        Text(TodayRitualCopy.numberDayEnergyInfo)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.78))
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    .overlay {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                    }
                    Text(TodayRitualCopy.numberCircleHint)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.5))
                        .frame(maxWidth: .infinity)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .animation(reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.82), value: digitChosen)
    }

    private func numberButton(_ n: Int, center: CGPoint) -> some View {
        let angle = Double(n - 1) * (.pi * 2 / 6) - .pi / 2
        let r: CGFloat = min(88, center.x * 0.72)
        let x = center.x + CGFloat(cos(angle)) * r
        let y = center.y + CGFloat(sin(angle)) * r
        return Button {
            guard !digitChosen else { return }
            RitualPickHaptics.light()
            digitChosen = true
        } label: {
            Text("\(n)")
                .font(.headline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .frame(width: 44, height: 44)
                .background(Color.white.opacity(0.75))
                .clipShape(Circle())
                .overlay {
                    Circle().stroke(TodayFlowTheme.gold.opacity(0.4), lineWidth: 1)
                }
        }
        .buttonStyle(.plain)
        .position(x: x, y: y)
    }
}

private struct FlowerOfLifeBackdrop: View {
    var body: some View {
        Canvas { ctx, size in
            let w = size.width
            let h = size.height
            let r = min(w, h) * 0.18
            let centers: [(CGFloat, CGFloat)] = [
                (w / 2, h / 2),
                (w / 2 - r * 0.87, h / 2 - r * 0.5),
                (w / 2 + r * 0.87, h / 2 - r * 0.5),
                (w / 2 - r * 0.87, h / 2 + r * 0.5),
                (w / 2 + r * 0.87, h / 2 + r * 0.5),
                (w / 2, h / 2 - r),
                (w / 2, h / 2 + r),
            ]
            for (cx, cy) in centers {
                var p = Path()
                p.addEllipse(in: CGRect(x: cx - r, y: cy - r, width: r * 2, height: r * 2))
                ctx.stroke(p, with: .color(TodayFlowTheme.gold.opacity(0.25)), lineWidth: 1)
            }
        }
    }
}

// MARK: - Кнопка градиента (макет)

struct RitualRoseGoldProminentButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(Color.white)
            .shadow(color: Color.black.opacity(0.12), radius: 0, x: 0, y: 1)
            .padding(.vertical, 14)
            .padding(.horizontal, 16)
            .background(
                LinearGradient(
                    colors: [
                        Color(red: 0.85, green: 0.66, blue: 0.55),
                        Color(red: 0.92, green: 0.75, blue: 0.68),
                        Color(red: 0.93, green: 0.78, blue: 0.72),
                    ],
                    startPoint: .leading,
                    endPoint: .trailing
                )
                .opacity(configuration.isPressed ? 0.88 : 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(Color(red: 0.78, green: 0.52, blue: 0.42).opacity(0.35), lineWidth: 1)
            }
    }
}
