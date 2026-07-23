"""D1 — planet × sign → sphere-specific manifestation traits.

No boilerplate «задаёт тон». Unsupported pairs → omit (caller), not fake personal copy.
"""

from __future__ import annotations

import re
from typing import Any

SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

_SIGN_ALIASES = {
    "овен": "aries",
    "телец": "taurus",
    "близнецы": "gemini",
    "рак": "cancer",
    "лев": "leo",
    "дева": "virgo",
    "весы": "libra",
    "скорпион": "scorpio",
    "стрелец": "sagittarius",
    "козерог": "capricorn",
    "водолей": "aquarius",
    "рыбы": "pisces",
}


def normalize_sign(sign: str | None) -> str | None:
    if not sign:
        return None
    s = re.sub(r"\s+", " ", str(sign).strip().lower())
    if s in SIGNS:
        return s
    if s in _SIGN_ALIASES:
        return _SIGN_ALIASES[s]
    # English title / mixed
    for name in SIGNS:
        if s == name or s.startswith(name):
            return name
    return None


# sphere → planet → sign → {ru, en}
# Texts: sphere-specific manifestation, not generic sign passport / longitudinal claim.
_TRAITS: dict[str, dict[str, dict[str, dict[str, str]]]] = {
    "love": {
        "venus": {
            "aries": {
                "ru": "В близости ты быстрее зажигаешься, когда есть прямая инициатива и честный телесный интерес без долгих намёков.",
                "en": "In closeness you light up faster when initiative is direct and interest is named without long hints.",
            },
            "taurus": {
                "ru": "В близости ты раскрываешься через устойчивый телесный комфорт, привычный ритм касаний и спокойную предсказуемость.",
                "en": "In closeness you open through steady bodily comfort, a familiar touch rhythm, and calm predictability.",
            },
            "gemini": {
                "ru": "В близости ты оживляешься через живой разговор, игру смыслов и лёгкую смену ракурса без тяжёлой драмы.",
                "en": "In closeness you come alive through lively talk, playful meaning, and light shifts of angle without heavy drama.",
            },
            "cancer": {
                "ru": "В близости ты быстрее раскрываешься там, где есть эмоциональная безопасность, знакомый ритм и заметная забота в мелочах.",
                "en": "In closeness you open faster where there is emotional safety, a familiar rhythm, and care visible in small things.",
            },
            "leo": {
                "ru": "В близости тебе важно быть увиденным: тёплый отклик, щедрость внимания и право сиять без стыда за желание.",
                "en": "In closeness you need to be seen: warm response, generous attention, and room to shine without shame for wanting.",
            },
            "virgo": {
                "ru": "В близости ты включаешься через точные жесты заботы, порядок в быту рядом и уважение к личным границам тела.",
                "en": "In closeness you engage through precise care, order in shared daily life, and respect for body boundaries.",
            },
            "libra": {
                "ru": "В близости ты ищешь равный обмен: красивый тон разговора, взаимность шага и ощущение, что тебя не перетягивают.",
                "en": "In closeness you seek equal exchange: a fair tone, mutual steps, and not being pulled off balance.",
            },
            "scorpio": {
                "ru": "В близости тебе нужна глубина доверия: один честный слой правды важнее множества поверхностных знаков внимания.",
                "en": "In closeness you need depth of trust: one honest layer of truth beats many surface gestures.",
            },
            "sagittarius": {
                "ru": "В близости тебя питает пространство свободы рядом: общий смысл, честный юмор и право не сжиматься в контроле.",
                "en": "In closeness you are fed by freedom beside someone: shared meaning, honest humor, and no shrinking under control.",
            },
            "capricorn": {
                "ru": "В близости ты опираешься на надёжность поступка: обещание, которое держат, важнее красивых слов о чувствах.",
                "en": "In closeness you lean on reliable action: a kept promise matters more than pretty words about feelings.",
            },
            "aquarius": {
                "ru": "В близости тебе нужен воздух дружбы внутри пары: уважение к странности, личный контур и контакт без собственничества.",
                "en": "In closeness you need friendship-air inside the bond: respect for oddness, a personal contour, contact without possession.",
            },
            "pisces": {
                "ru": "В близости ты растворяешься в тонкой эмпатии — и поэтому особенно нуждаешься в ясной бережной границе «я / мы».",
                "en": "In closeness you dissolve into soft empathy — so you especially need a clear gentle boundary of I / we.",
            },
        },
        "sun": {
            "aries": {
                "ru": "В любви твой базовый ход — начинать контакт самому; без ясного «да» инициатива быстро выгорает в раздражении.",
                "en": "In love your base move is to start contact yourself; without a clear yes, initiative burns into irritation.",
            },
            "taurus": {
                "ru": "В любви тебе нужна опора на стабильность: резкие смены настроения партнёра выбивают почву сильнее, чем спор о деталях.",
                "en": "In love you need stability underfoot: a partner's sharp mood swings cost more than a detail argument.",
            },
            "gemini": {
                "ru": "В любви ты держишь связь через обновление темы; затянувшаяся тишина без смысла ощущается как разрыв.",
                "en": "In love you hold the bond by renewing the topic; long silence without meaning feels like a break.",
            },
            "cancer": {
                "ru": "В любви ты защищаешь свой внутренний дом; холодная отстранённость бьёт сильнее прямой критики.",
                "en": "In love you guard an inner home; cold distance hits harder than direct criticism.",
            },
            "leo": {
                "ru": "В любви тебе важно чувство взаимного света: обесценивание желания гасит контакт быстрее отказа в мелочи.",
                "en": "In love mutual warmth matters: devaluing desire kills contact faster than a small refusal.",
            },
            "virgo": {
                "ru": "В любви ты чинишь связь делом; хаос и невыполненные мелочи копятся в обиду без большого скандала.",
                "en": "In love you repair by doing; chaos and undone small things pile into resentment without a big fight.",
            },
            "libra": {
                "ru": "В любви ты балансируешь «мы»; перекос в одну сторону без разговора разрушает тепло быстрее спора о вкусах.",
                "en": "In love you balance the we; one-sided tilt without talk kills warmth faster than a taste dispute.",
            },
            "scorpio": {
                "ru": "В любви ты проверяешь правду взглядом; фальшь в мелочи бьёт сильнее открытого конфликта.",
                "en": "In love you test truth by feel; a small false note hits harder than an open conflict.",
            },
            "sagittarius": {
                "ru": "В любви тебе нужен горизонт вместе; ощущение клетки гасит влечение быстрее бытовой усталости.",
                "en": "In love you need a shared horizon; a cage feeling kills desire faster than ordinary tiredness.",
            },
            "capricorn": {
                "ru": "В любви ты строишь на долгом доверии; пустые обещания ломают близость сильнее временной дистанции.",
                "en": "In love you build on long trust; empty promises break closeness more than temporary distance.",
            },
            "aquarius": {
                "ru": "В любви тебе нужна честная дистанция внутри связи; липкий контроль выключает тепло быстрее ссоры.",
                "en": "In love you need honest distance inside the bond; sticky control shuts warmth faster than a quarrel.",
            },
            "pisces": {
                "ru": "В любви ты тонко считываешь настроение; жёсткий тон без объяснения ранит сильнее фактического отказа.",
                "en": "In love you read mood finely; a hard tone without explanation wounds more than a factual no.",
            },
        },
    },
    "money": {
        "jupiter": {
            "aries": {
                "ru": "В деньгах рост приходит через смелый первый вклад с потолком — без потолка импульс съедает запас.",
                "en": "With money growth comes via a bold first stake with a cap — without a cap, impulse eats the buffer.",
            },
            "taurus": {
                "ru": "В деньгах тебе легче наращивать ценность медленными регулярными вложениями, чем одним резким рывком.",
                "en": "With money you grow value more easily through slow regular deposits than one sharp leap.",
            },
            "gemini": {
                "ru": "В деньгах возможности открываются через несколько каналов сразу — риск в том, чтобы не размазать фокус.",
                "en": "With money openings arrive through several channels at once — the risk is smearing focus.",
            },
            "cancer": {
                "ru": "В деньгах тебе спокойнее, когда рост опирается на чувство «есть запас на близких и на себя».",
                "en": "With money you feel calmer when growth rests on a sense of buffer for kin and for yourself.",
            },
            "leo": {
                "ru": "В деньгах щедрый жест усиливает ощущение ценности — но без учёта он быстро превращается в дыру статуса.",
                "en": "With money a generous gesture boosts felt worth — without tracking it becomes a status hole.",
            },
            "virgo": {
                "ru": "В деньгах рост держится на точной настройке: маленькая правка расхода даёт больше, чем громкий план.",
                "en": "With money growth holds on precise tuning: a small spend fix beats a loud plan.",
            },
            "libra": {
                "ru": "В деньгах тебе важно, чтобы обмен был взаимным: односторонние «вложения в отношения» размывают ресурс.",
                "en": "With money mutual exchange matters: one-sided relationship spending blurs the resource.",
            },
            "scorpio": {
                "ru": "В деньгах сила в контроле скрытых обязательств — прозрачность долга важнее оптимистичного обещания роста.",
                "en": "With money power is in tracking hidden obligations — debt clarity beats optimistic growth talk.",
            },
            "sagittarius": {
                "ru": "В деньгах горизонт расширяется через обучение и дальний ход — без якоря цифр энтузиазм разлетается.",
                "en": "With money the horizon widens via learning and a long move — without number anchors, enthusiasm scatters.",
            },
            "capricorn": {
                "ru": "В деньгах рост выглядит как лестница достижений: статус и дисциплина платежа важнее случайного куша.",
                "en": "With money growth looks like an achievement ladder: payment discipline beats a lucky score.",
            },
            "aquarius": {
                "ru": "В деньгах тебе ближе нестандартный канал дохода и честный разговор о ценности, чем чужой шаблон успеха.",
                "en": "With money an unusual income channel and honest value talk beat someone else's success template.",
            },
            "pisces": {
                "ru": "В деньгах граница «своё / чужое» легко размывается — явная сумма и срок спасают от тихого истощения.",
                "en": "With money the mine/yours line blurs easily — a clear sum and deadline prevent quiet drain.",
            },
        },
        "saturn": {
            "aries": {
                "ru": "В деньгах дисциплина для тебя — вовремя остановить импульс покупки, а не накопить ещё один план «потом».",
                "en": "With money discipline means stopping an impulse buy in time — not stacking another later-plan.",
            },
            "taurus": {
                "ru": "В деньгах опора — привычка держать базу: скучный регулярный платёж себе надёжнее вдохновения.",
                "en": "With money the brace is a base habit: a boring regular payment to yourself beats inspiration.",
            },
            "gemini": {
                "ru": "В деньгах ограничение полезно как один выбранный фокус учёта — иначе цифры размножаются без решения.",
                "en": "With money a useful limit is one chosen tracking focus — otherwise numbers multiply without a call.",
            },
            "cancer": {
                "ru": "В деньгах зрелость — отделить заботу о близких от самопожертвования бюджетом без своего запаса.",
                "en": "With money maturity separates care for others from self-erasure of the budget with no buffer.",
            },
            "leo": {
                "ru": "В деньгах взросление — платить за видимость осознанно: статусный жест только из просчитанного слота.",
                "en": "With money growing up means paying for visibility on purpose: status gestures only from a budgeted slot.",
            },
            "virgo": {
                "ru": "В деньгах сатурнова опора — довести учёт до конца недели, а не бесконечно улучшать таблицу.",
                "en": "With money Saturn's brace is finishing the week's books — not endlessly refining the sheet.",
            },
            "libra": {
                "ru": "В деньгах важно вовремя назвать цену своего вклада — вежливость без цифры оставляет тебя в минусе.",
                "en": "With money name the price of your contribution in time — politeness without a number leaves you short.",
            },
            "scorpio": {
                "ru": "В деньгах жёсткая ясность по долгам и паям снимает тревогу сильнее, чем оптимистичный «как-нибудь».",
                "en": "With money hard clarity on debts and shares calms more than an optimistic somehow.",
            },
            "sagittarius": {
                "ru": "В деньгах рамка — один дальняя цель и запрет на три параллельных «важных» траты сразу.",
                "en": "With money the frame is one long goal and a ban on three parallel important spends at once.",
            },
            "capricorn": {
                "ru": "В деньгах твоя сила — долгий платёжный каркас: скучный график надёжнее вдохновляющего рывка.",
                "en": "With money your strength is a long payment frame: a boring schedule beats an inspired surge.",
            },
            "aquarius": {
                "ru": "В деньгах полезно зафиксировать свои правила обмена, даже если они не похожи на «как принято».",
                "en": "With money it helps to fix your own exchange rules even if they are not how it is done.",
            },
            "pisces": {
                "ru": "В деньгах граница расхода спасает от размытого «помогу потом» — сумма и дата важнее настроения.",
                "en": "With money a spend boundary saves you from vague I'll help later — sum and date beat mood.",
            },
        },
        "sun": {
            "aries": {
                "ru": "В деньгах базовый ход — решить и двинуть сумму; без решения импульс крутится впустую.",
                "en": "With money the base move is decide and move a sum; without a call, impulse spins in place.",
            },
            "taurus": {
                "ru": "В деньгах базовый ход — удержать уже заработанное; потеря стабильности бьёт больнее упущенной выгоды.",
                "en": "With money the base move is hold what is earned; losing stability hurts more than missed upside.",
            },
            "gemini": {
                "ru": "В деньгах базовый ход — собрать факты из двух источников, затем выбрать один канал действия.",
                "en": "With money the base move is gather facts from two sources, then pick one action channel.",
            },
            "cancer": {
                "ru": "В деньгах базовый ход — сначала закрыть чувство безопасности, потом говорить о росте.",
                "en": "With money the base move is secure the safety feeling first, then talk growth.",
            },
            "leo": {
                "ru": "В деньгах базовый ход — связать трату с самоуважением осознанно, а не в пику стыду.",
                "en": "With money the base move is link a spend to self-respect on purpose — not as a shame rebound.",
            },
            "virgo": {
                "ru": "В деньгах базовый ход — починить одну дыру в учёте до новых вложений.",
                "en": "With money the base move is fix one leak in tracking before new investments.",
            },
            "libra": {
                "ru": "В деньгах базовый ход — выровнять обмен: что уходит и что возвращается в ясных единицах.",
                "en": "With money the base move is rebalance exchange: what leaves and what returns in clear units.",
            },
            "scorpio": {
                "ru": "В деньгах базовый ход — вскрыть скрытый хвост обязательств, прежде чем обещать рост.",
                "en": "With money the base move is expose a hidden obligation tail before promising growth.",
            },
            "sagittarius": {
                "ru": "В деньгах базовый ход — выбрать один горизонт и отрезать соблазн трёх параллельных ставок.",
                "en": "With money the base move is pick one horizon and cut the urge for three parallel bets.",
            },
            "capricorn": {
                "ru": "В деньгах базовый ход — поставить платёж в календарь как работу, а не ждать настроения.",
                "en": "With money the base move is calendar the payment as work — not wait for mood.",
            },
            "aquarius": {
                "ru": "В деньгах базовый ход — назвать свою нестандартную цену вслух, не подгоняя её под чужой шаблон.",
                "en": "With money the base move is name your nonstandard price aloud without forcing a foreign template.",
            },
            "pisces": {
                "ru": "В деньгах базовый ход — отделить помощь другим от своего минимального запаса одной цифрой.",
                "en": "With money the base move is separate help to others from your minimum buffer with one number.",
            },
        },
    },
    "decisions": {
        "saturn": {
            "aries": {
                "ru": "В решениях зрелость — не отменять выбор импульсом «ещё раз переиграть», а зафиксировать ход и точку проверки.",
                "en": "In decisions maturity is not undoing a call with one more redo — lock the move and a check point.",
            },
            "taurus": {
                "ru": "В решениях тебе помогает медленная фиксация: один выбранный вариант держать, пока факты реально не сменились.",
                "en": "In decisions slow locking helps: hold one chosen option until facts truly change.",
            },
            "gemini": {
                "ru": "В решениях рамка — сузить до двух формулировок; иначе ум плодит ветки без закрытия.",
                "en": "In decisions the frame is narrow to two phrasings — else the mind grows branches without close.",
            },
            "cancer": {
                "ru": "В решениях важно отделить страх за близких от своего критерия — иначе выбор тонет в чужой тревоге.",
                "en": "In decisions separate fear for others from your criterion — else the call drowns in borrowed anxiety.",
            },
            "leo": {
                "ru": "В решениях тебе нужна видимая ответственность: назвать выбор вслух и принять его цену без перекладывания.",
                "en": "In decisions you need visible ownership: name the call aloud and take its cost without passing it off.",
            },
            "virgo": {
                "ru": "В решениях опора — довести один критерий до конца, а не улучшать список критериев бесконечно.",
                "en": "In decisions the brace is finish one criterion — not endlessly improve the criteria list.",
            },
            "libra": {
                "ru": "В решениях ловушка — вечный баланс; сила в том, чтобы объявить свой перевес и жить с ним до пересмотра.",
                "en": "In decisions the trap is endless balancing; strength is declaring your tilt and living with it until review.",
            },
            "scorpio": {
                "ru": "В решениях тебе нужна правда о цене выбора; сладкая версия без риска не даёт опереться.",
                "en": "In decisions you need the true cost of the call; a sweet risk-free version gives no footing.",
            },
            "sagittarius": {
                "ru": "В решениях горизонт важен, но без даты хода он остаётся мечтой — поставь срок первому шагу.",
                "en": "In decisions horizon matters, but without a move date it stays a dream — deadline the first step.",
            },
            "capricorn": {
                "ru": "В решениях твоя сила — превратить выбор в график: критерий, срок, ответственный — ты.",
                "en": "In decisions your strength is turning the call into a schedule: criterion, deadline, owner — you.",
            },
            "aquarius": {
                "ru": "В решениях полезно опереться на своё правило, даже если круг ждёт «как принято» — назови своё условие.",
                "en": "In decisions lean on your own rule even if the circle expects the usual — name your condition.",
            },
            "pisces": {
                "ru": "В решениях туман настроения снимается одной внешней опорой: цифра, дата или чужой ясный факт.",
                "en": "In decisions mood fog lifts with one outer brace: a number, a date, or one clear external fact.",
            },
        },
        "mercury": {
            "aries": {
                "ru": "В решениях мысль у тебя короткая и боевая: формулируй выбор в одном предложении — иначе спор размножается.",
                "en": "In decisions your thought is short and sharp: phrase the call in one sentence — else the debate multiplies.",
            },
            "taurus": {
                "ru": "В решениях тебе помогает повторить вывод своими словами и дать ему отлежаться до действия.",
                "en": "In decisions it helps to restate the conclusion in your words and let it sit before acting.",
            },
            "gemini": {
                "ru": "В решениях ты видишь развилки быстро — полезно записать две ветки и вычеркнуть третью как шум.",
                "en": "In decisions you see forks fast — write two branches and strike the third as noise.",
            },
            "cancer": {
                "ru": "В решениях внутренний диалог окрашен чувством; вынеси критерий на бумагу, чтобы не решить из обиды.",
                "en": "In decisions the inner talk is feeling-tinted; put the criterion on paper so you do not decide from hurt.",
            },
            "leo": {
                "ru": "В решениях тебе важно, чтобы формулировка была достойной — скажи выбор так, чтобы можно было за него стоять.",
                "en": "In decisions the wording must feel worthy — say the call so you can stand behind it.",
            },
            "virgo": {
                "ru": "В решениях ум цепляется за ошибки; ограничь проверку одним кругом фактов, затем закрывай.",
                "en": "In decisions the mind catches on errors; limit the check to one fact pass, then close.",
            },
            "libra": {
                "ru": "В решениях формулировки «за / против» помогают выйти из качелей — выбери сторону на время.",
                "en": "In decisions pro/con phrasing helps leave the swing — pick a side for a time.",
            },
            "scorpio": {
                "ru": "В решениях ты читаешь подтекст; проверь один скрытый мотив вслух, прежде чем утвердить ход.",
                "en": "In decisions you read subtext; check one hidden motive aloud before locking the move.",
            },
            "sagittarius": {
                "ru": "В решениях большая идея должна сжаться в следующий конкретный шаг — иначе смысл улетает.",
                "en": "In decisions a big idea must compress into the next concrete step — else meaning flies off.",
            },
            "capricorn": {
                "ru": "В решениях полезен сухой протокол: что решено, к какому сроку, что считается сделанным.",
                "en": "In decisions a dry protocol helps: what is decided, by when, what counts as done.",
            },
            "aquarius": {
                "ru": "В решениях неожиданный угол зрения — сила; зафиксируй своё условие отдельно от мнения большинства.",
                "en": "In decisions an odd angle is strength; fix your condition apart from majority opinion.",
            },
            "pisces": {
                "ru": "В решениях образы путают факты; переведи ощущение в одну проверяемую фразу перед выбором.",
                "en": "In decisions images confuse facts; turn the feeling into one testable sentence before choosing.",
            },
        },
        "sun": {
            "aries": {
                "ru": "В решениях базовый ход — выбрать быстро и назначить проверку; без проверки скорость становится хаосом.",
                "en": "In decisions the base move is choose fast and set a review — without review, speed becomes chaos.",
            },
            "taurus": {
                "ru": "В решениях базовый ход — не дергать выбранное без новых фактов.",
                "en": "In decisions the base move is not yank the chosen option without new facts.",
            },
            "gemini": {
                "ru": "В решениях базовый ход — сравнить две ясные опции и отбросить остальное как шум.",
                "en": "In decisions the base move is compare two clear options and drop the rest as noise.",
            },
            "cancer": {
                "ru": "В решениях базовый ход — спросить, что защищает твоё спокойствие, и выбрать от этого.",
                "en": "In decisions the base move is ask what protects your calm — and choose from that.",
            },
            "leo": {
                "ru": "В решениях базовый ход — взять авторство выбора на себя при свидетелях или в записи.",
                "en": "In decisions the base move is own the call — with witnesses or in writing.",
            },
            "virgo": {
                "ru": "В решениях базовый ход — исправить один конкретный изъян плана, затем действовать.",
                "en": "In decisions the base move is fix one concrete flaw in the plan, then act.",
            },
            "libra": {
                "ru": "В решениях базовый ход — объявить временный перевес и жить с ним до даты пересмотра.",
                "en": "In decisions the base move is declare a temporary tilt and live with it until review day.",
            },
            "scorpio": {
                "ru": "В решениях базовый ход — назвать настоящую цену варианта, включая то, что неприятно признать.",
                "en": "In decisions the base move is name the real cost of the option, including what is hard to admit.",
            },
            "sagittarius": {
                "ru": "В решениях базовый ход — связать выбор с дальним смыслом и ближайшим шагом в один день.",
                "en": "In decisions the base move is link the call to long meaning and the nearest step the same day.",
            },
            "capricorn": {
                "ru": "В решениях базовый ход — вписать выбор в срок и считать несделанное долгом перед собой.",
                "en": "In decisions the base move is put the call on a deadline and treat undone as a debt to yourself.",
            },
            "aquarius": {
                "ru": "В решениях базовый ход — проверить, не подменяешь ли своё правило чужим удобством.",
                "en": "In decisions the base move is check you are not swapping your rule for someone else's comfort.",
            },
            "pisces": {
                "ru": "В решениях базовый ход — вынести выбор из тумана настроения в одну внешнюю опору.",
                "en": "In decisions the base move is lift the call out of mood fog onto one outer brace.",
            },
        },
    },
}

