-- Wave 2 Phase A: tap_event_v1 store (also created via Base.metadata.create_all on fresh DBs)
CREATE TABLE IF NOT EXISTS today_tap_events (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(64) NOT NULL UNIQUE,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  day_facts_id VARCHAR(96) NOT NULL,
  local_date DATE NOT NULL,
  scene_id VARCHAR(128) NOT NULL,
  domain VARCHAR(32) NOT NULL DEFAULT 'work',
  prompted_text TEXT NOT NULL,
  response VARCHAR(32) NOT NULL,
  free_text TEXT,
  responded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  created_at TIMESTAMP WITHOUT TIME ZONE,
  CONSTRAINT uq_today_tap_user_date_scene UNIQUE (user_id, local_date, scene_id)
);
