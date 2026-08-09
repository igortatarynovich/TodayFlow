DsButton is a pill-shaped call-to-action button — the only hard-cornered element in the system is text; every actionable surface is a capsule.

```jsx
<DsButton variant="primary" href="/today">Begin your day</DsButton>
<DsButton variant="secondary" size="sm">Log in</DsButton>
```

Variants: `primary` (solid gold, uppercase, lifts + gold-glows on hover), `secondary` (outlined ink), `ghost` (no border, sentence case, for tertiary actions), `destructive` (solid error red). Sizes: `sm`, `md`, `block` (full width). Pass `href` to render as a link; omit it for a `<button>`. `DsIconButton` is the circular icon-only variant used for avatar/settings triggers.
