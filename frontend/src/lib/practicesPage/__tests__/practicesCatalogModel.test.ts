import {
  categoryLabelFromOptions,
  programCardsFromCatalog,
  progressSummaryFromApi,
  quickItemsFromCatalog,
  type PracticeCatalogItem,
} from "@/lib/practicesPage/practicesCatalogModel";

describe("practicesCatalogModel helpers", () => {
  const practice: PracticeCatalogItem = {
    id: "breath-478",
    title: "Дыхание 4-7-8",
    description: "Успокаивающая техника",
    category: "breathing",
    difficulty: "beginner",
    is_free: true,
    is_personalized: false,
    access_level: "free",
    tags: [],
    duration_minutes: 5,
  };

  const sequence: PracticeCatalogItem = {
    ...practice,
    id: "sequence-emotional-awareness-week",
    title: "Неделя осознанности",
    practice_type: "guided_sequence",
    sequence_id: "emotional-awareness-week",
    total_steps: 7,
    duration_minutes: undefined,
  };

  it("maps catalog items to program cards", () => {
    const cards = programCardsFromCatalog([practice], { locale: "ru", minutesShort: "мин", max: 1 });
    expect(cards[0]?.title).toBe("Дыхание 4-7-8");
    expect(cards[0]?.durationLabel).toBe("5 мин");
  });

  it("maps sequences to program cards with step count", () => {
    const cards = programCardsFromCatalog([sequence], { locale: "ru", minutesShort: "мин", max: 1 });
    expect(cards[0]?.tagLabel).toBe("Серия");
    expect(cards[0]?.durationLabel).toBe("7 шага");
  });

  it("builds progress summary with by_category rows", () => {
    const summary = progressSummaryFromApi(
      {
        total_completed: 10,
        personalized_completed: 4,
        general_completed: 6,
        by_category: [{ category: "breathing", total_completed: 3, personalized_completed: 1 }],
        current_streak_days: 2,
        longest_streak_days: 5,
        weeks_active: 2,
      },
      [{ id: "breathing", name: "Дыхание" }],
      "ru",
    );

    expect(summary?.personalizedCompleted).toBe(4);
    expect(summary?.byCategory[0]?.label).toBe("Дыхание");
    expect(summary?.byCategory[0]?.sharePercent).toBe(30);
  });

  it("maps quick items and excludes program cards", () => {
    const items = quickItemsFromCatalog([practice, sequence], {
      locale: "ru",
      minutesShort: "мин",
      max: 2,
      excludeIds: new Set([practice.id]),
    });
    expect(items).toHaveLength(1);
    expect(items[0]?.id).toBe(sequence.id);
  });

  it("resolves category labels from API options", () => {
    expect(categoryLabelFromOptions("breathing", [{ id: "breathing", name: "Дыхание" }], "ru")).toBe(
      "Дыхание",
    );
  });
});
