# Life spheres quality pack run 20260721T145313Z

projection_version: `life_spheres_projector_v0.1`
cases_pass: 1/8
comparisons_pass: 2/2
total_defects: 23

## lsq-01 — Sun Leo · Venus Cancer · Moon Cancer — soft closeness — FAIL
intent: Same Sun as lsq-02; Venus/Moon differ → love must diverge
fingerprint: `sha256:6c02934be2e5d5024306deea2238aef1ccd6afabcd3d8b4b24f0037fc542bcca`
### love — fail
style_class: pace · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Cancer задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужен свой темп — в духе «Близость через тёплые слова, предсказуе…».
- ✓ **risk**: Слишком быстрый заход в близость или замирание при чужом ритме.
- ✓ **turns_on**: Ритм, в котором можно быть без спектакля.
- ✓ **turns_off**: Резкие требования и хаотичная доступность.
- ✓ **helps**: Назови одну границу темпа до следующего глубокого разговора.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — fail
style_class: security · depth: sign_only
rules: rule:money.how.planet, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✗ **how**: В деньгах: Юпитер в знаке Cancer задаёт тон проявления в этой сфере.
  - `RULESET` money.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В деньгах нужно ощущение безопасности под ресурсом — в духе «Деньги как спокойная безопасность: малы…».
- ✓ **risk**: Траты от тревоги или отказ от любого движения.
- ✓ **turns_on**: Видимый запас и честные пределы.
- ✓ **turns_off**: Сравнение с другими и внезапные дыры в плане.
- ✓ **helps**: Назови одну цифру безопасности и держи её неделю.
UI: FE may prefix «В реализации» for money how
### decisions — fail
style_class: analysis · depth: sign_only
rules: rule:decisions.how.planet, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✗ **how**: В решениях: Сатурн в знаке Capricorn задаёт тон проявления в этой сфере.
  - `RULESET` decisions.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В решениях нужен достаточный разбор без зависания — в духе «Решения через согласование с близкими,…».
- ✓ **risk**: Переанализ мимо полезного окна.
- ✓ **turns_on**: Короткая проверка фактов и затем выбор.
- ✓ **turns_off**: Новые данные без слота на решение.
- ✓ **helps**: Ограничь исследование одним заходом; в конце — решение.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-02 — Sun Leo · Venus Aries · Moon Aquarius — autonomy pace — FAIL
intent: Pair with lsq-01: love/money/decisions must not collapse to same Leo sun filler
fingerprint: `sha256:192686dec4d74763a3965a8a6e4c078da5dc485506a8d59964b01de12b17dd2d`
### love — fail
style_class: clarity · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Aries задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через прямые слова, быстрый те…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — fail
style_class: growth · depth: sign_only
rules: rule:money.how.planet, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✗ **how**: В деньгах: Юпитер в знаке Sagittarius задаёт тон проявления в этой сфере.
  - `RULESET` money.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В деньгах нужен шаг роста без импульса — в духе «Деньги как рост: один смелый шаг с пото…».
- ✓ **risk**: Перерастяжение или полный застой без следующего хода.
- ✓ **turns_on**: Малое измеримое расширение.
- ✓ **turns_off**: Ставки «всё или ничего».
- ✗ **helps**: Одно действие роста с потолком — затем разбор.
  - `RULESET` money.helps lacks actionable support
UI: FE may prefix «В реализации» for money how
### decisions — fail
style_class: speed · depth: sign_only
rules: rule:decisions.how.planet, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✗ **how**: В решениях: Сатурн в знаке Capricorn задаёт тон проявления в этой сфере.
  - `RULESET` decisions.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В решениях нужен быстрый честный выбор — в духе «Решения быстро и честно: ясное да/нет и…».
- ✓ **risk**: Скорость без точки пересмотра.
- ✗ **turns_on**: Ясное да/нет с датой проверки.
  - `RULESET` decisions.turns_on: interchangeable for most users (weak personal binding)