# Preferred planet order per sphere (same as projector).
_SPHERE_PLANETS = {
    "love": ("venus", "sun"),
    "money": ("jupiter", "saturn", "sun"),
    "decisions": ("saturn", "mercury", "sun"),
}


def resolve_sphere_trait(
    sphere_id: str,
    natal: dict[str, Any],
    *,
    locale: str = "ru",
) -> dict[str, Any] | None:
    """Return trait pack or None if unsupported (caller must omit, not invent)."""
    en = (locale or "ru").lower().startswith("en")
    planets = _SPHERE_PLANETS.get(sphere_id) or ()
    # Prefer explicit planet_bullets only if non-empty and not boilerplate — still tag as bullet
    bullets = natal.get("planet_bullets") if isinstance(natal.get("planet_bullets"), dict) else {}

    for planet in planets:
        sign_raw = natal.get(f"{planet}_sign")
        sign = normalize_sign(str(sign_raw) if sign_raw else None)
        bl = bullets.get(planet)
        if isinstance(bl, list) and bl and str(bl[0]).strip():
            text = str(bl[0]).strip()
            # Reject known boilerplate if somehow injected
            if "задаёт тон проявления" in text.lower() or "colors how this area" in text.lower():
                pass
            else:
                return {
                    "text": text[:420],
                    "planet": planet,
                    "sign": sign,
                    "trait_rule_id": f"trait:{sphere_id}.{planet}.bullet",
                    "source": "planet_bullet",
                }
        if not sign:
            continue
        row = ((_TRAITS.get(sphere_id) or {}).get(planet) or {}).get(sign)
        if not row:
            continue
        text = row.get("en" if en else "ru") or row.get("ru") or ""
        if len(text.strip()) < 40:
            continue
        return {
            "text": text.strip(),
            "planet": planet,
            "sign": sign,
            "trait_rule_id": f"trait:{sphere_id}.{planet}.{sign}",
            "source": "trait_table",
        }
    return None


def trait_supported(sphere_id: str, planet: str, sign: str | None) -> bool:
    s = normalize_sign(sign)
    if not s:
        return False
    return bool(((_TRAITS.get(sphere_id) or {}).get(planet) or {}).get(s))
