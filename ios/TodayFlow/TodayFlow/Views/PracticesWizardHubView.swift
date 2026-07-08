import SwiftUI

private enum PracticesWizardStep: String {
    case goal
    case direction
    case practice
}

/// Product UI wizard — паритет веб `/practices` (goal → direction → catalog).
struct PracticesWizardHubView: View {
    @Binding var navigationPath: NavigationPath
    var isAuthenticated: Bool

    @State private var step: PracticesWizardStep = .goal
    @State private var selectedGoalId: PracticeCatalogGoalId?
    @State private var selectedDirection: PracticeCatalogDirectionKey?
    @State private var catalogTab: PracticeCatalogContent.CatalogTabId = .all
    @State private var allPractices: [PracticeSummaryDTO] = []
    @State private var loading = false
    @State private var errorMessage: String?

    private var ru: Bool { IOSAppLocale.prefersRussian }

    private var goals: [PracticeCatalogGoalOption] { PracticeCatalogContent.goals(ru: ru) }

    private var selectedGoal: PracticeCatalogGoalOption? {
        goals.first { $0.id == selectedGoalId }
    }

    private var filteredPractices: [PracticeSummaryDTO] {
        guard let direction = selectedDirection else { return [] }
        let directionMatched = allPractices.filter { PracticeCatalogContent.matchesDirection($0, direction: direction) }
        let pool = directionMatched.isEmpty ? Array(allPractices.prefix(8)) : directionMatched
        return pool
            .filter { PracticeCatalogContent.matchesCatalogTab($0, tab: catalogTab) }
            .sorted { lhs, rhs in
                if lhs.isPersonalized != rhs.isPersonalized { return lhs.isPersonalized && !rhs.isPersonalized }
                return (lhs.durationMinutes ?? 0) < (rhs.durationMinutes ?? 0)
            }
    }

