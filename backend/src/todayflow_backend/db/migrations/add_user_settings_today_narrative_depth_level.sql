-- DE-8: preferred depth for POST /today/narrative (quick | normal | deep)
-- Date: 2026-05-04

ALTER TABLE user_settings
ADD COLUMN IF NOT EXISTS today_narrative_depth_level VARCHAR(20) DEFAULT 'normal';

COMMENT ON COLUMN user_settings.today_narrative_depth_level IS 'Today narrative depth_level: quick, normal, deep';
