-- Subscriber deep themes preference (L3 selectable tips)
-- Date: 2026-07-27

ALTER TABLE user_settings
ADD COLUMN IF NOT EXISTS profile_deep_themes JSONB DEFAULT NULL;

COMMENT ON COLUMN user_settings.profile_deep_themes IS 'L3 deep theme preference: {selected:[theme_id], updated_at:iso}';
