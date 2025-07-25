-- Migration 001: Add Enhanced Tracking Tables
-- Date: 2025-07-13

-- Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    message_type TEXT NOT NULL,
    message_content TEXT NOT NULL,
    admin_user_id TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    message_id TEXT,
    reply_token TEXT,
    session_id TEXT,
    metadata TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Friend Activity Table  
CREATE TABLE IF NOT EXISTS friend_activity (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    user_profile TEXT,
    source TEXT DEFAULT 'line_webhook',
    event_data TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Telegram Notifications Table
CREATE TABLE IF NOT EXISTS telegram_notifications (
    id TEXT PRIMARY KEY,
    notification_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    user_id TEXT,
    admin_user_id TEXT,
    telegram_message_id INTEGER,
    telegram_chat_id TEXT,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    data TEXT,
    scheduled_at DATETIME,
    sent_at DATETIME,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Telegram Settings Table
CREATE TABLE IF NOT EXISTS telegram_settings (
    id TEXT PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type TEXT DEFAULT 'string',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    updated_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System Logs Table
CREATE TABLE IF NOT EXISTS system_logs (
    id TEXT PRIMARY KEY,
    log_level TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    message TEXT NOT NULL,
    details TEXT,
    user_id TEXT,
    admin_user_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    request_id TEXT,
    performance_ms INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Migration History Table
CREATE TABLE IF NOT EXISTS migration_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT NOT NULL,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);
