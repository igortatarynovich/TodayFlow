-- Migration: Add context fields to journal_entries table
-- These fields allow linking journal entries to practices, tarot cards, patterns, and days

-- Add practice_id column (nullable, links to practice)
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS practice_id VARCHAR;

-- Add tarot_card_id column (nullable, links to tarot card)
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS tarot_card_id VARCHAR;

-- Add pattern_axis_id column (nullable, links to pattern axis A1-A7)
ALTER TABLE journal_entries 
ADD COLUMN IF NOT EXISTS pattern_axis_id VARCHAR;

-- Add day column (nullable, date of the day for evening entries)
-- Note: In the model it's defined as Date, but we need to check if it exists first
-- If the column exists as INTEGER, we might need to change it to DATE
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'journal_entries' 
        AND column_name = 'day'
    ) THEN
        ALTER TABLE journal_entries ADD COLUMN day DATE;
    END IF;
END $$;

