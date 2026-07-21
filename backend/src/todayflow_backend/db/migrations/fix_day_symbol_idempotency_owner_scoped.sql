-- P0: day-symbol idempotency must be scoped by owner_key.
-- Previously global UNIQUE(card_idempotency_key) / UNIQUE(number_idempotency_key)
-- let user B receive user A's reveal when both sent number_reveal:${date}.

ALTER TABLE day_symbol_states DROP CONSTRAINT IF EXISTS uq_day_symbol_card_idem;
ALTER TABLE day_symbol_states DROP CONSTRAINT IF EXISTS uq_day_symbol_number_idem;

-- Partial uniques: multiple NULLs allowed (not yet revealed).
CREATE UNIQUE INDEX IF NOT EXISTS uq_day_symbol_owner_card_idem
    ON day_symbol_states (owner_key, card_idempotency_key)
    WHERE card_idempotency_key IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_day_symbol_owner_number_idem
    ON day_symbol_states (owner_key, number_idempotency_key)
    WHERE number_idempotency_key IS NOT NULL;
