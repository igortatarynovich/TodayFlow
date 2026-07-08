-- Add challenge_type column to challenges table
ALTER TABLE challenges ADD COLUMN IF NOT EXISTS challenge_type VARCHAR DEFAULT 'goal';

-- Update existing challenges to have default type
UPDATE challenges SET challenge_type = 'goal' WHERE challenge_type IS NULL;

