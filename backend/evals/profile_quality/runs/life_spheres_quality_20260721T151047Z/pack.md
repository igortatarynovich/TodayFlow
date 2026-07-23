# Life spheres quality pack run 20260721T151047Z

projection_version: `life_spheres_projector_v0.2`
cases_pass: 8/8
comparisons_pass: 2/2
total_defects: 0

## lsq-01 — Sun Leo · Venus Cancer · Moon Cancer — soft closeness — PASS
intent: Same Sun as lsq-02; Venus/Moon differ → love must diverge
fingerprint: `sha256:93cb2f24a2cbe6ed5f470597279feb1c4723aea506cde9f3256727d23db45b58`
### love — pass
style_class: care · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости ты быстрее раскрываешься там, где есть эмоциональная безопасность, знакомый ритм и заметная забота в мелочах.
- ✓ **need**: В любви нужна тёплая опора без растворения — в духе «Близость через тёплые слова, предсказуе…».
- ✓ **risk**: Забота ценой своих границ.
- ✓ **turns_on**: Взаимная поддержка и мягкая устойчивость.
- ✓ **turns_off**: Обесценивание чувств и холодная отстранённость.
- ✓ **helps**: Один жест заботы о себе и один — о контакте, в один день.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: security · depth: sign_only
rules: rule:money.how.trait, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах тебе спокойнее, когда рост опирается на чувство «есть запас на близких и на себя».
- ✓ **need**: В деньгах нужно ощущение безопасности под ресурсом — в духе «Деньги как спокойная безопасность: малы…».
- ✓ **risk**: Траты от тревоги или отказ от любого движения.
- ✓ **turns_on**: Видимый запас и честные пределы.
- ✓ **turns_off**: Сравнение с другими и внезапные дыры в плане.
- ✓ **helps**: Назови одну цифру безопасности и держи её неделю.
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: structure · depth: sign_only
rules: rule:decisions.how.trait, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях твоя сила — превратить выбор в график: критерий, срок, ответственный — ты.
- ✓ **need**: В решениях нужна ясная рамка — в духе «Решения через согласование с близкими,…».
- ✓ **risk**: Бесконечные варианты без закрытия.
- ✓ **turns_on**: Один критерий и короткий дедлайн.
- ✓ **turns_off**: Открытые вкладки непринятых выборов.
- ✓ **helps**: Запиши три критерия, выбери ход, поставь таймбокс.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-02 — Sun Leo · Venus Aries · Moon Aquarius — autonomy pace — PASS
intent: Pair with lsq-01: love/money/decisions must not collapse to same Leo sun filler
fingerprint: `sha256:755e912111ce59c45c765d25cfdc26544152dd19ed93fc666f6c5a590bffbd1d`
### love — pass
style_class: autonomy · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости ты быстрее зажигаешься, когда есть прямая инициатива и честный телесный интерес без долгих намёков.
- ✓ **need**: В любви нужно пространство для себя внутри близости — в духе «Близость через прямые слова, быстрый те…».
- ✓ **risk**: Слияние до раздражения или уход без слов.
- ✓ **turns_on**: Уважение к личному воздуху при устойчивом контакте.
- ✓ **turns_off**: Контроль, проверки и отсутствие своей зоны.
- ✓ **helps**: Оставь один личный слот неприкосновенным, оставаясь на связи.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: growth · depth: sign_only
rules: rule:money.how.trait, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах горизонт расширяется через обучение и дальний ход — без якоря цифр энтузиазм разлетается.
- ✓ **need**: В деньгах нужен шаг роста без импульса — в духе «Деньги как рост: один смелый шаг с пото…».
- ✓ **risk**: Перерастяжение или полный застой без следующего хода.
- ✓ **turns_on**: Малое измеримое расширение.
- ✓ **turns_off**: Ставки «всё или ничего».
- ✓ **helps**: Один шаг роста с потолком — затем короткий разбор.
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: speed · depth: sign_only
rules: rule:decisions.how.trait, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях твоя сила — превратить выбор в график: критерий, срок, ответственный — ты.
- ✓ **need**: В решениях нужен быстрый честный выбор — в духе «Решения быстро и честно: ясное да/нет и…».
- ✓ **risk**: Скорость без точки пересмотра.
- ✓ **turns_on**: Ясное да/нет с датой проверки.
- ✓ **turns_off**: Чужая навязанная срочность.
- ✓ **helps**: Реши один раз; поставь один пересмотр, не десять.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-03 — Fixed natal · clarity/structure styles — PASS
intent: Same natal as lsq-04; only styles change → style lens must drive need/risk/on/off/helps
fingerprint: `sha256:9efce2fa7ea9e2239df45be008e9b94cf40cf8494548495b8b1143d4319248bf`
### love — pass
style_class: clarity · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости тебе нужен воздух дружбы внутри пары: уважение к странности, личный контур и контакт без собственничества.
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через честный разговор и ясные…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: structure · depth: sign_only
rules: rule:money.how.trait, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах тебе легче наращивать ценность медленными регулярными вложениями, чем одним резким рывком.
- ✓ **need**: В деньгах нужны простые правила ценности — в духе «Деньги через структуру: учёт, правила ц…».
- ✓ **risk**: Хаос в учёте или зажим контроля до остановки действий.
- ✓ **turns_on**: Понятные цифры и маленькие регулярные шаги.
- ✓ **turns_off**: Стыд за запросы и туман во взаиморасчётах.
- ✓ **helps**: Один денежный фокус на неделю и запись «что сработало».
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: structure · depth: sign_only
rules: rule:decisions.how.trait, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях горизонт важен, но без даты хода он остаётся мечтой — поставь срок первому шагу.
- ✓ **need**: В решениях нужна ясная рамка — в духе «Решения через один критерий, короткий д…».
- ✓ **risk**: Бесконечные варианты без закрытия.
- ✓ **turns_on**: Один критерий и короткий дедлайн.
- ✓ **turns_off**: Открытые вкладки непринятых выборов.
- ✓ **helps**: Запиши три критерия, выбери ход, поставь таймбокс.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-04 — Fixed natal · depth/security/analysis styles — PASS
intent: Pair with lsq-03: prove style sensitivity without natal drift
fingerprint: `sha256:8ded89baf86129c496e58aa6d9e16557c57ddd95cd5d7a18ba73e4eb453a9497`
### love — pass
style_class: pace · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости тебе нужен воздух дружбы внутри пары: уважение к странности, личный контур и контакт без собственничества.
- ✓ **need**: В любви нужен свой темп — в духе «Близость через глубину смысла и медленн…».
- ✓ **risk**: Слишком быстрый заход в близость или замирание при чужом ритме.
- ✓ **turns_on**: Ритм, в котором можно быть без спектакля.
- ✓ **turns_off**: Резкие требования и хаотичная доступность.
- ✓ **helps**: Назови одну границу темпа до следующего глубокого разговора.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: security · depth: sign_only
rules: rule:money.how.trait, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах тебе легче наращивать ценность медленными регулярными вложениями, чем одним резким рывком.
- ✓ **need**: В деньгах нужно ощущение безопасности под ресурсом — в духе «Деньги как чувство безопасности: видимы…».
- ✓ **risk**: Траты от тревоги или отказ от любого движения.
- ✓ **turns_on**: Видимый запас и честные пределы.
- ✓ **turns_off**: Сравнение с другими и внезапные дыры в плане.
- ✓ **helps**: Назови одну цифру безопасности и держи её неделю.
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: speed · depth: sign_only
rules: rule:decisions.how.trait, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях горизонт важен, но без даты хода он остаётся мечтой — поставь срок первому шагу.
- ✓ **need**: В решениях нужен быстрый честный выбор — в духе «Решения через короткий анализ фактов бе…».
- ✓ **risk**: Скорость без точки пересмотра.
- ✓ **turns_on**: Ясное да/нет с датой проверки.
- ✓ **turns_off**: Чужая навязанная срочность.
- ✓ **helps**: Реши один раз; поставь один пересмотр, не десять.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-05 — Full houses enrich how (time known) — PASS
intent: House fragments must appear in evidence and how; no house claims without text
fingerprint: `sha256:ba6de5634f4fc114be6b8d2cfee26990f96ecf0f43ae3216180c7f4080283316`
### love — pass
style_class: clarity · depth: houses_plus_styles
rules: rule:love.how.trait, rule:love.how.house7, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости тебе нужен воздух дружбы внутри пары: уважение к странности, личный контур и контакт без собственничества. В партнёрском поле: Партнёрство строится на равном разговоре и совпадении темпа.
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через прямые слова и равный те…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: exchange · depth: houses_plus_styles
rules: rule:money.how.trait, rule:money.how.house2, rule:money.how.house8, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах тебе важно, чтобы обмен был взаимным: односторонние «вложения в отношения» размывают ресурс. Ресурс растёт, когда вклад и цена названы без тумана. Общие обязательства требуют ясных границ обмена.
- ✓ **need**: В деньгах нужен честный обмен ценности — в духе «Деньги как честный обмен ценности: проз…».
- ✓ **risk**: Отдавать больше, чем готовы, или обесценивать свой вклад.
- ✓ **turns_on**: Прозрачные договорённости о цене и вкладе.
- ✓ **turns_off**: Размытые «потом рассчитаемся».
- ✓ **helps**: Одна ясная договорённость о цене до следующего обмена.
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: consensus · depth: houses_plus_styles
rules: rule:decisions.how.trait, rule:decisions.how.house9, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях полезно опереться на своё правило, даже если круг ждёт «как принято» — назови своё условие. В поле выбора: Выбор держится на смысле и праве сказать своё решение вслух.
- ✓ **need**: В решениях нужно согласование без растворения — в духе «Решения вместе собрать два мнения, зате…».
- ✓ **risk**: Ждать всех и потерять свой критерий.
- ✓ **turns_on**: Короткий круг мнений и свой финальный ход.
- ✓ **turns_off**: Бесконечные совещания без владельца решения.
- ✓ **helps**: Собери два мнения, назови своё решение и следующий шаг.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-06 — Sign-only · no houses — honesty — PASS
intent: Must not mention houses/ASC; still emit useful sign_plus_styles map
fingerprint: `sha256:d214718de704f8da2e57a318ca09af8ee3cbe22964219dd2f79addfd02c4e5de`
### love — pass
style_class: clarity · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости ты ищешь равный обмен: красивый тон разговора, взаимность шага и ощущение, что тебя не перетягивают.
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через предсказуемый ритм конта…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: structure · depth: sign_only
rules: rule:money.how.trait, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах горизонт расширяется через обучение и дальний ход — без якоря цифр энтузиазм разлетается.
- ✓ **need**: В деньгах нужны простые правила ценности — в духе «Деньги через устойчивый порядок: регуля…».
- ✓ **risk**: Хаос в учёте или зажим контроля до остановки действий.
- ✓ **turns_on**: Понятные цифры и маленькие регулярные шаги.
- ✓ **turns_off**: Стыд за запросы и туман во взаиморасчётах.
- ✓ **helps**: Один денежный фокус на неделю и запись «что сработало».
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: structure · depth: sign_only
rules: rule:decisions.how.trait, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях туман настроения снимается одной внешней опорой: цифра, дата или чужой ясный факт.
- ✓ **need**: В решениях нужна ясная рамка — в духе «Решения через структуру: критерии снача…».
- ✓ **risk**: Бесконечные варианты без закрытия.
- ✓ **turns_on**: Один критерий и короткий дедлайн.
- ✓ **turns_off**: Открытые вкладки непринятых выборов.
- ✓ **helps**: Запиши три критерия, выбери ход, поставь таймбокс.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-07 — Only relationship_style present — PASS
intent: Partial map: love may emit; money/decisions omit — not invent from identity
fingerprint: `sha256:e29f5820e3f52aeac9715d15bd103b4c70da765bf32f8c4129ceff4bc2b9c7d7`
### love — pass
style_class: care · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости ты раскрываешься через устойчивый телесный комфорт, привычный ритм касаний и спокойную предсказуемость.
- ✓ **need**: В любви нужна тёплая опора без растворения — в духе «Близость через тёплую поддержку и право…».
- ✓ **risk**: Забота ценой своих границ.
- ✓ **turns_on**: Взаимная поддержка и мягкая устойчивость.
- ✓ **turns_off**: Обесценивание чувств и холодная отстранённость.
- ✓ **helps**: Один жест заботы о себе и один — о контакте, в один день.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass_omit
omitted: style_missing (expected=True)
### decisions — pass_omit
omitted: style_missing (expected=True)

