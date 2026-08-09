Mobile "Today ritual" building blocks, lifted from the TodayFlow-Потоk-Дня prototype: a mood-driven radial-gradient background (8 palettes, see Day Atmosphere colors), frosted glass cards that sit on top of it, carousel dots/arrows for a step flow, a bottom tab bar, priority/promise chip groups, and habit streak rows with day dots.

```jsx
<DsMoodBackground mood="radiance" style={{minHeight:780,borderRadius:40}}>
  <DsGlassCard mood="radiance">Today's theme…</DsGlassCard>
</DsMoodBackground>
```

Use `mood` consistently across `DsMoodBackground` and any `DsGlassCard`/reveal inside it — the glass tint and ink color both depend on whether the mood is light (six of eight) or dark (`tension`, `depth`).
