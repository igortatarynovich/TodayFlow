#!/usr/bin/env python3
"""Build DATA/reference/tarot/knowledge_v1/cards.json (Tarot Knowledge Base v1).

Authoring surface for semantic facts. Runtime SoT is the committed JSON.
Canon: docs/tarot/TAROT_KNOWLEDGE_BASE_V1.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.tarot_minors_q1_archetypes import MINORS_Q1  # noqa: E402

OUT = ROOT / "DATA" / "reference" / "tarot" / "knowledge_v1" / "cards.json"
DECK = ROOT / "DATA" / "astrology_reference" / "tarot_full_deck.json"

# Question-type tags used in amplifies_questions (align with engine domains + backlog ontology).
Q = (
    "choice",
    "relationships",
    "work",
    "money",
    "purpose",
    "inner_state",
    "decision",
    "conflict",
    "growth",
    "undefined",
)

SUIT_ORDER = ("wands", "cups", "swords", "pentacles")
RANK_ORDER = (
    "ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "page",
    "knight",
    "queen",
    "king",
)

OPPOSITE_SUIT = {
    "wands": "cups",
    "cups": "wands",
    "swords": "pentacles",
    "pentacles": "swords",
}


def _card(
    card_id: int,
    name_ru: str,
    *,
    central: str,
    light: list[str],
    shadow: list[str],
    inner: str,
    outer: str,
    relationships: str,
    work: str,
    money: str,
    growth: str,
    rev_central: str,
    rev_themes: list[str],
    rev_trap: str,
    amplifies: list[str],
    intensifies: list[int],
    softens: list[int],
    upright_themes: list[str] | None = None,
    reversed_themes: list[str] | None = None,
    q1: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "card_id": card_id,
        "name_ru": name_ru,
        "central_archetype": central,
        "light": light,
        "shadow": shadow,
        "inner_conflict": inner,
        "outer_expression": outer,
        "domains": {
            "relationships": relationships,
            "work": work,
            "money": money,
            "growth": growth,
        },
        "reversed": {
            "central": rev_central,
            "themes": rev_themes,
            "trap": rev_trap,
        },
        "amplifies_questions": amplifies,
        "intensifies_with": intensifies,
        "softens_with": softens,
        "upright_themes": upright_themes or light[:4],
        "reversed_themes": reversed_themes or rev_themes,
    }
    if q1:
        for key in (
            "core_scene",
            "central_conflict",
            "driving_need",
            "shadow_pattern",
            "growth_direction",
            "work_lens",
            "relationship_lens",
            "money_lens",
            "inner_lens",
            "reversed_shift",
            "adjacent_distinction",
        ):
            val = q1.get(key)
            if val:
                out[key] = val
    return out


MAJORS: dict[int, dict[str, Any]] = {
    0: _card(
        0,
        "Шут",
        central="новый шаг в неизвестное без полной карты",
        light=["открытость опыту", "эксперимент", "свобода от старого сценария", "лёгкость старта"],
        shadow=["импульсивность", "прыжок ради снятия тревоги", "отказ готовиться"],
        inner="хочет свободы и боится выглядеть неготовым",
        outer="начинает раньше, чем объяснит себе зачем",
        relationships="свежий контакт или готовность рискнуть близостью без гарантий",
        work="пилот / новый роль / смена поля без полного плана",
        money="ставка на потенциал, а не на уже посчитанный доход",
        growth="разрешить себе первый несовершенный шаг",
        rev_central="прыжок без опоры или застревание в «ещё не готов»",
        rev_themes=["импульс без подготовки", "откладывание старта", "наивное повторение цикла"],
        rev_trap="либо бросается, либо вечно готовится — оба пути избегают контакта с реальностью",
        amplifies=["growth", "decision", "purpose", "choice"],
        intensifies=[1, 10, 16],
        softens=[4, 9, 14],
    ),
    1: _card(
        1,
        "Маг",
        central="сбор ресурсов в одно направленное действие",
        light=["фокус", "воля", "инструменты в руках", "связь слова и дела"],
        shadow=["рассеянность", "манипуляция", "сомнение в своём влиянии"],
        inner="знает, что может, но сомневается, стоит ли брать ответственность",
        outer="собирает средства, людей, навыки в одну линию",
        relationships="инициирует разговор или рамку контакта",
        work="запуск, презентация, сбор команды/инструментов",
        money="активное использование уже имеющихся рычагов",
        growth="перевести намерение в конкретный жест",
        rev_central="сила есть, но вектор размазан или используется криво",
        rev_themes=["рассеянная энергия", "манипуляция", "недоверие к своим инструментам"],
        rev_trap="много говорит о возможностях, мало фиксирует один ход",
        amplifies=["work", "decision", "purpose", "growth"],
        intensifies=[0, 7, 19],
        softens=[2, 9, 14],
    ),
    2: _card(
        2,
        "Верховная Жрица",
        central="знание под поверхностью; пауза перед проявленным ответом",
        light=["интуиция", "тишина", "внутреннее знание", "хранение границы"],
        shadow=["закрытость", "молчание вместо ясности", "недоверие к сигналу"],
        inner="чувствует правду раньше, чем может её объяснить",
        outer="держит паузу, читает скрытые сигналы, не спешит открываться",
        relationships="нужна честность без давления; важно то, что не сказано",
        work="стратегия «ещё не раскрывать»; наблюдение за полем",
        money="не вкладываться в то, что не резонирует телом",
        growth="доверять тихому знанию без требования доказательств",
        rev_central="сигнал глушится или прячется от себя",
        rev_themes=["игнор интуиции", "закрытость", "секрет как контроль"],
        rev_trap="молчит так долго, что ситуация решает за него",
        amplifies=["inner_state", "relationships", "decision", "undefined"],
        intensifies=[18, 9, 17],
        softens=[1, 19, 4],
    ),
    3: _card(
        3,
        "Императрица",
        central="опора, рост и телесная щедрость формы",
        light=["забота", "плодородие", "телесность", "создание условий"],
        shadow=["истощение от отдачи", "перегруз заботой", "зависимость от «быть нужной»"],
        inner="хочет питать жизнь и боится опустошиться",
        outer="создаёт среду, где что-то может вырасти",
        relationships="тепло, поддержка, телесный/бытовой контакт",
        work="выращивание продукта, команды, условий",
        money="изобилие через заботу о базе, не через гонку",
        growth="разрешить себе получать, а не только отдавать",
        rev_central="отдача без восполнения или творческий застой",
        rev_themes=["истощение", "отдавать больше, чем получать", "застой творчества"],
        rev_trap="держит всех на плаву ценой собственной опоры",
        amplifies=["relationships", "growth", "money", "inner_state"],
        intensifies=[19, 17, 21],
        softens=[4, 15, 13],
    ),
    4: _card(
        4,
        "Император",
        central="структура, границы и ответственность за порядок",
        light=["ясные правила", "ответственность", "стабильный каркас", "защита территории"],
        shadow=["жёсткость", "контроль вместо диалога", "страх хаоса"],
        inner="безопасность через контроль структуры",
        outer="задаёт рамки, роли, сроки, иерархию",
        relationships="нужны договорённости и уважение границ",
        work="управление, система, фиксация правил",
        money="бюджет, план, контроль риска",
        growth="отличать опору от жёсткости",
        rev_central="контроль подменяет заботу о смысле",
        rev_themes=["тирания правил", "потеря гибкости", "отказ от ответственности"],
        rev_trap="либо давит рамкой, либо бросает рамку совсем",
        amplifies=["work", "decision", "money", "conflict"],
        intensifies=[5, 11, 16],
        softens=[0, 3, 14],
    ),
    5: _card(
        5,
        "Иерофант",
        central="ценности, учение и свои/чужие «как надо»",
        light=["свои принципы", "передача смысла", "опора на традицию", "этический каркас"],
        shadow=["догма", "чужие правила вместо своих", "стыд за отклонение"],
        inner="хочет принадлежать смыслу и боится выйти из нормы",
        outer="ссылается на правила, учителей, «правильный путь»",
        relationships="вопрос общих ценностей и допустимого",
        work="нормы команды, наставничество, политика",
        money="«правильные» вложения vs свои критерии",
        growth="отличить живую ценность от чужой догмы",
        rev_central="бунт против формы или слепое следование",
        rev_themes=["чужие «как надо»", "ломание правил без опоры", "догма"],
        rev_trap="либо подчиняется норме, либо ломает её назло — без своей оси",
        amplifies=["purpose", "work", "decision", "growth"],
        intensifies=[4, 6, 20],
        softens=[0, 12, 17],
    ),
    6: _card(
        6,
        "Влюблённые",
        central="честный выбор сердца и согласование желания",
        light=["назвать желание", "союз", "согласование ценностей", "выбор с телом"],
        shadow=["колебание", "страх назвать желание", "выбор из долга"],
        inner="тянет к тому, что важно, и пугает цена выбора",
        outer="развилка, где нужно выбрать сторону желания",
        relationships="признание влечения/ценности союза или разрыва",
        work="выбор пути по смыслу, не только по статусу",
        money="деньги следуют за выбранной связью/путём",
        growth="сказать правду желания вслух",
        rev_central="развилка без решения или союз без честности",
        rev_themes=["страх выбора", "двойственность", "чужой выбор за себя"],
        rev_trap="остаётся «между», чтобы не потерять ни один вариант",
        amplifies=["choice", "relationships", "decision", "purpose"],
        intensifies=[15, 11, 19],
        softens=[9, 14, 2],
    ),
    7: _card(
        7,
        "Колесница",
        central="движение к цели через собранную волю",
        light=["направление", "прогресс", "дисциплина воли", "победа темпа"],
        shadow=["спешка", "гонка без паузы", "победа ценой интеграции"],
        inner="хочет уже быть «там» и не выносит двусмысленности",
        outer="ускоряет, давит на газ, держит курс",
        relationships="продвижение контакта или уход вперёд в одиночку",
        work="дедлайн, кампания, рывок к результату",
        money="агрессивный темп заработка/закрытия сделки",
        growth="держать курс, не теряя связь с телом",
        rev_central="разъезжающиеся reins: скорость без направления",
        rev_themes=["разброс воли", "затор", "победа без смысла"],
        rev_trap="давит газ, когда нужна стыковка двух сил",
        amplifies=["work", "decision", "conflict", "growth"],
        intensifies=[1, 16, 8],
        softens=[12, 14, 9],
    ),
    8: _card(
        8,
        "Сила",
        central="мягкая устойчивость и владение импульсом",
        light=["терпение", "мужество без давления", "ласковая твёрдость", "интеграция страсти"],
        shadow=["срыв", "сомнение в выдержке", "подавление вместо контакта"],
        inner="боится собственной силы и учится быть с ней рядом",
        outer="держит давление спокойно, не ломая и не сдаваясь",
        relationships="нежность + граница; не шантаж эмоцией",
        work="выдержка в сложном процессе без ломки людей",
        money="терпеливое наращивание без жадности/паники",
        growth="дружить с импульсом, а не давить его",
        rev_central="сила уходит в срыв или в самоотрицание",
        rev_themes=["срыв контроля", "слабость от подавления", "грубость"],
        rev_trap="либо душит импульс, либо отдаёт ему руль",
        amplifies=["inner_state", "relationships", "conflict", "growth"],
        intensifies=[15, 11, 19],
        softens=[16, 13, 7],
    ),
    9: _card(
        9,
        "Отшельник",
        central="своя правда, найденная в тишине",
        light=["уединение", "ясность наедине с собой", "внутренний ориентир", "зрелая дистанция"],
        shadow=["изоляция от правды", "уход от контакта", "холод как защита"],
        inner="нужен свет своего ответа, не шум чужих",
        outer="отступает, наблюдает, несёт фонарь себе",
        relationships="пауза ради ясности, не наказание молчанием",
        work="глубокая проработка без показухи",
        money="осторожность, отказ от шумных схем",
        growth="услышать свою правду без аудитории",
        rev_central="одиночество как бегство или отказ от нужной паузы",
        rev_themes=["изоляция", "страх тишины", "потеря ориентира"],
        rev_trap="прячется так глубоко, что фонарь гаснет",
        amplifies=["inner_state", "purpose", "decision", "growth"],
        intensifies=[2, 12, 18],
        softens=[6, 19, 3],
    ),
    10: _card(
        10,
        "Колесо Фортуны",
        central="сдвиг цикла; окно, которое не удержишь силой",
        light=["перемена фазы", "окно возможности", "поворот удачи", "ритм больше плана"],
        shadow=["застревание", "страх, что ничего не изменится", "магическое ожидание"],
        inner="хочет стабильности и одновременно жаждет сдвига",
        outer="обстоятельства поворачиваются; важно заметить фазу",
        relationships="смена динамики пары / круга",
        work="поворот рынка, роли, Timing",
        money="цикл дохода: не путать фазу с личной ценностью",
        growth="войти в поворот осознанно, не цепляясь",
        rev_central="сопротивление циклу или чувство «замкнуло»",
        rev_themes=["застревание", "неудачный timing", "повторение круга"],
        rev_trap="ждёт чуда, не делая шаг в открытое окно",
        amplifies=["decision", "work", "money", "undefined"],
        intensifies=[0, 16, 21],
        softens=[4, 14, 8],
    ),
    11: _card(
        11,
        "Справедливость",
        central="честный учёт последствий и баланса",
        light=["ясность фактов", "ответственность", "баланс обмена", "честный взгляд"],
        shadow=["холодная правота", "самооправдание", "счёт без жалости к себе"],
        inner="хочет справедливости и боится увидеть свою долю",
        outer="взвешивает, договаривается, фиксирует условия",
        relationships="честный разговор о вкладе и границах",
        work="оценка, контракт, последствия решения",
        money="справедливая цена, долги, ясный учёт",
        growth="признать свою часть без самобичевания",
        rev_central="перекос: вина / обеление / избегание учёта",
        rev_themes=["самооправдание", "несправедливый перекос", "откладывание разбора"],
        rev_trap="судит других строже, чем себя — или наоборот",
        amplifies=["decision", "conflict", "money", "work"],
        intensifies=[4, 6, 20],
        softens=[8, 17, 3],
    ),
    12: _card(
        12,
        "Повешенный",
        central="другой угол зрения; пауза ради ясности",
        light=["смена перспективы", "добровольная пауза", "сдача контроля ради смысла"],
        shadow=["ожидание, что решат другие", "застревание в жертве", "пассивность"],
        inner="старый угол зрения больше не работает",
        outer="замирает, смотрит иначе, отпускает привычный рычаг",
        relationships="пауза в динамике; видеть партнёра иначе",
        work="стоп-кадр перед стратегией; отказ от ложной активности",
        money="не торопить сделку, пока нет нового угла",
        growth="выдержать пустоту между старым и новым пониманием",
        rev_central="пауза стала избеганием или насильственной остановкой",
        rev_themes=["застревание", "мученичество", "отказ менять угол"],
        rev_trap="висит, но не смотрит — только страдает",
        amplifies=["inner_state", "decision", "purpose", "undefined"],
        intensifies=[9, 13, 18],
        softens=[7, 1, 19],
    ),
    13: _card(
        13,
        "Смерть",
        central="завершение формы, чтобы стало возможно следующее",
        light=["освобождение", "переход", "честное закрытие этапа"],
        shadow=["цепляние за старое", "страх пустоты", "отрицание конца"],
        inner="часть идентичности уже мертва, но рука ещё держит",
        outer="обрыв, финал, расчистка, необратимый сдвиг",
        relationships="конец формы союза или глубокая трансформация роли",
        work="закрытие проекта/роли; нельзя «чуть подлатать»",
        money="отпустить убыточную схему / старый источник",
        growth="разрешить пустоте быть дверью, не дырой",
        rev_central="отказ завершать; гниение вместо перехода",
        rev_themes=["цепляние", "страх пустоты", "затянувшийся конец"],
        rev_trap="тянет труп формы, чтобы не встретить неизвестность",
        amplifies=["growth", "relationships", "work", "decision"],
        intensifies=[16, 20, 10],
        softens=[17, 3, 19],
    ),
    14: _card(
        14,
        "Умеренность",
        central="смешивание без крайностей; ровный целебный темп",
        light=["баланс", "алхимия середины", "терпеливое смешение", "ровный темп"],
        shadow=["качели всё или ничего", "размывание границ ради «мира»"],
        inner="усталость от полюсов; ищет рабочую середину",
        outer="дозирует, смешивает, калибрует",
        relationships="мягкая настройка близости без крайностей",
        work="интеграция процессов; не героический рывок",
        money="устойчивый поток вместо скачков",
        growth="практика середины как силы, не слабости",
        rev_central="срыв баланса в крайность или в размытость",
        rev_themes=["крайности", "потеря меры", "ложный компромисс"],
        rev_trap="смешивает несовместимое и называет это миром",
        amplifies=["inner_state", "relationships", "growth", "work"],
        intensifies=[17, 8, 21],
        softens=[15, 16, 7],
    ),
    15: _card(
        15,
        "Дьявол",
        central="привязанность, привычный сценарий и скрытая выгода оставаться",
        light=["увидеть петлю", "назвать зависимость", "честность о выгоде"],
        shadow=["зависимость", "страх потери", "соблазн контроля через привязку"],
        inner="часть хочет свободы, часть кормится клеткой",
        outer="повтор паттерна, контракт с тенью, «не могу, но выбираю»",
        relationships="токсичная привязка / ревность / игра власти",
        work="золотая клетка, выгорающий контракт, зависимость от статуса",
        money="долг, жадность, страх остаться без",
        growth="увидеть выгоду оставаться — первый ключ к выходу",
        rev_central="петля видна; возможен первый шаг к выходу",
        rev_themes=["осознание зависимости", "разрыв иллюзии", "страх свободы"],
        rev_trap="говорит «вижу», но ещё кормит ту же выгоду",
        amplifies=["relationships", "money", "conflict", "inner_state"],
        intensifies=[18, 16, 6],
        softens=[8, 14, 17],
    ),
    16: _card(
        16,
        "Башня",
        central="трещина в мнимой надёжности; правда, которую нельзя достроить",
        light=["место для правды", "освобождение от лжи опоры", "очищение структуры"],
        shadow=["шок", "страх перемены", "отрицание трещины"],
        inner="знал, что конструкция шаткая, но держался за фасад",
        outer="внезапный обрыв, разоблачение, вынужденная перестройка",
        relationships="кризис, который нельзя замазать вежливостью",
        work="срыв плана, увольнение, коллапс системы",
        money="потеря «надёжного» источника",
        growth="строить на правде, а не на фасаде",
        rev_central="отложенный обвал или страх сильнее самой перемены",
        rev_themes=["затягивание краха", "микротрещины", "отказ слышать сигнал"],
        rev_trap="латает фасад, пока фундамент уже ушёл",
        amplifies=["conflict", "work", "decision", "growth"],
        intensifies=[13, 15, 10],
        softens=[17, 14, 19],
    ),
    17: _card(
        17,
        "Звезда",
        central="тонкая надежда и восстановление после усталости",
        light=["ориентир", "исцеление", "тихая вера", "открытость будущему"],
        shadow=["сомнение в восстановлении", "наивный оптимизм без опоры"],
        inner="хочет верить, что ещё можно — и боится разочарования",
        outer="мягкий свет после бури; жест заботы о себе",
        relationships="нежность без давления; надежда на живой контакт",
        work="восстановление смысла и вдохновения",
        money="бережный возврат к потоку после потерь",
        growth="разрешить себе надежду без доказательства",
        rev_central="свет есть, но доверие к нему тонкое",
        rev_themes=["сомнение", "потеря ориентира", "усталость верить"],
        rev_trap="ждёт знака с неба вместо маленького жеста восстановления",
        amplifies=["inner_state", "growth", "purpose", "relationships"],
        intensifies=[19, 3, 14],
        softens=[16, 15, 18],
    ),
    18: _card(
        18,
        "Луна",
        central="туман, страх и неясность; нужно назвать скрытое",
        light=["заметить скрытое", "назвать страх", "работать с образом, не фактом"],
        shadow=["додумывание", "принять желание за факт", "паранойя"],
        inner="тревога заполняет пробелы в информации",
        outer="неясные сигналы, сны, проекции, зыбкая почва",
        relationships="ревность, недосказанность, фантазии о другом",
        work="неясные условия; риск решать на слухах",
        money="туман вокруг цифр; страх вместо учёта",
        growth="отличить страх от сигнала",
        rev_central="туман редеет; скрытое становится заметнее",
        rev_themes=["прояснение", "риск принять желание за факт", "выход из проекции"],
        rev_trap="объявляет ясность раньше, чем проверил страх",
        amplifies=["inner_state", "relationships", "undefined", "conflict"],
        intensifies=[15, 2, 12],
        softens=[19, 11, 1],
    ),
    19: _card(
        19,
        "Солнце",
        central="ясность, видимость и тепло правды",
        light=["простота правды", "тепло", "радость без маски", "явность"],
        shadow=["страх уязвимости", "сдержанная радость", "ослепление успехом"],
        inner="хочет быть виден и боится, что свет сделает уязвимым",
        outer="всё становится очевидным; меньше теней",
        relationships="открытость, тепло, простые слова",
        work="результат виден; признание",
        money="прозрачный доход/успех",
        growth="разрешить себе радость без оправдания",
        rev_central="свет есть, но приглушён стыдом или перегревом",
        rev_themes=["сдержанная ясность", "страх уязвимости", "ложная бравада"],
        rev_trap="прячет радость или форсирует позитив",
        amplifies=["growth", "relationships", "work", "purpose"],
        intensifies=[17, 6, 21],
        softens=[18, 15, 16],
    ),
    20: _card(
        20,
        "Суд",
        central="зов к итогу; ответить на назревшее",
        light=["подвести черту", "ответить на зов", "признание пути", "второе рождение"],
        shadow=["откладывание разговора с собой", "суд как самобичевание"],
        inner="уже слышит зов, но медлит с ответом",
        outer="итог, объявление, возврат к старой теме на новом уровне",
        relationships="важный разговор / признание / примирение с прошлым",
        work="оценка результата, новый уровень ответственности",
        money="итог цикла; расчёт",
        growth="ответить «да» на то, что уже созрело",
        rev_central="зов есть, ответ откладывается",
        rev_themes=["прокрастинация итога", "самосуд", "глушение зова"],
        rev_trap="анализирует зов вместо ответа действием",
        amplifies=["purpose", "decision", "growth", "work"],
        intensifies=[13, 11, 21],
        softens=[12, 9, 14],
    ),
    21: _card(
        21,
        "Мир",
        central="завершение дуги и принятие целостности итога",
        light=["целостность", "принятие итога", "интеграция опыта", "закрытие круга"],
        shadow=["формально закрыто, внутри незавершённость", "страх нового круга"],
        inner="хочет закрыть главу и одновременно не отпускает",
        outer="финал проекта/этапа с ощущением полноты",
        relationships="зрелый итог союза или цикл близости",
        work="завершение фазы с признанием результата",
        money="собранный итог; стабилизация",
        growth="включить опыт в идентичность, не тащить хвост",
        rev_central="круг почти закрыт, но не хватает внутреннего «да»",
        rev_themes=["недозакрытие", "формальный финал", "страх следующего витка"],
        rev_trap="объявляет завершение, не интегрировав урок",
        amplifies=["growth", "purpose", "work", "relationships"],
        intensifies=[19, 10, 14],
        softens=[0, 16, 15],
    ),
}


SUIT_CORE: dict[str, dict[str, Any]] = {
    "wands": {
        "axis": "воля, инициатива, направление огня",
        "relationships": "страсть, инициатива в контакте, защита своего огня",
        "work": "старт, лидерство импульса, кампания",
        "money": "риск ради роста, энергия вкладывается в движение",
        "growth": "действовать из живого желания, не из долга",
        "light": ["импульс", "кураж", "своё направление"],
        "shadow": ["перегорание", "спешка", "разброс огня"],
        "element_soft": [14, 17, 3],
        "element_hard": [15, 16, 7],
    },
    "cups": {
        "axis": "чувство, связь, эмоциональная правда",
        "relationships": "близость, эмпатия, честное чувство",
        "work": "климат команды, смысл через контакт",
        "money": "ценность через заботу и обмен, не только цифру",
        "growth": "разрешить чувству быть данными",
        "light": ["открытость сердцу", "тепло", "резонанс"],
        "shadow": ["идеализация", "размытые границы", "уход в фантазию"],
        "element_soft": [4, 11, 1],
        "element_hard": [15, 18, 12],
    },
    "swords": {
        "axis": "мысль, слово, конфликт, ясность",
        "relationships": "разговор, граница, правда, которая режет",
        "work": "решение, стратегия, конфликт интересов",
        "money": "холодный расчёт, договор, спор о условиях",
        "growth": "назвать мысль без жестокости к себе",
        "light": ["ясная формулировка", "честный разрез", "ум как инструмент"],
        "shadow": ["ментальный шум", "резкость", "прокрутки"],
        "element_soft": [3, 8, 14],
        "element_hard": [15, 16, 9],
    },
    "pentacles": {
        "axis": "материя, труд, тело, практический результат",
        "relationships": "надёжность, быт, совместная база",
        "work": "навык, процесс, измеримый вклад",
        "money": "доход, ресурс, устойчивость",
        "growth": "воплотить идею в материю маленьким шагом",
        "light": ["опора", "терпеливый труд", "приземление"],
        "shadow": ["застревание в безопасности", "жадность к контролю", "откладывание"],
        "element_soft": [0, 17, 10],
        "element_hard": [15, 4, 16],
    },
}

RANK_CORE: dict[str, dict[str, Any]] = {
    "ace": {
        "phase": "семя / чистый потенциал",
        "inner": "чувствует начало раньше формы",
        "outer": "появляется искра или предложение начать",
        "rev": "искра глушится или форсируется",
        "trap": "хочет результат семени без посадки",
        "amplifies": ["growth", "decision", "purpose"],
    },
    "2": {
        "phase": "развилка / удержание двух сил",
        "inner": "стоит между вариантами и калибрует вес",
        "outer": "выбор или баланс двух направлений",
        "rev": "застревание в «или-или» без движения",
        "trap": "держит оба варианта, чтобы не потерять ни один",
        "amplifies": ["choice", "decision", "work"],
    },
    "3": {
        "phase": "рост через связь / первый плод сотрудничества",
        "inner": "хочет расшириться через других",
        "outer": "команда, отклик, видимый прогресс",
        "rev": "рост без корня или одиночный рывок",
        "trap": "празднует рост, игнорируя качество связи",
        "amplifies": ["work", "relationships", "growth"],
    },
    "4": {
        "phase": "стабилизация / опора / пауза в структуре",
        "inner": "нужна безопасная база",
        "outer": "фиксирует границы, дом, рамку",
        "rev": "застой под видом стабильности",
        "trap": "держит рамку, когда жизнь уже просит сдвига",
        "amplifies": ["inner_state", "money", "work"],
    },
    "5": {
        "phase": "трение / потеря / конкуренция",
        "inner": "боль или спор за место",
        "outer": "конфликт, утрата, борьба",
        "rev": "выход из боя или застревание в обиде",
        "trap": "воюет за правоту вместо нужды",
        "amplifies": ["conflict", "inner_state", "relationships"],
    },
    "6": {
        "phase": "обмен / признание / движение к гармонии",
        "inner": "хочет быть увиденным и отдать/принять справедливо",
        "outer": "жест признания, помощь, переход",
        "rev": "неравный обмен или отказ принять помощь",
        "trap": "ждёт аплодисментов вместо продолжения пути",
        "amplifies": ["relationships", "work", "growth"],
    },
    "7": {
        "phase": "испытание выбора / стратегии удержания",
        "inner": "проверяет, что действительно своё",
        "outer": "оборона позиции или соблазн лёгкого пути",
        "rev": "сдача границ или паранойя угроз",
        "trap": "защищает позицию, которая уже не живая",
        "amplifies": ["decision", "conflict", "work"],
    },
    "8": {
        "phase": "движение мастерства / уход / поток",
        "inner": "готов менять темп или оставлять старое",
        "outer": "ускорение, практика, уход",
        "rev": "затор или хаотичная спешка",
        "trap": "движется, чтобы не чувствовать",
        "amplifies": ["growth", "work", "decision"],
    },
    "9": {
        "phase": "почти итог / граница выдержки",
        "inner": "усталость у финиша; охраняет достигнутое",
        "outer": "последний рубеж, осторожность, накопление",
        "rev": "истощение или отказ от границы",
        "trap": "стоит на страже так долго, что не входит внутрь",
        "amplifies": ["inner_state", "money", "conflict"],
    },
    "10": {
        "phase": "итог цикла / полнота / перегруз формы",
        "inner": "несёт весь вес завершённого",
        "outer": "пик, завершение, передача дальше",
        "rev": "сброс ноши или крах от перегруза",
        "trap": "держит итог один, не делегируя",
        "amplifies": ["work", "relationships", "money"],
    },
    "page": {
        "phase": "вестник / ученичество / новость",
        "inner": "любопытство важнее статуса",
        "outer": "сообщение, приглашение учиться",
        "rev": "незрелость или глушение новости",
        "trap": "собирает новости вместо опыта",
        "amplifies": ["growth", "undefined", "inner_state"],
    },
    "knight": {
        "phase": "движение качества масти в мир",
        "inner": "импульс нести свою стихию наружу",
        "outer": "поход, предложение, резкий ход",
        "rev": "хаотичный натиск или трусость хода",
        "trap": "скачет, не сверив карту",
        "amplifies": ["decision", "work", "conflict"],
    },
    "queen": {
        "phase": "владение стихией изнутри; зрелая забота",
        "inner": "держит пространство масти без спектакля",
        "outer": "эмпатия/мастерство среды; регулирует климат",
        "rev": "выгорание заботы или холодный контроль",
        "trap": "заботится всеми, кроме своей опоры",
        "amplifies": ["relationships", "inner_state", "growth"],
    },
    "king": {
        "phase": "мастерство и ответственность вовне",
        "inner": "готов отвечать за поле масти",
        "outer": "лидерство, решение, структура стихии",
        "rev": "тирания экспертизы или отказ от трона",
        "trap": "правит формой, потеряв живую связь с мастью",
        "amplifies": ["work", "decision", "purpose"],
    },
}

# Per-card polish for minors where suit×rank would be too generic (id -> overrides).
MINOR_POLISH: dict[int, dict[str, Any]] = {
    26: {  # 5 of wands
        "central": "соревнование воль; трение инициатив без общего курса",
        "outer": "спор, конкурсы, хаотичная борьба за первенство",
    },
    40: {  # 5 of cups
        "central": "горечь потери при ещё доступных опорах",
        "inner": "смотрит на разлитое и не видит оставшееся",
    },
    42: {  # 7 of cups
        "central": "облако вариантов; соблазн фантазии вместо выбора",
        "trap": "выбирает картинку, а не проверяемый шаг",
    },
    43: {  # 8 of cups
        "central": "уход от эмоционально исчерпанного, даже если «почти хорошо»",
        "outer": "оставляет привычную чашу ради более честного пути",
    },
    51: {  # 2 of swords
        "central": "отказ видеть; баланс через закрытые глаза",
        "trap": "называет паузу нейтралитетом, пока правда давит",
    },
    52: {  # 3 of swords
        "central": "боль правды; разрез, который нельзя заговорить",
        "outer": "ясная боль, разрыв, жёсткая новость",
    },
    56: {  # 7 of swords
        "central": "обходной манёвр; стратегия вне прямого боя",
        "shadow_extra": ["самообман", "тихий уход от ответственности"],
    },
    57: {  # 8 of swords
        "central": "ментальная клетка; ограничение больше в уме, чем в фактах",
        "trap": "ждёт освобождения снаружи, не меняя мысль",
    },
    58: {  # 9 of swords
        "central": "ночная тревога; ум крутит худший сценарий",
        "inner": "страх занимает место сна и ясности",
    },
    68: {  # 5 of pentacles
        "central": "ощущение выброшенности из тепла ресурсов",
        "outer": "нехватка, исключение, холод материальной реальности",
    },
    71: {  # 8 of pentacles
        "central": "ремесло; повторяемая практика до качества",
        "growth": "мастерство через скучную точность",
    },
}


def _minor_id(suit: str, rank: str) -> int:
    return 22 + SUIT_ORDER.index(suit) * 14 + RANK_ORDER.index(rank)


def _build_minor(suit: str, rank: str, name_ru: str) -> dict[str, Any]:
    """Q1: unique archetype profile is SoT for minors (not rank×suit matrix)."""
    sid = _minor_id(suit, rank)
    profile = MINORS_Q1.get((suit, rank))
    if profile is None:
        raise KeyError(f"missing Q1 archetype for {(suit, rank)}")

    s = SUIT_CORE[suit]
    light = [str(x) for x in (profile.get("light") or [])][:5]
    shadow = [str(x) for x in (profile.get("shadow") or [])][:5]
    central = str(profile.get("central") or profile.get("core_scene") or "")
    inner = str(profile.get("central_conflict") or "")
    outer = str(profile.get("core_scene") or "")
    relationships = str(profile.get("relationship_lens") or "")
    work = str(profile.get("work_lens") or "")
    money = str(profile.get("money_lens") or "")
    growth = str(profile.get("growth_direction") or profile.get("inner_lens") or "")
    rev_central = str(profile.get("reversed_shift") or "")
    rev_themes = [rev_central[:80], str(profile.get("shadow_pattern") or "")[:80]]
    rev_themes = [t for t in rev_themes if t]
    rev_trap = str(profile.get("shadow_pattern") or "")

    idx = RANK_ORDER.index(rank)
    near: list[int] = []
    for j in (idx - 1, idx + 1, idx - 2, idx + 2):
        if 0 <= j < len(RANK_ORDER):
            near.append(_minor_id(suit, RANK_ORDER[j]))
    intensifies = list(dict.fromkeys([*near[:3], *s["element_hard"][:2]]))[:5]
    opp = OPPOSITE_SUIT[suit]
    softens = list(dict.fromkeys([_minor_id(opp, rank), *s["element_soft"][:3]]))[:5]

    amplifies = ["growth", "decision"]
    if suit == "cups":
        amplifies = ["relationships", "inner_state", "growth"]
    elif suit == "pentacles":
        amplifies = ["money", "work", "growth"]
    elif suit == "swords":
        amplifies = ["conflict", "decision", "inner_state"]
    elif suit == "wands":
        amplifies = ["work", "growth", "decision"]

    return _card(
        sid,
        name_ru,
        central=central,
        light=light or ["живая грань", "уникальный фокус"],
        shadow=shadow or ["ловушка карты", "срыв зрелости"],
        inner=inner,
        outer=outer,
        relationships=relationships,
        work=work,
        money=money,
        growth=growth,
        rev_central=rev_central,
        rev_themes=rev_themes or [rev_central, "сдвиг динамики"],
        rev_trap=rev_trap or rev_central,
        amplifies=amplifies,
        intensifies=intensifies,
        softens=softens,
        q1={
            "core_scene": profile.get("core_scene"),
            "central_conflict": profile.get("central_conflict"),
            "driving_need": profile.get("driving_need"),
            "shadow_pattern": profile.get("shadow_pattern"),
            "growth_direction": profile.get("growth_direction"),
            "work_lens": profile.get("work_lens"),
            "relationship_lens": profile.get("relationship_lens"),
            "money_lens": profile.get("money_lens"),
            "inner_lens": profile.get("inner_lens"),
            "reversed_shift": profile.get("reversed_shift"),
            "adjacent_distinction": profile.get("adjacent_distinction"),
        },
    )


def build_all() -> list[dict[str, Any]]:
    deck = {int(c["id"]): c for c in json.loads(DECK.read_text(encoding="utf-8"))}
    cards: list[dict[str, Any]] = []
    for cid in range(78):
        row = deck[cid]
        name_ru = str(row.get("name_ru") or row.get("name") or f"card_{cid}")
        if cid <= 21:
            entry = dict(MAJORS[cid])
            entry["name_ru"] = name_ru
            cards.append(entry)
            continue
        suit = str(row.get("suit") or "")
        slug = str(row.get("slug") or "")
        # slug like wands_ace / cups_2
        rank = slug.split("_", 1)[1] if "_" in slug else RANK_ORDER[(cid - 22) % 14]
        cards.append(_build_minor(suit, rank, name_ru))
    return cards


_Q1_FIELDS = (
    "core_scene",
    "central_conflict",
    "driving_need",
    "shadow_pattern",
    "growth_direction",
    "work_lens",
    "relationship_lens",
    "money_lens",
    "inner_lens",
    "reversed_shift",
    "adjacent_distinction",
)


def validate(cards: list[dict[str, Any]]) -> None:
    required = (
        "card_id",
        "name_ru",
        "central_archetype",
        "light",
        "shadow",
        "inner_conflict",
        "outer_expression",
        "domains",
        "reversed",
        "amplifies_questions",
        "intensifies_with",
        "softens_with",
        "upright_themes",
        "reversed_themes",
    )
    assert len(cards) == 78, len(cards)
    ids = [c["card_id"] for c in cards]
    assert ids == list(range(78)), "card_id must be 0..77 contiguous"
    banned = ("аркан", "Аркан")
    for c in cards:
        for key in required:
            assert key in c, (c["card_id"], key)
        for dkey in ("relationships", "work", "money", "growth"):
            assert str(c["domains"].get(dkey) or "").strip(), (c["card_id"], dkey)
        rev = c["reversed"]
        assert rev.get("central") and rev.get("themes") and rev.get("trap")
        blob = json.dumps(c, ensure_ascii=False)
        for b in banned:
            assert b not in blob, (c["card_id"], b)
        assert 2 <= len(c["light"]) <= 6
        assert 2 <= len(c["shadow"]) <= 6
        # Minors 22–77: full Q1 archetype profile required.
        if int(c["card_id"]) >= 22:
            for qk in _Q1_FIELDS:
                assert str(c.get(qk) or "").strip(), (c["card_id"], qk)
            assert len(str(c["adjacent_distinction"]).strip()) >= 12, c["card_id"]


def main() -> None:
    cards = build_all()
    validate(cards)
    payload = {
        "contract_version": "tarot_knowledge_v1",
        "locale": "ru",
        "card_count": len(cards),
        "cards": cards,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(cards)} cards)")


if __name__ == "__main__":
    main()
