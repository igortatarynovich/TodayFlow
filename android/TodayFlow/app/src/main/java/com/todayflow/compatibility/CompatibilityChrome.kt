package com.todayflow.compatibility

import java.util.Locale

object CompatibilityChrome {
    fun useRussian(): Boolean = Locale.getDefault().language.lowercase(Locale.US) == "ru"

    val navTitle: String get() = if (useRussian()) "Совместимость" else "Compatibility"
    val exploreTitle: String get() = if (useRussian()) "Что можно исследовать" else "What you can explore"
    val popularTitle: String get() = if (useRussian()) "Самые популярные разборы" else "Popular readings"
    val seriesTitle: String get() = if (useRussian()) "Серии" else "Series"
    val loading: String get() = if (useRussian()) "Загружаю encyclopedia…" else "Loading encyclopedia…"
    val loadError: String get() = if (useRussian()) "Не удалось загрузить каталог." else "Could not load catalog."
    val retry: String get() = if (useRussian()) "Повторить" else "Retry"
    val analyzeInvestigation: String get() = if (useRussian()) "Исследование" else "Exploration"
    val analyzeTitle: String get() = if (useRussian()) "Разобрать совместимость" else "Analyze compatibility"
    val quickEntry: String get() = if (useRussian()) "Быстрый вход" else "Quick entry"
    val preciseEntry: String get() = if (useRussian()) "Точный разбор" else "Precise reading"
    val yourSign: String get() = if (useRussian()) "Твой знак" else "Your sign"
    val partnerSign: String get() = if (useRussian()) "Знак партнёра" else "Partner sign"
    val betweenYou: String get() = if (useRussian()) "Между вами сейчас" else "Between you now"
    val contextUnspecified: String get() = if (useRussian()) "Не указывать" else "Not specified"
    val yourBirthdate: String get() = if (useRussian()) "Твоя дата рождения" else "Your birth date"
    val partnerBirthdate: String get() = if (useRussian()) "Дата партнёра" else "Partner birth date"
    val nameYou: String get() = if (useRussian()) "Твоё имя (необязательно)" else "Your name (optional)"
    val namePartner: String get() = if (useRussian()) "Имя партнёра (необязательно)" else "Partner name (optional)"
    val runReading: String get() = if (useRussian()) "Получить разбор" else "Get reading"
    val calculating: String get() = if (useRussian()) "Считаю…" else "Calculating…"
    val dynamicsError: String get() = if (useRussian()) "Не удалось загрузить разбор." else "Could not load the reading."
    val back: String get() = if (useRussian()) "Назад" else "Back"
    val betweenYouResult: String get() = if (useRussian()) "Между вами" else "Between you"
    val layers: String get() = if (useRussian()) "Слои динамики" else "Dynamic layers"
}
