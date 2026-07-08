/** Living Maps explore catalog — MP-1 · PROFILE_SCREEN_MASTER §7. */

export type ProfileMapExploreCard = {
  id: string;
  title: string;
  desc: string;
  href: string;
  primary?: boolean;
};

export const PROFILE_MAP_EXPLORE_CARDS: ProfileMapExploreCard[] = [
  {
    id: "hub",
    title: "Все карты",
    desc: "Хаб карт и ритма",
    href: "/tracking/progress",
    primary: true,
  },
  { id: "mood", title: "Настроение", desc: "Утренние отметки", href: "/maps/mood" },
  { id: "energy", title: "Энергия", desc: "Темп дня", href: "/maps/energy" },
  { id: "promise", title: "Обещания", desc: "Вечернее закрытие", href: "/maps/promise" },
  { id: "habits", title: "Привычки", desc: "Цветовая карта", href: "/habits" },
  { id: "ascetic", title: "Аскезы", desc: "Тропа пути", href: "/maps/ascetic" },
  { id: "wish", title: "Желания", desc: "Созвездие якорей", href: "/maps/wish" },
  { id: "relationship", title: "Связи", desc: "Круги внимания", href: "/maps/relationship" },
  { id: "tarot", title: "Таро", desc: "Архетипическая линия", href: "/maps/tarot" },
  { id: "rhythm", title: "Ритм", desc: "Месяц и Flow", href: "/tracking/calendar" },
];