## lsq-08 — Identity slow/care · styles speed/impulse tension — PASS
intent: Surface coherence risk: ruleset must not invent fake harmony; detect weak coherence
fingerprint: `sha256:82bc4ee4922924835deda065f5704c92daa7186cabe66b5d20aee51c1347064c`
### love — pass
style_class: pace · depth: sign_only
rules: rule:love.how.trait, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В близости тебе важно быть увиденным: тёплый отклик, щедрость внимания и право сиять без стыда за желание.
- ✓ **need**: В любви нужен свой темп — в духе «Близость через быстрый темп, сразу к де…».
- ✓ **risk**: Слишком быстрый заход в близость или замирание при чужом ритме.
- ✓ **turns_on**: Ритм, в котором можно быть без спектакля.
- ✓ **turns_off**: Резкие требования и хаотичная доступность.
- ✓ **helps**: Назови одну границу темпа до следующего глубокого разговора.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: growth · depth: sign_only
rules: rule:money.how.trait, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах рост приходит через смелый первый вклад с потолком — без потолка импульс съедает запас.
- ✓ **need**: В деньгах нужен шаг роста без импульса — в духе «Деньги через смелый рост и готовность р…».
- ✓ **risk**: Перерастяжение или полный застой без следующего хода.
- ✓ **turns_on**: Малое измеримое расширение.
- ✓ **turns_off**: Ставки «всё или ничего».
- ✓ **helps**: Один шаг роста с потолком — затем короткий разбор.
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: speed · depth: sign_only
rules: rule:decisions.how.trait, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях горизонт важен, но без даты хода он остаётся мечтой — поставь срок первому шагу.
- ✓ **need**: В решениях нужен быстрый честный выбор — в духе «Решения сразу: скорость важнее долгого…».
- ✓ **risk**: Скорость без точки пересмотра.
- ✓ **turns_on**: Ясное да/нет с датой проверки.
- ✓ **turns_off**: Чужая навязанная срочность.
- ✓ **helps**: Реши один раз; поставь один пересмотр, не десять.
UI: FE maps fields 1:1 when contract present; partial map OK