- ✓ **turns_off**: Чужая навязанная срочность.
- ✓ **helps**: Реши один раз; поставь один пересмотр, не десять.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-03 — Fixed natal · clarity/structure styles — FAIL
intent: Same natal as lsq-04; only styles change → style lens must drive need/risk/on/off/helps
fingerprint: `sha256:95b3b0a1262f4e7db71959e924cbc3d1de4066edfbd9cb956ae9e9a9ea605563`
### love — fail
style_class: clarity · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Aquarius задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через честный разговор и ясные…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — fail
style_class: structure · depth: sign_only
rules: rule:money.how.planet, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✗ **how**: В деньгах: Юпитер в знаке Taurus задаёт тон проявления в этой сфере.
  - `RULESET` money.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В деньгах нужны простые правила ценности — в духе «Деньги через структуру: учёт, правила ц…».
- ✓ **risk**: Хаос в учёте или зажим контроля до остановки действий.
- ✓ **turns_on**: Понятные цифры и маленькие регулярные шаги.
- ✓ **turns_off**: Стыд за запросы и туман во взаиморасчётах.
- ✓ **helps**: Один денежный фокус на неделю и запись «что сработало».
UI: FE may prefix «В реализации» for money how
### decisions — fail
style_class: analysis · depth: sign_only
rules: rule:decisions.how.planet, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✗ **how**: В решениях: Сатурн в знаке Sagittarius задаёт тон проявления в этой сфере.
  - `RULESET` decisions.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В решениях нужен достаточный разбор без зависания — в духе «Решения через один критерий, короткий д…».
- ✓ **risk**: Переанализ мимо полезного окна.
- ✓ **turns_on**: Короткая проверка фактов и затем выбор.
- ✓ **turns_off**: Новые данные без слота на решение.
- ✓ **helps**: Ограничь исследование одним заходом; в конце — решение.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-04 — Fixed natal · depth/security/analysis styles — FAIL
intent: Pair with lsq-03: prove style sensitivity without natal drift
fingerprint: `sha256:fdadd21a9fd038d89121bc531bf3dbba6af078cd5b71cc04d98430f54a1380ac`
### love — fail
style_class: pace · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Aquarius задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужен свой темп — в духе «Близость через глубину смысла и медленн…».
- ✓ **risk**: Слишком быстрый заход в близость или замирание при чужом ритме.
- ✓ **turns_on**: Ритм, в котором можно быть без спектакля.
- ✓ **turns_off**: Резкие требования и хаотичная доступность.
- ✓ **helps**: Назови одну границу темпа до следующего глубокого разговора.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — fail
style_class: security · depth: sign_only
rules: rule:money.how.planet, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✗ **how**: В деньгах: Юпитер в знаке Taurus задаёт тон проявления в этой сфере.
  - `RULESET` money.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В деньгах нужно ощущение безопасности под ресурсом — в духе «Деньги как чувство безопасности: видимы…».
- ✓ **risk**: Траты от тревоги или отказ от любого движения.
- ✗ **turns_on**: Видимый запас и честные пределы.
  - `RULESET` money.turns_on: interchangeable for most users (weak personal binding)
- ✓ **turns_off**: Сравнение с другими и внезапные дыры в плане.
- ✓ **helps**: Назови одну цифру безопасности и держи её неделю.
UI: FE may prefix «В реализации» for money how
### decisions — fail
style_class: analysis · depth: sign_only
rules: rule:decisions.how.planet, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✗ **how**: В решениях: Сатурн в знаке Sagittarius задаёт тон проявления в этой сфере.
  - `RULESET` decisions.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В решениях нужен достаточный разбор без зависания — в духе «Решения через короткий анализ фактов бе…».
