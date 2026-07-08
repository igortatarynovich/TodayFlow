-- Третья шкала в пофазных чек-инах (как в QuickPulse: энергия / настроение / стресс)
ALTER TABLE state_check_ins ADD COLUMN IF NOT EXISTS stress_scale INTEGER;
