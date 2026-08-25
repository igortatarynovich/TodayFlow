# Profile Natal Decode Depth v1

**Status:** ACCEPTED — opt-in depth layer (не personality root)  
**Date:** 2026-07-27  
**Parents:** [PROFILE_EXPERIENCE_SCENARIO_V1.md](./PROFILE_EXPERIENCE_SCENARIO_V1.md) · [PROFILE_PRODUCT_SURFACE_CANON.md](./PROFILE_PRODUCT_SURFACE_CANON.md) · [TODAY_DEPTH_LAYER_V1.md](../TODAY_DEPTH_LAYER_V1.md) (аналог паттерна)  
**Code:** `natal_decode_depth_v0.py` · `POST /account/profile/natal-decode` · IL-4 bind: [PROFILE_MEANING_POLISH_V1.md](./PROFILE_MEANING_POLISH_V1.md) (1.3.123)

## Architecture impact

```markdown
## Architecture impact
- **SoT before:** Character Engine = sole personality SoT; natal editorial / interpreter risked parallel «who you are»
- **SoT after:** Natal Decode = **explicit-request depth projection** over fixed CE Identity Core + natal facts.
  Never writes `character_engine_v1`. Never feeds Today/Compat/Tarot as character root.
- **Public contract changed?** yes (additive) — `POST /account/profile/natal-decode` → `natal_decode_depth_v0`
- **Migration required?** no — FE shows CTA; generate only on user action
- **Canon updated?** yes — this doc · Scenario Act II · Surface · Content · CE Architecture Impact
- **Backward compatible?** yes — additive endpoint; core-profile GET unchanged (no auto-decode)
```

## Principle (locked)

1. **CE остаётся единственным SoT личности.** Decode не переопределяет ядро, напряжение, компас.
2. **Только слой глубины** — «как карта объясняет уже известное ядро», не второй портрет.
3. **Один раз по fingerprint** — первый явный `POST` / UI CTA собирает историю; `GET` отдаёт готовый артефакт (`access: ready`, `can_generate: false`). Повторный LLM запрещён, пока не сменится fingerprint (birth/natal/numerology) или ops one-shot. Запрещено: publish профиля, GET `/core-profile`, фоновый job «на всякий случай», кнопка «собрать ещё раз».
4. **Дома в базовом Profile** — короткие **тезисы о человеке** (`how`/`do`), не абзацы и не энциклопедия. Длинная планетарная проза живёт только здесь.
5. **Acceptance строки decode:** убрав имя планеты/дома, фраза всё ещё про **этого** человека и то же Identity Core.
6. **Day hooks** — инструкции **на сейчас** (жест / пауза / проверка), не пересказ характера. Без hooks decode остаётся интересным чтением; с ними — вещью, которую применяют и проверяют.
7. **Честная цена** — хотя бы в одной секции или limits назван риск/ловушка оси (не только дар карты). Лесть без цены ломает доверие к следующему дню.

Связь с CE retention: [PROFILE_EXPERIENCE_SCENARIO_V1](./PROFILE_EXPERIENCE_SCENARIO_V1.md) §3.1.

## Forbidden

- Параллельный personality root / второй logline  
- Запись decode в `character_engine_v1` или overwrite Snapshot portrait  
- Чтение decode Today / Compat / Tarot как character SoT  
- Автогенерация на GET natal-chart / core-profile  
- Энциклопедия («дом N отвечает за…») без связи с ядром  

## Allowed

- Soft CTA в Deep Sources / Personal Map: «Открыть расшифровку карты» — **только пока decode ещё не собран**  
- LLM prose: целостная история человека (планеты + углы + дома + нумерология) поверх fixed Identity Core  
- Persist decode по fingerprint; reuse на GET и повторный POST (без LLM)  
- Старый `include_editorial` на Map — остаётся map editorial; **не** CE SoT; новый decode preferred когда CE grounded  

## Contract sketch

| Piece | Rule |
|-------|------|
| Trigger | First `POST` when no cache; `GET` returns ready artifact when persisted |
| Gate | CE Identity Core `grounded` + natal facts available; else status + CTA |
| Input | Fixed identity_core · primary tension · natal pack · numerology pack |
| Output nest | `natal_decode_depth_v0` — additive; persisted in `generation_logs` by fingerprint |
| Consumers | Profile Deep Sources / Personal Map UI only; `day_hooks` могут **информировать** Today как derived tips, не как personality SoT |
| Non-consumers | Day Engine as character root · ExperienceSlice personality rewrite · Compat person root |

## Wire

- Prompt id: `profile.natal_decode_depth.v1`  
- Service: `services/natal_decode_depth_v0.py`  
- Houses base layer: `character_engine_house_lines_v0` (thesis `how`/`do`)  
