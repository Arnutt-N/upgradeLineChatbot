-- Migration 002: Fix metadata column name
-- Description: เปลี่ยน metadata เป็น extra_data (SQLAlchemy reserved word)
-- Date: 2025-07-13

-- Update chat_history table
ALTER TABLE chat_history RENAME COLUMN metadata TO extra_data;

-- Record migration
INSERT INTO migration_history (migration_name) VALUES ('002_fix_metadata_column.sql');
