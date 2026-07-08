#!/usr/bin/env python3
"""One-shot merge of compat.* i18n keys into app.en.json / app.ru.json (run from repo root)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "CONTENT" / "i18n"

# (key, en, ru)
ROWS: list[tuple[str, str, str]] = [
    # Elements / modalities (sign pair hints)
    ("compat.element.same", "natural mutual understanding", "естественное взаимопонимание"),
    ("compat.element.fire_air", "quick mutual spark", "быстрая взаимная подпитка"),
    ("compat.element.earth_water", "gentle grounding and support", "мягкое укрепление и опора"),
    ("compat.element.fire_water", "contrast between impulse and feeling", "контраст импульса и чувств"),
    ("compat.element.earth_air", "tension between logic and practicality", "конфликт логики и практичности"),
    ("compat.element.mixed", "variable synchronization", "переменная синхронизация"),
    ("compat.modality.same", "shared working rhythm", "общий рабочий ритм"),
    ("compat.modality.cardinal_fixed", "balance between starting and holding steady", "баланс старта и удержания"),
    ("compat.modality.cardinal_mutable", "fast adaptation with a rush risk", "быстрая адаптация с риском спешки"),
    ("compat.modality.fixed_mutable", "a gap in flexibility versus inertia", "разница в гибкости и инерции"),
    ("compat.modality.mixed", "uneven but workable pacing", "нестабильная, но управляемая динамика"),
    # Relationship context (API + LLM)
    ("compat.context.unspecified", "context not specified", "контекст не указан"),
    ("compat.context.just_met", "just getting to know each other", "только познакомились"),
    ("compat.context.mutual_attraction", "mutual attraction", "есть притяжение"),
    ("compat.context.in_relationship", "already in a relationship", "уже в отношениях"),
    ("compat.context.unclear", "situation is unclear", "непонятная ситуация"),
    ("compat.context.conflict_distance", "conflict or distance", "конфликт или дистанция"),
    ("compat.context.split_but_pull", "split but still pulled together", "расстались, но тянет"),
    # Product context hooks
    ("compat.sign.ctx.just_met", "You're at the start: lots of guesses and fast reads — below is how this pair usually unfolds.", "Вы на старте: много гипотез и быстрых интерпретаций — ниже про то, как эта пара обычно раскрывается."),
    ("compat.sign.ctx.mutual_attraction", "There's clear attraction — next it depends on how you negotiate pace and honesty.", "Есть явное притяжение — дальше всё решает то, как вы договариваетесь о темпе и честности."),
    ("compat.sign.ctx.in_relationship", "You're already in contact — below is about repeating patterns, not the first spark.", "Вы уже в контакте — ниже про повторяющиеся сценарии, а не про «первый импульс»."),
    ("compat.sign.ctx.unclear", "The situation is fuzzy — naming the dynamic helps you stop guessing and bending facts.", "Ситуация расплывчата — разбор помогает назвать динамику, чтобы перестать гадать и подгонять факты."),
    ("compat.sign.ctx.conflict_distance", "There's distance or conflict — below is the typical loop and where it can break.", "Есть дистанция или конфликт — ниже про типичный цикл и где его можно разорвать."),
    ("compat.sign.ctx.split_but_pull", "You're not formally together but it pulls — below is how attraction depends on clarity and boundaries.", "Формально вы не вместе, но тянет — ниже про зависимость притяжения от ясности и границ."),
    ("compat.sign.ctx.unspecified", "Below isn't a sign cheat sheet — it's the usual contact dynamic between you.", "Ниже — не таблица знаков, а типичная динамика контакта между вами."),
    # Overview
    ("compat.sign.overview.bridge", "Between {from_name} and {to_name} you’ll notice a «{element_relation}» thread. Early on that often feels like recognition or interest — but it doesn’t erase pace differences.", "Между {from_name} и {to_name} заметна связка «{element_relation}». На первых порах это часто даёт ощущение узнавания или интереса — но не отменяет различий в ритме."),
    ("compat.sign.overview.rhythm", "Different pacing shows up wherever «{rhythm_relation}» kicks in. One of you may move into contact faster while the other steps back to stay in control or not burn out.", "Разный ритм проявляется там, где включается «{rhythm_relation}». Один из вас может быстрее идти в контакт, второй — отстраняться, чтобы сохранить контроль или не перегореть."),
    ("compat.sign.overview.not_verdict", "This isn't a verdict on compatibility — it's dynamics that are easier to hold once they're named.", "Это не приговор совместимости — это динамика, которую проще держать в руках, когда она названа."),
    ("compat.sign.overview.extra.conflict", "Right now it matters more to see the repeating fight/silence script than «who's right on the topic».", "Сейчас важнее смотреть на повторяющийся сценарий ссоры/молчания, чем на «кто прав по теме»."),
    ("compat.sign.overview.extra.split", "When it pulls after a breakup, separate attraction from a real shot at contact without the old loop.", "Когда тянет после расставания, полезно различать притяжение и реальную возможность контакта без старого цикла."),
    # Taglines (template surface)
    ("compat.tagline.t1", "strong pull, unstable pacing", "сильное притяжение, но нестабильная динамика"),
    ("compat.tagline.t2", "strong pull and sharp conflict edges", "сильное притяжение и острые углы в конфликте"),
    ("compat.tagline.t3", "steadier day-to-day than spark and novelty", "ровнее в быту, чем в искре и новизне"),
    ("compat.tagline.t4", "strong chemistry — don't confuse it with safety", "сильная химия — важно не путать её с безопасностью"),
    ("compat.tagline.t5", "the bond shifts by phase — normal if you talk about it", "связь чувствуется по-разному в разные фазы — это нормально, если вы про это говорите"),
    # Static report (GET signs paragraphs etc.)
    (
        "compat.static.summary",
        "{from_name} & {to_name}: {element_relation}; day-to-day, {rhythm_relation} matters most.",
        "{from_name} и {to_name}: {element_relation}, а в повседневном ритме важнее всего {rhythm_relation}.",
    ),
    (
        "compat.static.para1",
        "{from_name} and {to_name} align fastest where neither tries to force the other's pace.",
        "{from_name} и {to_name} быстрее совпадают там, где не пытаются переделать темп друг друга под себя.",
    ),
    (
        "compat.static.para2",
        "The pair's strength is {element_relation}. That usually shows up in first contact, chemistry, or how easily you return to dialogue.",
        "Сильная сторона пары — {element_relation}. Это обычно чувствуется в первом контакте, общей химии или в том, как легко снова вернуться в диалог.",
    ),
    (
        "compat.static.para3",
        "The main friction zone is {rhythm_relation}. The clearer you name expectations and decision speed, the less unnecessary tension.",
        "Главная зона трения — {rhythm_relation}. Чем яснее вы проговариваете ожидания и скорость решений, тем меньше ненужного напряжения.",
    ),
    (
        "compat.static.para4",
        "This bond holds best on simple agreements: what matters, where initiative lives, and how you discuss hard things without guessing.",
        "Лучше всего эта связка держится на простых договоренностях: что важно, где нужна инициатива и как вы обсуждаете сложное без угадывания.",
    ),
    (
        "compat.static.para5",
        "To go deeper, the next level is less about signs and more about real dates, profile, and lived contact patterns.",
        "Если хочется понять пару глубже, следующий уровень уже не про знаки, а про реальные даты, профиль и живой сценарий контакта.",
    ),
    (
        "compat.quick.headline.hi",
        "Between you, connection shows up fast and is easier to sustain than for many pairs.",
        "Между вами связь возникает быстро и держится легче, чем у большинства пар.",
    ),
    (
        "compat.quick.headline.mid",
        "Solid potential — this pair opens up better through tuning than on autopilot.",
        "Потенциал хороший, но эта пара раскрывается лучше через настройку, чем сама по себе.",
    ),
    (
        "compat.quick.headline.low",
        "It works if you don't leave contact to chance and agree on what matters early.",
        "Связь рабочая, если вы не пускаете контакт на самотек и заранее договариваетесь о важном.",
    ),
    (
        "compat.quick.headline.min",
        "This pair needs more care, clarity, and patience than instant matching.",
        "Эта пара требует больше бережности, ясности и терпения, чем мгновенного совпадения.",
    ),
    (
        "compat.quick.strongest.hi",
        "What works best here is {element_relation}: it's easier to catch a shared tone and return to contact.",
        "Лучше всего здесь работает {element_relation}: вам проще поймать общий тон и снова вернуться в контакт.",
    ),
    (
        "compat.quick.strongest.mid",
        "The pair's strength is {element_relation}. You can build trust on that if you don't lose clarity in how you talk.",
        "Сильная сторона пары — {element_relation}. На этом можно строить доверие, если не терять ясность в общении.",
    ),
    (
        "compat.quick.strongest.low",
        "The anchor is {element_relation}. That's the foothold for contact without extra pressure.",
        "Опора пары — {element_relation}. Это дает точку, от которой можно выстраивать контакт без лишнего давления.",
    ),
    (
        "compat.quick.strongest.min",
        "Even in a tough mix there's still an anchor — {element_relation}. Lean on that, not on instant matching.",
        "Даже в непростом сочетании остается опора — {element_relation}. На нее и стоит опираться, а не на идею мгновенного совпадения.",
    ),
    (
        "compat.quick.friction.hi",
        "Friction usually starts not in feelings but where «{rhythm_relation}» shows up and you stop checking pace with each other.",
        "Трение обычно начинается не в чувствах, а там, где включается {rhythm_relation} и вы перестаете сверяться по темпу.",
    ),
    (
        "compat.quick.friction.mid",
        "The main risk is {rhythm_relation}. That's where resentment stacks from mismatched expectations.",
        "Главный риск пары — {rhythm_relation}. Именно здесь проще всего накопить обиду из-за разных ожиданий.",
    ),
    (
        "compat.quick.friction.low",
        "The weak spot is {rhythm_relation}. Without spoken rules it turns into push-pull fast.",
        "Слабое место этой связи — {rhythm_relation}. Без проговоренных правил это быстро превращается в качели.",
    ),
    (
        "compat.quick.friction.min",
        "Main tension comes from {rhythm_relation}. If you ignore it, the bond tips into stubbornness or withdrawal.",
        "Главное напряжение здесь дает {rhythm_relation}. Если это не замечать, связь быстрее уходит в упрямство или отстранение.",
    ),
    (
        "compat.quick.next.hi",
        "Don't rely only on ease. Agree early how you hold contact on ordinary daily topics.",
        "Не полагайтесь только на легкость. Лучше сразу договориться, как вы держите контакт в обычных бытовых темах.",
    ),
    (
        "compat.quick.next.mid",
        "Next step: clarify expectations and pace — who ramps in faster, who needs more time, and how you talk about tension.",
        "Следующий шаг здесь — прояснить ожидания и темп: кто быстрее включается, кому нужно больше времени и как вы обсуждаете напряжение.",
    ),
    (
        "compat.quick.next.low",
        "Name boundaries and how you discuss hard topics. That makes this pairing steadier.",
        "Лучше заранее обозначить границы и способ разговора о сложном. Именно это делает такую пару устойчивее.",
    ),
    (
        "compat.quick.next.min",
        "Don't force closeness. First understand how you each enter contact and how not to hurt each other with that gap.",
        "Не форсируйте сближение. Сначала полезнее понять, где вы по-разному входите в контакт и как не ранить друг друга этой разницей.",
    ),
    ("compat.quick.strength_extra", "Direct talk without extra guessing helps this bond.", "Этой связи помогает прямой разговор без лишних догадок."),
    ("compat.quick.caution_extra", "Don't wait for alignment to appear by itself if pace and expectations stay unnamed.", "Не стоит ждать, что совпадение случится само, если темп и ожидания не названы вслух."),
    # Pair dynamics JSON (LLM input)
    ("compat.dynamics.tendency.cardinal", "more likely to initiate contact and steer turning points", "скорее инициирует контакт и задаёт повороты"),
    ("compat.dynamics.tendency.fixed", "more likely to hold pace and boundaries, slower to change", "скорее держит темп и границы, медленнее меняется"),
    ("compat.dynamics.tendency.mutable", "more likely to adapt and redirect the conversation", "скорее подстраивается и переводит разговор"),
    ("compat.dynamics.tendency.default", "enters contact differently in different phases", "входит в контакт по-разному в разные фазы"),
    ("compat.dynamics.emotional.diff", "different depth and speed of closing off emotionally", "разная глубина и скорость закрытия"),
    ("compat.dynamics.emotional.same", "similar emotional tempo, different ways of protecting", "похожий эмоциональный темп, разный способ защиты"),
    ("compat.label.you", "You", "Ты"),
    ("compat.label.partner", "Partner", "Партнёр"),
    ("compat.llm.feedback", "{block}: user marked «{val}»", "{block}: пользователь отметил «{val}»"),
    # Modality role lines (you / partner)
    ("compat.role.you.cardinal.1", "you move into contact faster and set the pace of getting closer", "быстрее идёшь в контакт и задаёшь темп сближения"),
    ("compat.role.you.cardinal.2", "you want clarity and an answer sooner", "хочешь ясности и ответа поскорее"),
    ("compat.role.you.fixed.1", "you hold your line and dislike being yanked around", "держишь свою линию и не любишь, когда тебя дёргают"),
    ("compat.role.you.fixed.2", "you cling to stability more once you're already in contact", "сильнее цепляешься за стабильность, когда уже вошёл в контакт"),
    ("compat.role.you.mutable.1", "you adapt flexibly but may drift into what's unsaid", "гибко подстраиваешься, но можешь «уплыть» в недосказанность"),
    ("compat.role.you.mutable.2", "you often seek compromise instead of head-on collision", "часто ищешь компромисс вместо прямого столкновения"),
    ("compat.role.you.default.1", "you enter contact differently depending on the phase", "по-разному включаешься в контакт в зависимости от фазы"),
    ("compat.role.partner.cardinal.1", "often leads the conversation and initiates turns", "часто ведёт разговор и инициирует повороты"),
    ("compat.role.partner.cardinal.2", "may read a pause as losing interest", "может воспринимать паузу как потерю интереса"),
    ("compat.role.partner.fixed.1", "holds distance and controls the pace of closeness", "держит дистанцию и контролирует темп сближения"),
    ("compat.role.partner.fixed.2", "opens slower than you sometimes want", "открывается медленнее, чем тебе иногда хочется"),
    ("compat.role.partner.mutable.1", "smooths and redirects when it heats up", "сглаживает и переводит тему, когда становится жарко"),
    ("compat.role.partner.mutable.2", "may retreat into generalities instead of a clear yes/no", "может уходить в общие фразы вместо чёткого «да/нет»"),
    ("compat.role.partner.default.1", "enters contact their own way — not always matching your expectation", "по-своему входит в контакт — это не всегда совпадает с твоим ожиданием"),
    # Sexuality intensity labels
    ("compat.sexintensity.deep", "very high — feelings and physicality run deep", "очень высокий — чувства и телесность включаются глубоко"),
    ("compat.sexintensity.strong", "strong — closeness and proof of importance through touch matter", "сильный — хочется близости и подтверждения значимости через контакт"),
    ("compat.sexintensity.fast", "strong — you're pulled together physically fast", "сильный — вас быстро тянет друг к другу физически"),
    ("compat.sexintensity.good", "solid — attraction exists if daily tension doesn't smother it", "хороший — притяжение есть, если не гасить его бытовым напряжением"),
    ("compat.sexintensity.low", "not the main engine — it needs deliberate upkeep", "не главный двигатель пары — его нужно сознательно поддерживать"),
    # Block: emotions
    ("compat.block.emotions.title", "Emotional fit", "Эмоциональная совместимость"),
    ("compat.block.emotions.subtitle", "Who goes deeper, who shuts down, who pulls for closeness", "Кто глубже, кто закрывается, кто тянет близость"),
    ("compat.block.emotions.take.diff", "One of you feels emotions longer and deeper; the other moves toward rationality or distance faster.", "Один из вас проживает эмоции глубже и дольше, второй быстрее уходит в рациональность или дистанцию."),
    ("compat.block.emotions.take.same", "You read each other's emotional backdrop faster — the risk is both stewing, then flipping into «hard mode» together.", "Вы быстрее узнаёте эмоциональный фон друг друга — риск в том, что оба копите, а потом включаете «жёсткий режим» одновременно."),
    ("compat.block.emotions.detail.diff", "Against «{element_relation}» one may feel a missing response; the other may feel pressure or emotional control.", "На фоне «{element_relation}» один может чувствовать нехватку ответа, другой — давление или контроль со стороны чувств."),
    ("compat.block.emotions.detail.same", "Similar element helps read mood, but fights often aren't about facts — they're about «how important this is right now».", "Похожая стихия помогает узнавать настроение, но спор часто не о фактах, а о том, «насколько это сейчас важно»."),
    ("compat.block.emotions.risk", "If needs aren't named sooner, the slower side starts «reading silence» and misreads.", "Если быстрее не называть потребности, медленнее начинает «читать молчание» и ошибаться."),
    ("compat.block.emotions.action", "Agree one signal for «I need a pause» and how you return to the conversation.", "Договоритесь о одном сигнале «мне нужна пауза» и о том, как вы возвращаетесь к разговору."),
    # Block: communication
    ("compat.block.communication.title", "Communication", "Коммуникация"),
    ("compat.block.communication.subtitle", "Directness, avoidance, what's left unsaid", "Прямота, избегание, недосказанность"),
    ("compat.block.communication.take.diff", "You don't always match on style: one wants straight words; the other wants time and soft framing.", "Вы не всегда совпадаете по способу общения: одному нужна прямая формулировка, другому — время и мягкая поддача."),
    ("compat.block.communication.take.same", "You may speak «the same language» but dodge uncomfortable topics until it's late.", "Вы можете говорить «на одном языке», но избегать неудобных тем, пока не станет слишком поздно."),
    ("compat.block.communication.detail", "The rhythm backdrop is «{rhythm_relation}» — talks cut off mid-sentence or jump topics without decisions.", "Фон ритма — «{rhythm_relation}»: из-за него разговоры то обрываются на полуслове, то превращаются в переключение тем без решения."),
    ("compat.block.communication.risk", "What's unsaid turns into tests, hints, and «you should have known» resentment.", "Недосказанность превращается в проверки, намёки и обиды «ты должен был понять»."),
    ("compat.block.communication.action", "One concrete question instead of a monologue — and time to answer without interrogation.", "Один конкретный вопрос вместо монолога — и время на ответ без допроса."),
    # Block: conflicts
    ("compat.block.conflicts.title", "Conflict", "Конфликты"),
    ("compat.block.conflicts.subtitle", "Who escalates, who shuts down, how to close the loop", "Кто разгоняет, кто замыкается, как замкнуть цикл"),
    ("compat.block.conflicts.take", "Conflict often runs on reaction, not topic: one ramps tension; the other withdraws or closes.", "Конфликт часто разгоняется не темой, а реакцией: один усиливает напряжение, второй уходит или закрывается."),
    ("compat.block.conflicts.detail", "A typical loop is pressure → distance → more pressure, especially with «{rhythm_relation}» in the pair.", "Типичный цикл здесь легко описать как «давление → дистанция → ещё больше давления», особенно когда в паре «{rhythm_relation}»."),
    ("compat.block.conflicts.action", "A stop phrase for raised voices and a 15-minute slot «without armor» to unpack.", "Стоп-фраза на повышение тона и отдельный слот «15 минут без защиты» для разбора."),
    # Block: sexuality
    ("compat.block.sexuality.title", "Sexual dynamic", "Сексуальная динамика"),
    ("compat.block.sexuality.subtitle", "Pull, initiative, control, tension", "Притяжение, инициатива, контроль, напряжение"),
    ("compat.block.sexuality.take", "Physical pull here is {sex_intensity}.", "Уровень физического притяжения здесь — {sex_intensity}."),
    ("compat.block.sexuality.detail.mid", "{initiator} {control_line} Closeness can be intense yet unpredictable on safety — especially if one needs proof of worth and the other needs control.", "{initiator} {control_line} Из-за этого близость может быть интенсивной и при этом непредсказуемой по безопасности — особенно если одному нужна проверка значимости, а другому — ощущение контроля."),
    ("compat.block.sexuality.risk", "Sex doesn't erase what's unsaid at home — it muffles it, then it returns louder.", "Секс не закрывает недосказанность в быту — он временно заглушает, потом возвращается сильнее."),
    ("compat.block.sexuality.action", "Say what closeness means for each of you and where pressure becomes a red flag.", "Отдельно проговорить «что близость значит для каждого» и где для кого красные флаги давления."),
    ("compat.block.sexuality.initiator.diff", "The «first step» toward closeness often belongs to whoever moves faster into contact — not the same as vulnerability readiness.", "Чаще «первым шагом» в близость владеет тот, кто быстрее берёт инициативу в контакте — но это не значит готовность к уязвимости."),
    ("compat.block.sexuality.initiator.same", "Initiative can be shared — both wait for a signal and both fear seeming clingy.", "Инициатива может быть общей — оба ждут сигнала и оба боятся показаться навязчивыми."),
    ("compat.block.sexuality.control.fixed", "Control often hides as «the right pace» or coolness — especially if one sign holds the boundary harder.", "Контроль часто маскируется под «правильный темп» или холодность — особенно если один из знаков упрямее держит границу."),
    ("compat.block.sexuality.control.other", "Control can show up as minimizing or postponing the important talk.", "Контроль может проявляться через обесценивание или откладывание разговора о важном."),
    # Block: long_term
    ("compat.block.long_term.title", "Long-term", "Долгосрочность"),
    ("compat.block.long_term.subtitle", "Foundation, goals, fatigue over time", "База, цели, усталость со временем"),
    ("compat.block.long_term.take.low", "Over time the bond can ride on pull and shared meaning — but without agreements it turns tiring.", "На дистанции связь может держаться на притяжении и общих смыслах — но без договорённостей начнёт вызывать усталость."),
    ("compat.block.long_term.take.high", "There's a base for the long haul if you don't swap patience for avoiding hard topics.", "Есть база для долгой связи, если вы не используете терпение как замену прямым темам."),
    ("compat.block.long_term.detail", "Right now the foothold is «{strongest}». Long-run risk is enduring what should be spoken before resentment stacks.", "Сейчас опора — «{strongest}». Риск долгосрока — привычка терпеть то, что нужно проговаривать до накопления обиды."),
    ("compat.block.long_term.risk", "If you only match on intensity, not agreements — the bond burns out.", "Если совпадаете только в интенсивности, но не в договорённостях — связь выжигает."),
    ("compat.block.long_term.action", "One shared 3-month horizon: not a slogan — practical and emotional ground rules.", "Один совместный горизонт на 3 месяца: не романтический лозунг, а бытовые и эмоциональные правила."),
    # Scenarios
    ("compat.scenario.closer.title", "If you want to get closer", "Если хочешь сблизиться"),
    ("compat.scenario.closer.b1", "Don't push pace — offer a small step and a specific time.", "Не дави на темп — предложи маленький шаг и конкретное время."),
    ("compat.scenario.closer.b2", "Leave room without a «who wins the silence» game.", "Оставляй пространство без игры в «кто круче держит паузу»."),
    ("compat.scenario.closer.b3", "Once say out loud what closeness means to you — without blame.", "Один раз скажи вслух, что для тебя значит близость — без обвинений."),
    ("compat.scenario.clarity.title", "If you want clarity", "Если хочешь ясности"),
    ("compat.scenario.clarity.b1", "Ask one direct question and don't stretch ambiguity into «later».", "Задай один прямой вопрос и не растягивай неопределённость «на потом»."),
    ("compat.scenario.clarity.b2", "Write agreements in plain language: «we do this / we don't do this».", "Фиксируй договорённости простым языком: «мы это или мы это не делаем»."),
    ("compat.scenario.clarity.b3", "Don't mix clarity with ultimatum — tone makes the difference.", "Не смешивай ясность с ультиматумом — разница в тоне решает."),
    ("compat.scenario.exit.title", "If you want to leave or lower involvement", "Если хочешь выйти или снизить вовлечённость"),
    ("compat.scenario.exit.b1", "Watch actions and patterns, not chat explanations.", "Смотри на действия и паттерн, не на объяснения в переписке."),
    ("compat.scenario.exit.b2", "Don't keep contact to prove you're «good enough».", "Не держи контакт ради проверки «достаточно ли я хорош(а)»."),
    ("compat.scenario.exit.b3", "If it pulls after a breakup — list three concrete pain repeats and check what changed.", "Если тянет после расставания — выпиши три конкретных повтора боли и проверь, что изменилось."),
    ("compat.scenario.insert.just_met", "At the start curiosity beats fast «forever» conclusions.", "На старте полезнее любопытство, чем быстрые выводы о «навсегда»."),
    ("compat.scenario.insert.conflict", "Lower escalation first — then the meaning of the fight.", "Сначала снизьте эскалацию — потом уже смысл спора."),
]


def main() -> None:
    patch_en: dict[str, str] = {}
    patch_ru: dict[str, str] = {}
    for key, en, ru in ROWS:
        patch_en[key] = en
        patch_ru[key] = ru

    def merge(locale: str, patch: dict[str, str]) -> None:
        path = I18N / f"app.{locale}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        overlap = set(data) & set(patch)
        if overlap:
            raise SystemExit(f"Keys already exist ({locale}): {sorted(overlap)[:20]}…")
        data.update(patch)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    merge("en", patch_en)
    merge("ru", patch_ru)
    print(f"Merged {len(patch_en)} compat keys into app.en.json and app.ru.json")


if __name__ == "__main__":
    main()
