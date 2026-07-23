# Product Prompt Library

**Статус:** POINTER — не SoT  
**Ядро:** [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md)

Промпты — **Implementations** контракта (ключевой IP TodayFlow под конкретную модель).  
Они не второстепенны, но и не единственный источник логики.

```text
Contract     = что должно произойти (schemas · deps · execution · quality)
Implementations = как модель этого добивается (промпт GPT / Claude / Gemini / DeepSeek / local)
```

См. структуру `Personality → Contract + Implementations` в Generation Contracts.