- ✓ **risk**: Переанализ мимо полезного окна.
- ✓ **turns_on**: Короткая проверка фактов и затем выбор.
- ✓ **turns_off**: Новые данные без слота на решение.
- ✓ **helps**: Ограничь исследование одним заходом; в конце — решение.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-05 — Full houses enrich how (time known) — PASS
intent: House fragments must appear in evidence and how; no house claims without text
fingerprint: `sha256:1f3e331ea1b28541a98e401f5cb4e5128868d80e74d5d820f3243434b4cac9ee`
### love — pass
style_class: clarity · depth: houses_plus_styles
rules: rule:love.how.planet, rule:love.how.house7, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✓ **how**: В любви: Венера в знаке Aquarius задаёт тон проявления в этой сфере. В партнёрском поле: Партнёрство строится на равном разговоре и совпадении темпа.
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через прямые слова и равный те…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass
style_class: exchange · depth: houses_plus_styles
rules: rule:money.how.planet, rule:money.how.house2, rule:money.how.house8, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✓ **how**: В деньгах: Юпитер в знаке Libra задаёт тон проявления в этой сфере. Ресурс растёт, когда вклад и цена названы без тумана. Общие обязательства требуют ясных границ обмена.
- ✓ **need**: В деньгах нужен честный обмен ценности — в духе «Деньги как честный обмен ценности: проз…».
- ✓ **risk**: Отдавать больше, чем готовы, или обесценивать свой вклад.
- ✓ **turns_on**: Прозрачные договорённости о цене и вкладе.
- ✓ **turns_off**: Размытые «потом рассчитаемся».
- ✓ **helps**: Одна ясная договорённость о цене до следующего обмена.
UI: FE may prefix «В реализации» for money how
### decisions — pass
style_class: consensus · depth: houses_plus_styles
rules: rule:decisions.how.planet, rule:decisions.how.house9, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✓ **how**: В решениях: Сатурн в знаке Aquarius задаёт тон проявления в этой сфере. В поле выбора: Выбор держится на смысле и праве сказать своё решение вслух.
- ✓ **need**: В решениях нужно согласование без растворения — в духе «Решения вместе собрать два мнения, зате…».
- ✓ **risk**: Ждать всех и потерять свой критерий.
- ✓ **turns_on**: Короткий круг мнений и свой финальный ход.
- ✓ **turns_off**: Бесконечные совещания без владельца решения.
- ✓ **helps**: Собери два мнения, назови своё решение и следующий шаг.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-06 — Sign-only · no houses — honesty — FAIL
intent: Must not mention houses/ASC; still emit useful sign_plus_styles map
fingerprint: `sha256:38d132627a4a76427e4d3c4a8857aca684e8717c2c435f9373533187ee114946`
### love — fail
style_class: clarity · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Libra задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через предсказуемый ритм конта…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — fail
style_class: structure · depth: sign_only
rules: rule:money.how.planet, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✗ **how**: В деньгах: Юпитер в знаке Sagittarius задаёт тон проявления в этой сфере.
  - `RULESET` money.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В деньгах нужны простые правила ценности — в духе «Деньги через устойчивый порядок: регуля…».
- ✓ **risk**: Хаос в учёте или зажим контроля до остановки действий.
- ✓ **turns_on**: Понятные цифры и маленькие регулярные шаги.
- ✓ **turns_off**: Стыд за запросы и туман во взаиморасчётах.
- ✓ **helps**: Один денежный фокус на неделю и запись «что сработало».
UI: FE may prefix «В реализации» for money how
### decisions — fail
style_class: structure · depth: sign_only
rules: rule:decisions.how.planet, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✗ **how**: В решениях: Сатурн в знаке Pisces задаёт тон проявления в этой сфере.
  - `RULESET` decisions.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В решениях нужна ясная рамка — в духе «Решения через структуру: критерии снача…».
- ✓ **risk**: Бесконечные варианты без закрытия.
- ✓ **turns_on**: Один критерий и короткий дедлайн.
- ✓ **turns_off**: Открытые вкладки непринятых выборов.
- ✓ **helps**: Запиши три критерия, выбери ход, поставь таймбокс.
UI: FE maps fields 1:1 when contract present; partial map OK

