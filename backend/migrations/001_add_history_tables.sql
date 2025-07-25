-- Migration 001: เพิ่มตารางประวัติและ Tracking
-- Date: 2025-07-13
-- Description: เพิ่มตารางสำหรับ comprehensive history tracking และ Telegram integration

-- ========================================
-- 1. Chat History (ประวัติการแชทแบบละเอียด)
-- ========================================
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    message_type TEXT NOT NULL, -- 'user', 'admin', 'bot'
    message_content TEXT NOT NULL,
    admin_user_id TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    message_id TEXT,
    reply_token TEXT,
    session_id TEXT,
    metadata TEXT, -- JSON
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_message_type ON chat_history(message_type);
CREATE INDEX IF NOT EXISTS idx_chat_history_admin_user_id ON chat_history(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);

-- ========================================
-- 2. Friend Activity (ประวัติเพื่อน)
-- ========================================
CREATE TABLE IF NOT EXISTS friend_activity (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    activity_type TEXT NOT NULL, -- 'follow', 'unfollow', 'block', 'unblock'
    user_profile TEXT, -- JSON
    source TEXT DEFAULT 'line_webhook',
    event_data TEXT, -- JSON
    ip_address TEXT,
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_friend_activity_user_id ON friend_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_friend_activity_type ON friend_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_friend_activity_timestamp ON friend_activity(timestamp);

-- ========================================
-- 3. Telegram Notifications
-- ========================================
CREATE TABLE IF NOT EXISTS telegram_notifications (
    id TEXT PRIMARY KEY,
    notification_type TEXT NOT NULL, -- 'chat_request', 'new_friend', 'system_alert', 'user_message'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    user_id TEXT,
    telegram_message_id INTEGER,
    telegram_chat_id TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'failed', 'retry'
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    retry_after DATETIME,
    priority INTEGER DEFAULT 1, -- 1-5
    metadata TEXT, -- JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_telegram_notifications_type ON telegram_notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_user_id ON telegram_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_status ON telegram_notifications(status);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_created_at ON telegram_notifications(created_at);

-- ========================================
-- 4. Telegram Settings
-- ========================================
CREATE TABLE IF NOT EXISTS telegram_settings (
    id TEXT PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type TEXT DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    category TEXT DEFAULT 'general', -- 'general', 'notifications', 'alerts', 'bot'
    is_sensitive BOOLEAN DEFAULT FALSE,
    updated_by TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_telegram_settings_key ON telegram_settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_telegram_settings_category ON telegram_settings(category);

-- ========================================
-- 5. System Logs
-- ========================================
CREATE TABLE IF NOT EXISTS system_logs (
    id TEXT PRIMARY KEY,
    log_level TEXT NOT NULL, -- 'debug', 'info', 'warning', 'error', 'critical'
    category TEXT NOT NULL, -- 'line_webhook', 'telegram', 'admin', 'system', 'database'
    module TEXT,
    function_name TEXT,
    message TEXT NOT NULL,
    details TEXT, -- JSON
    user_id TEXT,
    session_id TEXT,
    request_id TEXT,
    execution_time INTEGER, -- milliseconds
    memory_usage INTEGER, -- bytes
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_category ON system_logs(category);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_session_id ON system_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);

-- ========================================
-- 6. Insert Default Telegram Settings
-- ========================================
INSERT OR IGNORE INTO telegram_settings (id, setting_key, setting_value, setting_type, description, category) VALUES
('telegram_001', 'bot_enabled', 'true', 'boolean', 'เปิด/ปิดการใช้งาน Telegram Bot', 'bot'),
('telegram_002', 'notification_chat_request', 'true', 'boolean', 'แจ้งเตือนเมื่อมีคำขอแชท', 'notifications'),
('telegram_003', 'notification_new_friend', 'true', 'boolean', 'แจ้งเตือนเมื่อมีเพื่อนใหม่', 'notifications'),
('telegram_004', 'notification_system_alert', 'true', 'boolean', 'แจ้งเตือนเมื่อมี system alert', 'notifications'),
('telegram_005', 'retry_max_attempts', '3', 'number', 'จำนวนครั้งสูงสุดในการ retry', 'general'),
('telegram_006', 'retry_delay_minutes', '5', 'number', 'หน่วงเวลาระหว่าง retry (นาที)', 'general'),
('telegram_007', 'queue_max_size', '1000', 'number', 'ขนาดสูงสุดของ notification queue', 'general'),
('telegram_008', 'message_format', '{"chat_request": "🚨 *มีคำขอแชทใหม่* 🚨\\n\\n*จาก:* {user_name}\\n*ข้อความ:* {message}", "new_friend": "👋 *มีเพื่อนใหม่* 👋\\n\\n*ชื่อ:* {user_name}\\n*เวลา:* {timestamp}"}', 'json', 'รูปแบบข้อความแจ้งเตือน', 'notifications');

-- ========================================
-- 7. Log Migration Completion
-- ========================================
INSERT INTO system_logs (id, log_level, category, module, message, details, timestamp) VALUES
('migration_001_' || strftime('%s', 'now'), 'info', 'database', 'migration', 'Migration 001 completed successfully', '{"migration": "001_add_history_tables", "tables_added": ["chat_history", "friend_activity", "telegram_notifications", "telegram_settings", "system_logs"], "indexes_created": 15, "default_settings_added": 8}', CURRENT_TIMESTAMP);

-- ========================================
-- Migration 001 Complete
-- ========================================