    private var todayItems: [PracticeSummaryDTO] {
        Array(filteredPractices.prefix(4))
    }

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 20) {
                    headerBlock
                    wizardStepsRow

                    switch step {
                    case .goal:
                        goalStep
                    case .direction:
                        directionStep
                    case .practice:
                        practiceStep
                    }
                }
                .padding(.horizontal, 18)
                .padding(.top, 12)
                .padding(.bottom, 28)
            }
        }
        .navigationTitle(PracticesExperienceChrome.practicesCatalogPageTitle)
        .todayflowNavigationBarTitleDisplayModeLarge()
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    navigationPath.append(PracticesRoute.history)
                } label: {
                    Image(systemName: "clock.arrow.circlepath")
                }
                .accessibilityLabel(PracticesExperienceChrome.a11yHistory)
            }
        }
    }

    private var headerBlock: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(PracticesExperienceChrome.practicesCatalogPageSubtitle)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var wizardStepsRow: some View {
        HStack(spacing: 8) {
            wizardChip(
                label: "1. \(PracticesExperienceChrome.practicesCatalogWizardStepGoal)",
                active: step == .goal
            )
            wizardChip(
                label: "2. \(PracticesExperienceChrome.practicesCatalogWizardStepDirection)",
                active: step == .direction
            )
            wizardChip(
                label: "3. \(PracticesExperienceChrome.practicesCatalogWizardStepPractice)",
                active: step == .practice
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(PracticesExperienceChrome.practicesCatalogWizardStepsAria)
    }

    private func wizardChip(label: String, active: Bool) -> some View {
        Text(label)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(active ? TodayFlowTheme.accent.opacity(0.18) : Color.black.opacity(0.05), in: Capsule())
            .foregroundStyle(active ? TodayFlowTheme.accent : TodayFlowTheme.secondaryInk)
    }

    private var goalStep: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(PracticesExperienceChrome.practicesCatalogGoalPrompt)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            ForEach(goals) { goal in
                Button {
                    selectedGoalId = goal.id
                    step = .direction
                } label: {
                    HStack(alignment: .top, spacing: 12) {
                        Text(goal.icon)
                            .font(.title2)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(goal.title)
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(goal.description)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                .multilineTextAlignment(.leading)
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(16)
                    .todayFlowCard()
                }
                .buttonStyle(.plain)
            }
        }
    }

    @ViewBuilder
    private var directionStep: some View {
        if let goal = selectedGoal {
            VStack(alignment: .leading, spacing: 14) {
                Button {
                    step = .goal
                    selectedGoalId = nil
                    selectedDirection = nil
                } label: {
                    Text(PracticesExperienceChrome.practicesCatalogBack)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.accent)
                }
                .buttonStyle(.plain)

                Text(PracticesExperienceChrome.practicesCatalogChooseDirection)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)

                Text(goal.title)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                ForEach(goal.directions, id: \.self) { direction in
                    Button {
                        selectedDirection = direction
                        step = .practice
                        Task { await loadPractices() }
                    } label: {
                        Text(PracticeCatalogContent.directionLabel(direction, ru: ru))
                            .font(.body.weight(.medium))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(16)
                            .todayFlowCard()
                            .foregroundStyle(TodayFlowTheme.ink)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    @ViewBuilder
    private var practiceStep: some View {
        if let direction = selectedDirection {
            VStack(alignment: .leading, spacing: 16) {
                Button {
                    step = .direction
                } label: {
                    Text("\(PracticesExperienceChrome.practicesCatalogBack) · \(PracticeCatalogContent.directionLabel(direction, ru: ru))")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.accent)
                        .multilineTextAlignment(.leading)
                }
                .buttonStyle(.plain)

                if loading {
                    ProgressView(PracticesExperienceChrome.loadingPractices)
                        .tint(TodayFlowTheme.accent)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 24)
                } else if let errorMessage {
                    Text(errorMessage)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.roseClay)
                        .padding(16)
                        .todayFlowCard()
                } else {
                    todaySection
                    catalogTabs
                    programGrid
                }
            }
        }
    }

    private var todaySection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(PracticesExperienceChrome.practicesCatalogTodayLabel)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .textCase(.uppercase)
                Spacer()
                let done = min(2, todayItems.count)
                Text("\(done) \(PracticesExperienceChrome.practicesCatalogProgressOf) \(todayItems.count)")
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }

            ForEach(Array(todayItems.enumerated()), id: \.element.id) { index, practice in
                HStack(spacing: 10) {
                    Image(systemName: index < 2 ? "checkmark.circle.fill" : "circle")
                        .foregroundStyle(index < 2 ? TodayFlowTheme.accent : TodayFlowTheme.secondaryInk.opacity(0.4))
                    VStack(alignment: .leading, spacing: 2) {
                        Text(practice.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                        Text(PracticeCatalogContent.categoryLabel(for: practice, ru: ru))
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                    }
                    Spacer()
                    if let min = practice.durationMinutes {
                        Text("\(min) \(PracticesExperienceChrome.practicesCatalogMinutesShort)")
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                    }
                }
                .padding(.vertical, 6)
            }
        }
        .padding(16)
        .todayFlowCard()
    }

    private var catalogTabs: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(PracticeCatalogContent.CatalogTabId.allCases) { tab in
                    Button {
                        catalogTab = tab
                    } label: {
                        Text(tab.label(ru: ru))
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(
                                catalogTab == tab ? TodayFlowTheme.accent.opacity(0.22) : Color.black.opacity(0.06),
                                in: Capsule()
                            )
                            .foregroundStyle(catalogTab == tab ? TodayFlowTheme.accent : TodayFlowTheme.ink)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .accessibilityLabel(PracticesExperienceChrome.practicesCatalogCategoriesAria)
    }

    private var programGrid: some View {
        LazyVStack(spacing: 12) {
            ForEach(Array(filteredPractices.prefix(8))) { practice in
                Button {
                    navigationPath.append(PracticesRoute.practice(practice.id))
                } label: {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(practice.title)
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                            Spacer()
                            if let min = practice.durationMinutes {
                                Text("\(min) \(PracticesExperienceChrome.practicesCatalogMinutesShort)")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                            }
                        }
                        Text(practice.description)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                            .lineLimit(3)
                            .multilineTextAlignment(.leading)
                        if practice.isPersonalized {
                            Text(PracticesExperienceChrome.practicesCatalogPersonalizedBadge)
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.accent)
                        }
                    }
                    .padding(16)
                    .todayFlowCard()
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func loadPractices() async {
        await MainActor.run {
            loading = true
            errorMessage = nil
        }
        do {
            let list = try await PracticesClient.fetchPracticesList()
            await MainActor.run {
                allPractices = list
                loading = false
            }
        } catch {
            await MainActor.run {
                errorMessage = PracticesExperienceChrome.practicesCatalogLoadError
                loading = false
            }
        }
    }
}

#if DEBUG
#Preview("Practices wizard") {
    NavigationStack {
        PracticesWizardHubView(navigationPath: .constant(NavigationPath()), isAuthenticated: true)
    }
}
#endif