## lsq-07 — Only relationship_style present — FAIL
intent: Partial map: love may emit; money/decisions omit — not invent from identity
fingerprint: `sha256:2acb59b88ab1812952314ef8cd6c3d8b14315b973cf3ef7d8d7aa11e81221979`
### love — fail
style_class: clarity · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Taurus задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужна ясность и предсказуемый контакт — в духе «Близость через тёплую поддержку и право…».
- ✓ **risk**: Точка слома — ожидание, что другой угадает без слов.
- ✓ **turns_on**: Спокойный прямой разговор и совпадение по темпу близости.
- ✓ **turns_off**: Намёки, двойные сигналы и давление без следующего шага.
- ✓ **helps**: Одна короткая честная договорённость на неделю — не разбор «всего сразу».
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — pass_omit
omitted: style_missing (expected=True)
### decisions — pass_omit
omitted: style_missing (expected=True)

## lsq-08 — Identity slow/care · styles speed/impulse tension — FAIL
intent: Surface coherence risk: ruleset must not invent fake harmony; detect weak coherence
fingerprint: `sha256:8940a9d75f2cd41a9197ede9629d5f0e3be55ffd46d81db73efcf223cad15908`
### love — fail
style_class: pace · depth: sign_only
rules: rule:love.how.planet, rule:love.need.from_style, rule:love.risk.from_style, rule:love.on.from_style, rule:love.off.from_style, rule:love.helps.from_style
- ✗ **how**: В любви: Венера в знаке Leo задаёт тон проявления в этой сфере.
  - `RULESET` love.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В любви нужен свой темп — в духе «Близость через быстрый темп, сразу к де…».
- ✓ **risk**: Слишком быстрый заход в близость или замирание при чужом ритме.
- ✓ **turns_on**: Ритм, в котором можно быть без спектакля.
- ✓ **turns_off**: Резкие требования и хаотичная доступность.
- ✓ **helps**: Назови одну границу темпа до следующего глубокого разговора.
UI: FE withLifeSphereHowFrame may prefix «В отношениях» (PROJECTION chrome, not claim invent)
### money — fail
style_class: growth · depth: sign_only
rules: rule:money.how.planet, rule:money.need.from_style, rule:money.risk.from_style, rule:money.on.from_style, rule:money.off.from_style, rule:money.helps.from_style
- ✗ **how**: В деньгах: Юпитер в знаке Aries задаёт тон проявления в этой сфере.
  - `RULESET` money.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В деньгах нужен шаг роста без импульса — в духе «Деньги через смелый рост и готовность р…».
- ✓ **risk**: Перерастяжение или полный застой без следующего хода.
- ✓ **turns_on**: Малое измеримое расширение.
- ✓ **turns_off**: Ставки «всё или ничего».
- ✗ **helps**: Одно действие роста с потолком — затем разбор.
  - `RULESET` money.helps lacks actionable support
UI: FE may prefix «В реализации» for money how
### decisions — fail
style_class: analysis · depth: sign_only
rules: rule:decisions.how.planet, rule:decisions.need.from_style, rule:decisions.risk.from_style, rule:decisions.on.from_style, rule:decisions.off.from_style, rule:decisions.helps.from_style
- ✗ **how**: В решениях: Сатурн в знаке Sagittarius задаёт тон проявления в этой сфере.
  - `RULESET` decisions.how uses planet-in-sign boilerplate without trait content (only sign label changes — weak personal binding)
- ✓ **need**: В решениях нужен достаточный разбор без зависания — в духе «Решения сразу: скорость важнее долгого…».
- ✓ **risk**: Переанализ мимо полезного окна.
- ✓ **turns_on**: Короткая проверка фактов и затем выбор.
- ✓ **turns_off**: Новые данные без слота на решение.
- ✓ **helps**: Ограничь исследование одним заходом; в конце — решение.
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
    "how_jaccard": 0.8,
    "need_jaccard": 0.312
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
    "how_jaccard": 0.8,
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
    "need_jaccard": 0.222
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
      "risk": false,
      "turns_on": false,
      "turns_off": false,
      "helps": false
    },
    "any_differ": true,
    "how_jaccard": 1.0,
    "need_jaccard": 0.714
  }
}

