-- Add observations column to day_rituals table
-- This column stores observations from evening ritual: {noticed: "...", hardest: "...", easier: "..."}

ALTER TABLE day_rituals 
ADD COLUMN IF NOT EXISTS observations JSON;

-- Add comment
COMMENT ON COLUMN day_rituals.observations IS 'Evening observations: {noticed: "...", hardest: "...", easier: "..."}';
