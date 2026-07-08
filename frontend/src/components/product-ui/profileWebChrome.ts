import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";

export type ProfileWebChrome = {
  pageTitle: string;
  pageSubtitle: string;
  todayPrefix: string;
  profileAria: string;
  railAnchorsTitle: string;
  railLinksTitle: string;
  railLinksHint: string;
  railCompatibilityLink: string;
  myDaysEyebrow: string;
  myDaysLink: string;
  myDaysHeatmapAria: string;
  archetypeAria: string;
};

export function profileWebChromeBundle(locale: FlowPracticesChromeLocale): ProfileWebChrome {
  const loc = locale === "ru" ? "ru" : "en";
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);

  return {
    pageTitle: tr("profile.web.pageTitle", "Моя карта", "My map"),
    pageSubtitle: tr(
      "profile.web.pageSubtitle",
      "Личный профиль — опора для Today и совместимости.",
      "Your personal profile — the anchor for Today and compatibility.",
    ),
    todayPrefix: tr("profile.web.todayPrefix", "Сегодня,", "Today,"),
    profileAria: tr("profile.web.profileAria", "Профиль", "Profile"),
    railAnchorsTitle: tr("profile.web.rail.anchors", "Якоря карты", "Map anchors"),
    railLinksTitle: tr("profile.web.rail.links", "Связи", "Connections"),
    railLinksHint: tr(
      "profile.web.rail.linksHint",
      "Посмотри динамику с близкими людьми через совместимость.",
      "Explore dynamics with people close to you through compatibility.",
    ),
    railCompatibilityLink: tr("profile.web.rail.compatLink", "Открыть совместимость", "Open compatibility"),
    myDaysEyebrow: tr("profile.web.myDays.eyebrow", "МОИ ДНИ", "MY DAYS"),
    myDaysLink: tr("profile.web.myDays.link", "Открыть полный анализ →", "Open full analysis →"),
    myDaysHeatmapAria: tr("profile.web.myDays.heatmapAria", "Активность последних дней", "Recent day activity"),
    archetypeAria: tr("profile.web.archetypeAria", "Архетип", "Archetype"),
  };
}
