-- Migration: Add challenge_day_tasks and challenge_task_completions tables
-- Created: 2024

CREATE TABLE IF NOT EXISTS challenge_day_tasks (
    id SERIAL PRIMARY KEY,
    challenge_id VARCHAR NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL CHECK (day_number > 0),
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    task_type VARCHAR NOT NULL DEFAULT 'reflection' CHECK (task_type IN ('reflection', 'action', 'journal', 'meditation')),
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(challenge_id, day_number, "order")
);

CREATE INDEX IF NOT EXISTS idx_challenge_day_tasks_challenge_id ON challenge_day_tasks(challenge_id);
CREATE INDEX IF NOT EXISTS idx_challenge_day_tasks_day_number ON challenge_day_tasks(challenge_id, day_number);

CREATE TABLE IF NOT EXISTS challenge_task_completions (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER NOT NULL REFERENCES challenge_participants(id) ON DELETE CASCADE,
    task_id INTEGER NOT NULL REFERENCES challenge_day_tasks(id) ON DELETE CASCADE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(participant_id, task_id)
);

CREATE INDEX IF NOT EXISTS idx_challenge_task_completions_participant_id ON challenge_task_completions(participant_id);
CREATE INDEX IF NOT EXISTS idx_challenge_task_completions_task_id ON challenge_task_completions(task_id);