## Compare lsq-01 vs lsq-02 — PASS
{
  "love": {
    "comparable": true,
    "fields_differ": {
      "how": true,
      "need": true,
      "risk": true,
      "turns_on": true,
      "turns_off": true,
      "helps": true
    },
    "any_differ": true,
    "how_jaccard": 0.13,
    "need_jaccard": 0.25
  },
  "money": {
    "comparable": true,
    "fields_differ": {
      "how": true,
      "need": true,
      "risk": true,
      "turns_on": true,
      "turns_off": true,
      "helps": true
    },
    "any_differ": true,
    "how_jaccard": 0.045,
    "need_jaccard": 0.19
  },
  "decisions": {
    "comparable": true,
    "fields_differ": {
      "how": false,
      "need": true,
      "risk": true,
      "turns_on": true,
      "turns_off": true,
      "helps": true
    },
    "any_differ": true,
    "how_jaccard": 1.0,
    "need_jaccard": 0.176
  }
}

## Compare lsq-03 vs lsq-04 — PASS
{
  "love": {
    "comparable": true,
    "fields_differ": {
      "how": false,
      "need": true,
      "risk": true,
      "turns_on": true,
      "turns_off": true,
      "helps": true
    },
    "any_differ": true,
    "how_jaccard": 1.0,
    "need_jaccard": 0.235
  },
  "money": {
    "comparable": true,
    "fields_differ": {
      "how": false,
      "need": true,
      "risk": true,
      "turns_on": true,
      "turns_off": true,
      "helps": true
    },
    "any_differ": true,
    "how_jaccard": 1.0,
    "need_jaccard": 0.167
  },
  "decisions": {
    "comparable": true,
    "fields_differ": {
      "how": false,
      "need": true,
      "risk": true,
      "turns_on": true,
      "turns_off": true,
      "helps": true
    },
    "any_differ": true,
    "how_jaccard": 1.0,
    "need_jaccard": 0.312
  }
}

