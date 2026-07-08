import Foundation

/// Паритет с `frontend/.../trackerEntityCatalog.ts` — `HABIT_TEMPLATE_GROUPS`.
enum HabitTemplateCatalog {
    struct Category: Identifiable {
        let id: String
        let label: String
        let description: String
    }

    struct Item: Identifiable {
        var id: String { title }
        let title: String
        let hint: String?
    }

    struct Group: Identifiable {
        var id: String { category.id }
        let category: Category
        let items: [Item]
    }

    static let groups: [Group] = [
        Group(
            category: Category(id: "morning", label: "Утро", description: "Старт дня"),
            items: [
                Item(title: "Стакан воды после подъёма", hint: "30 секунд"),
                Item(title: "2 минуты планирования дня", hint: "Три задачи"),
                Item(title: "Свет и окно — сразу после будильника", hint: "Регуляция циркад"),
                Item(title: "Короткая зарядка 7 минут", hint: "Любимый комплекс"),
                Item(title: "Аффирмация или намерение вслух", hint: "Одна фраза"),
            ]
        ),
        Group(
            category: Category(id: "body_habit", label: "Тело", description: "Движение и сон"),
            items: [
                Item(title: "Прогулка 20+ минут", hint: "Без подкаста — только шаги"),
                Item(title: "Лечь в одно время ±30 мин", hint: "Якорь сна"),
                Item(title: "Один приём пищи без экрана", hint: "Осознанность"),
                Item(title: "Растяжка перед сном", hint: "5–10 минут"),
                Item(title: "Лестница вместо лифта (где безопасно)", hint: "Микродвижение"),
            ]
        ),
        Group(
            category: Category(id: "mind", label: "Фокус и цифра", description: "Внимание и экран"),
            items: [
                Item(title: "Первый час дня без соцсетей", hint: "Режим «не беспокоить»"),
                Item(title: "Один Pomodoro без переключений", hint: "25 минут"),
                Item(title: "Инбокс нуля — раз в день 15 минут", hint: "Не весь день в почте"),
                Item(title: "Телефон вне спальни на ночь", hint: "Зарядка в коридоре"),
                Item(title: "Очистить рабочий стол / одну папку", hint: "Микро-порядок"),
            ]
        ),
        Group(
            category: Category(id: "care", label: "Забота", description: "Ресурс и эмоции"),
            items: [
                Item(title: "Дневник: 3 строки вечером", hint: "Факт — чувство — завтра"),
                Item(title: "5 минут дыхания", hint: "Таймер"),
                Item(title: "Сказать «спасибо» кому-то конкретно", hint: "Текст или голос"),
                Item(title: "10 минут на хобби без цели", hint: "Радость"),
                Item(title: "Прогулка без цели", hint: "Только идти"),
            ]
        ),
        Group(
            category: Category(id: "home", label: "Быт", description: "Окружение"),
            items: [
                Item(title: "10 минут уборки таймером", hint: "Один угол"),
                Item(title: "Вынести мусор / разгрузить посудомойку", hint: "Микрозадача"),
                Item(title: "Подготовить одежду на завтра", hint: "Вечером"),
                Item(title: "Проветривание + влажная уборка стола", hint: "Среда = голова"),
            ]
        ),
        Group(
            category: Category(id: "social", label: "Связь", description: "Люди"),
            items: [
                Item(title: "Одно сообщение близкому", hint: "Не деловое"),
                Item(title: "Позвонить родителю / другу 10 минут", hint: "Голос"),
                Item(title: "Поблагодарить коллегу за конкретику", hint: "Письмо или устно"),
            ]
        ),
    ]
}
