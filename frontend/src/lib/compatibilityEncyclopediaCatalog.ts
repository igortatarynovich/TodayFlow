export type CompatibilityExploreCategory = {
  id: string;
  emoji: string;
  title: string;
  subtitle: string;
  href: string;
};

export type CompatibilityPopularReading = {
  id: string;
  title: string;
  href: string;
};

export type CompatibilitySeries = {
  id: string;
  title: string;
  subtitle: string;
  href: string;
};

export const COMPATIBILITY_EXPLORE_CATEGORIES: CompatibilityExploreCategory[] = [
  { id: "love", emoji: "❤️", title: "Любовь", subtitle: "Притяжение, близость, романтика", href: "/compatibility/analyze?topic=love" },
  { id: "living", emoji: "🏡", title: "Совместная жизнь", subtitle: "Быт, дом, ритм двоих", href: "/compatibility/analyze?topic=living_together" },
  { id: "work", emoji: "💼", title: "Работа", subtitle: "Роли, темп, решения", href: "/compatibility/analyze?topic=work" },
  { id: "friendship", emoji: "🤝", title: "Дружба", subtitle: "Опора, доверие, лёгкость", href: "/compatibility/analyze?topic=friendship" },
  { id: "sex", emoji: "🔥", title: "Секс", subtitle: "Желание, телесность, интим", href: "/compatibility/analyze?topic=sex" },
  { id: "money", emoji: "💰", title: "Деньги", subtitle: "Ресурсы, приоритеты, риски", href: "/compatibility/analyze?topic=money" },
  { id: "parenting", emoji: "👶", title: "Родительство", subtitle: "Дети, границы, поддержка", href: "/compatibility/analyze?topic=parenting" },
  { id: "travel", emoji: "✈️", title: "Путешествия", subtitle: "Совместный ритм и свобода", href: "/compatibility/analyze?topic=travel" },
  { id: "conflicts", emoji: "⚡", title: "Конфликты", subtitle: "Ссоры, триггеры, примирение", href: "/compatibility/analyze?topic=conflicts" },
  { id: "communication", emoji: "🎭", title: "Общение", subtitle: "Слова, паузы, недосказанность", href: "/compatibility/analyze?topic=communication" },
  { id: "emotional", emoji: "🌙", title: "Эмоциональная связь", subtitle: "Безопасность, уязвимость", href: "/compatibility/analyze?topic=emotional" },
  { id: "growth", emoji: "📈", title: "Рост друг друга", subtitle: "Вдохновение и развитие", href: "/compatibility/analyze?topic=growth" },
];

export const COMPATIBILITY_POPULAR_READINGS: CompatibilityPopularReading[] = [
  { id: "opposites", title: "Почему противоположности притягиваются?", href: "/compatibility/analyze?reading=opposites" },
  { id: "reconcile", title: "Кто чаще делает первый шаг после ссоры?", href: "/compatibility/analyze?reading=reconcile" },
  { id: "decisions", title: "Кто принимает решения?", href: "/compatibility/analyze?reading=decisions" },
  { id: "money_control", title: "Кто распоряжается деньгами?", href: "/compatibility/analyze?reading=money_control" },
  { id: "fatigue", title: "Кто быстрее устаёт друг от друга?", href: "/compatibility/analyze?reading=fatigue" },
  { id: "passion", title: "У кого выше страсть?", href: "/compatibility/analyze?reading=passion" },
  { id: "work_together", title: "Кто лучше работает вместе?", href: "/compatibility/analyze?reading=work_together" },
  { id: "inspire", title: "Кто кого вдохновляет?", href: "/compatibility/analyze?reading=inspire" },
  { id: "love_language", title: "Какой у пары язык любви?", href: "/compatibility/analyze?reading=love_language" },
  { id: "responsibility", title: "Кто берёт ответственность?", href: "/compatibility/analyze?reading=responsibility" },
];

export const COMPATIBILITY_SERIES: CompatibilitySeries[] = [
  { id: "living_together", title: "Living Together", subtitle: "Быт, границы, ритм дома", href: "/compatibility/analyze?series=living_together" },
  { id: "office", title: "Office Compatibility", subtitle: "Работа, роли, давление", href: "/compatibility/analyze?series=office" },
  { id: "partner_in_crime", title: "Partner in Crime", subtitle: "Авантюры, риск, азарт", href: "/compatibility/analyze?series=partner_in_crime" },
  { id: "vacation", title: "Vacation Together", subtitle: "Отдых, свобода, ожидания", href: "/compatibility/analyze?series=vacation" },
  { id: "business", title: "Business Partners", subtitle: "Деньги, решения, ответственность", href: "/compatibility/analyze?series=business" },
  { id: "conflict_style", title: "Conflict Style", subtitle: "Ссоры, паузы, примирение", href: "/compatibility/analyze?series=conflict_style" },
  { id: "parenting", title: "Parenting", subtitle: "Дети, опора, границы", href: "/compatibility/analyze?series=parenting" },
  { id: "money_together", title: "Money Together", subtitle: "Бюджет, приоритеты, страхи", href: "/compatibility/analyze?series=money_together" },
  { id: "love_languages", title: "Love Languages", subtitle: "Как вы чувствуете близость", href: "/compatibility/analyze?series=love_languages" },
  { id: "emotional", title: "Emotional Compatibility", subtitle: "Чувства, безопасность, дистанция", href: "/compatibility/analyze?series=emotional" },
  { id: "apocalypse", title: "Apocalypse", subtitle: "Кризис, стресс, выживание вместе", href: "/compatibility/analyze?series=apocalypse" },
];
