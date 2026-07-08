-- Migration: Add current_residence fields to astro_profiles table
-- Date: 2026-01-04

ALTER TABLE astro_profiles 
ADD COLUMN IF NOT EXISTS current_residence_city VARCHAR,
ADD COLUMN IF NOT EXISTS current_residence_latitude FLOAT,
ADD COLUMN IF NOT EXISTS current_residence_longitude FLOAT;

