## Summary

- 

## Design system

- [ ] Использую только `Ds*` примитивы и `--tf-*` / `--day-*` токены
- [ ] Не добавил новых `.cta*` / `.card*` / `.actionButton` / `.submitButton` классов в `*.module.css`
- [ ] Не добавил сырых hex для ink/surface и новых `--orbit-*` / `--todayflow-*` / `--tdp-*` / `--product-*` объявлений (gate: `scripts/check_ds_style_gate.py`)

## Testing

- [ ] Frontend lint/tests pass locally
- [ ] Backend tests pass locally
- [ ] User-facing copy policy checks pass (web + iOS)
- [ ] `python3 scripts/check_ds_style_gate.py` exits 0 (new violations fail; baseline warnings OK)

## Mobile Parity (Required)

- [ ] Web changes are mirrored for iOS behavior and copy
- [ ] API contract changes are compatible for iOS and future Android
- [ ] Any intentional parity gap is documented with follow-up task

## Risk Check

- [ ] Error/empty/loading states provide clear next action
- [ ] No user-facing technical/internal wording leaked into copy
