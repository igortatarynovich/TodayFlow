-- Ops: keep only the two live testers. Run against production todayflow.
BEGIN;

CREATE TEMP TABLE _keep AS
  SELECT id FROM users
  WHERE lower(trim(email)) IN (
    'victoria.tatarynovich@gmail.com',
    'pakistandiller@gmail.com'
  );

DO $$
BEGIN
  IF (SELECT count(*) FROM _keep) <> 2 THEN
    RAISE EXCEPTION 'keep set must be 2, got %', (SELECT count(*) FROM _keep);
  END IF;
END $$;

DELETE FROM cached_natal_charts
 WHERE astro_profile_id IN (
   SELECT id FROM astro_profiles WHERE user_id NOT IN (SELECT id FROM _keep)
 );
DELETE FROM subscription_history
 WHERE subscription_id IN (
   SELECT id FROM subscriptions WHERE user_id NOT IN (SELECT id FROM _keep)
 );
DELETE FROM challenge_task_completions
 WHERE participant_id IN (
   SELECT id FROM challenge_participants WHERE user_id NOT IN (SELECT id FROM _keep)
 );

DO $$
DECLARE
  t text;
  c text;
  leftover int := 1;
  pass int := 0;
BEGIN
  WHILE leftover > 0 AND pass < 15 LOOP
    leftover := 0;
    pass := pass + 1;
    FOR t, c IN
      SELECT tc.table_name, kcu.column_name
      FROM information_schema.table_constraints tc
      JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
      JOIN information_schema.constraint_column_usage ccu
        ON ccu.constraint_name = tc.constraint_name
      WHERE tc.constraint_type = 'FOREIGN KEY'
        AND ccu.table_name = 'users'
    LOOP
      BEGIN
        EXECUTE format(
          'DELETE FROM %I WHERE %I IS NOT NULL AND %I NOT IN (SELECT id FROM _keep)',
          t, c, c
        );
      EXCEPTION WHEN foreign_key_violation THEN
        leftover := leftover + 1;
      END;
    END LOOP;
  END LOOP;
  IF leftover > 0 THEN
    RAISE EXCEPTION 'could not clear child tables after % passes', pass;
  END IF;
END $$;

DELETE FROM users WHERE id NOT IN (SELECT id FROM _keep);

COMMIT;

SELECT id, email FROM users ORDER BY id;
