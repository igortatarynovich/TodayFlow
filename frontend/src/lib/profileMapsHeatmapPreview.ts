import { buildEnergyDayStory, buildEnergyMapCells, buildEnergyMapRecordsWithMoodFallback } from "@/lib/energyMapModel";
import {
  buildMoodDayStory,
  buildMoodMapCells,
  type MoodMapLocale,
} from "@/lib/moodMapModel";
import {
  buildPromiseDayStory,
  buildPromiseMapCells,
  scanPromiseMapDayRecords,
} from "@/lib/promiseMapModel";
import { scanMoodMapDayRecords } from "@/lib/todayDayEngagement";

export const PROFILE_MAPS_HEATMAP_WINDOW_DAYS = 35;

export type ProfileMapHeatmapId = "mood" | "energy" | "promise";

export type ProfileMapHeatmapCell = {
  dateISO: string;
  color: string;
  hasMark: boolean;
  isFuture: boolean;
  title: string;
};

export type ProfileMapHeatmapRow = {
  id: ProfileMapHeatmapId;
  title: string;
  href: string;
  cells: ProfileMapHeatmapCell[];
  filledCount: number;
};

export type ProfileMapsHeatmapPreviewModel = {
  rows: ProfileMapHeatmapRow[];
  hasAnyMarks: boolean;
};

export function buildProfileMapDayStory(
  mapId: ProfileMapHeatmapId,
  dateISO: string,
  locale: MoodMapLocale = "ru",
): string | null {
  if (mapId === "mood") {
    const record = scanMoodMapDayRecords().find((row) => row.dateISO === dateISO);
    return record ? buildMoodDayStory(record, locale) : null;
  }
  if (mapId === "energy") {
    const record = buildEnergyMapRecordsWithMoodFallback().find((row) => row.dateISO === dateISO) ?? null;
    return record ? buildEnergyDayStory(record, locale) : null;
  }
  const record = scanPromiseMapDayRecords().find((row) => row.dateISO === dateISO);
  return record ? buildPromiseDayStory(record, locale) : null;
}

export function buildProfileMapsHeatmapPreview(
  todayISO: string,
  windowDays = PROFILE_MAPS_HEATMAP_WINDOW_DAYS,
): ProfileMapsHeatmapPreviewModel {
  const moodCells = buildMoodMapCells(todayISO, windowDays).map((cell) => ({
    dateISO: cell.dateISO,
    color: cell.color,
    hasMark: Boolean(cell.record),
    isFuture: cell.isFuture,
    title: cell.record ? `${cell.dateISO} — ${cell.record.moodLabel}` : cell.dateISO,
  }));

  const energyCells = buildEnergyMapCells(todayISO, windowDays).map((cell) => ({
    dateISO: cell.dateISO,
    color: cell.color,
    hasMark: Boolean(cell.record),
    isFuture: cell.isFuture,
    title: cell.record
      ? `${cell.dateISO} — ${cell.record.tempoLabel ?? "энергия"}`
      : cell.dateISO,
  }));

  const promiseCells = buildPromiseMapCells(todayISO, windowDays).map((cell) => ({
    dateISO: cell.dateISO,
    color: cell.color,
    hasMark: Boolean(cell.record),
    isFuture: cell.isFuture,
    title: cell.record
      ? `${cell.dateISO} — ${cell.outcomeLabel ?? "обещание"}`
      : cell.dateISO,
  }));

  const rows: ProfileMapHeatmapRow[] = [
    {
      id: "mood",
      title: "Настроение",
      href: "/maps/mood",
      cells: moodCells,
      filledCount: moodCells.filter((cell) => cell.hasMark).length,
    },
    {
      id: "energy",
      title: "Энергия",
      href: "/maps/energy",
      cells: energyCells,
      filledCount: energyCells.filter((cell) => cell.hasMark).length,
    },
    {
      id: "promise",
      title: "Обещания дня",
      href: "/maps/promise",
      cells: promiseCells,
      filledCount: promiseCells.filter((cell) => cell.hasMark).length,
    },
  ];

  return {
    rows,
    hasAnyMarks: rows.some((row) => row.filledCount > 0),
  };
}
