# 📊 DATABASE ANALYSIS REPORT

## 🔍 **สถานะปัจจุบันของ Database**

### **🗄️ ตารางที่มีอยู่**
```
📋 TABLE: user_status (1 records)
  - user_id: VARCHAR (NOT NULL) [Primary Key]
  - is_in_live_chat: BOOLEAN (NULL)
  - chat_mode: VARCHAR (NULL) [Default: 'manual']
  - created_at: DATETIME (NULL) [Default: CURRENT_TIMESTAMP]
  - updated_at: DATETIME (NULL)
  - display_name: TEXT (NULL) ✅
  - picture_url: TEXT (NULL) ✅

📬 TABLE: chat_messages (66 records)
  - id: VARCHAR (NOT NULL) [Primary Key]
  - user_id: VARCHAR (NULL) [Foreign Key]
  - sender_type: VARCHAR (NULL) ['user', 'bot', 'admin']
  - message: TEXT (NULL)
  - created_at: DATETIME (NULL) [Default: CURRENT_TIMESTAMP]
```

---

## 🔄 **การใช้งานปัจจุบัน**

### **LINE Admin Live Chat System**
- ✅ ระบบ Live Chat สำหรับ LINE ทำงานปกติ
- ✅ มีข้อมูลผู้ใช้ 1 คน และข้อความ 66 ข้อความ
- ✅ Avatar System พร้อมใช้งาน (display_name, picture_url)
- ✅ WebSocket สำหรับ Real-time Chat

### **API Endpoints ปัจจุบัน**
```
🔗 /admin        → LINE Admin UI
🔗 /webhook      → LINE Webhook
🔗 /admin/reply  → ส่งข้อความตอบกลับ
🔗 /admin/users  → รายการผู้ใช้
🔗 /admin/messages/{user_id} → ข้อความของผู้ใช้
```

---

## 🎯 **แผนการแยกระบบ**

### **Database Tables ที่ต้องเพิ่ม**

#### **1. Shared Tables (ใช้ร่วมกัน)**
```sql
-- ✅ user_status (มีอยู่แล้ว - ใช้ร่วมกัน)
-- ✅ chat_messages (มีอยู่แล้ว - ใช้ร่วมกัน)

-- 🆕 shared_notifications (แจ้งเตือนระหว่างระบบ)
CREATE TABLE shared_notifications (
    id VARCHAR PRIMARY KEY,
    from_system VARCHAR NOT NULL,  -- 'forms' หรือ 'line_admin'
    to_system VARCHAR NOT NULL,
    type VARCHAR NOT NULL,         -- 'form_update', 'chat_alert'
    data TEXT,                     -- JSON data
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 🆕 shared_audit_logs (Log การทำงาน)
CREATE TABLE shared_audit_logs (
    id VARCHAR PRIMARY KEY,
    system VARCHAR NOT NULL,       -- 'forms' หรือ 'line_admin'
    action VARCHAR NOT NULL,       -- 'create', 'update', 'delete'
    table_name VARCHAR,
    record_id VARCHAR,
    user_id VARCHAR,
    changes TEXT,                  -- JSON before/after
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **2. Forms System Tables (เฉพาะ Admin Panel)**
```sql
-- 🆕 form_submissions (คำขอฟอร์ม)
CREATE TABLE form_submissions (
    id VARCHAR PRIMARY KEY,
    form_type VARCHAR NOT NULL,    -- 'kp7', 'id_card'
    user_id VARCHAR,               -- Link to user_status
    user_name VARCHAR NOT NULL,
    user_email VARCHAR,
    user_phone VARCHAR,
    status VARCHAR DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'rejected'
    form_data TEXT,               -- JSON ข้อมูลฟอร์ม
    notes TEXT,                   -- หมายเหตุ
    assigned_to VARCHAR,          -- เจ้าหน้าที่ที่รับผิดชอบ
    priority INTEGER DEFAULT 1,   -- ลำดับความสำคัญ
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- 🆕 form_attachments (ไฟล์แนบ)
CREATE TABLE form_attachments (
    id VARCHAR PRIMARY KEY,
    form_id VARCHAR NOT NULL,     -- Foreign Key to form_submissions
    file_name VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES form_submissions(id)
);

-- 🆕 admin_users (ผู้ดูแลระบบฟอร์ม)
CREATE TABLE admin_users (
    id VARCHAR PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    email VARCHAR,
    role VARCHAR DEFAULT 'officer', -- 'admin', 'officer', 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 🆕 form_status_history (ประวัติการเปลี่ยนสถานะ)
CREATE TABLE form_status_history (
    id VARCHAR PRIMARY KEY,
    form_id VARCHAR NOT NULL,
    old_status VARCHAR,
    new_status VARCHAR NOT NULL,
    changed_by VARCHAR,           -- admin_user_id
    notes TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES form_submissions(id)
);
```

#### **3. LINE Admin Tables (เฉพาะ LINE Admin)**
```sql
-- 🆕 line_rich_menus (เมนู LINE)
CREATE TABLE line_rich_menus (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    rich_menu_id VARCHAR,         -- LINE Rich Menu ID
    image_url VARCHAR,
    is_active BOOLEAN DEFAULT FALSE,
    menu_data TEXT,              -- JSON configuration
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 🆕 line_templates (Template ข้อความ)
CREATE TABLE line_templates (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    category VARCHAR,            -- 'greeting', 'faq', 'closing'
    template_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_by VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 🆕 line_bot_settings (การตั้งค่าบอท)
CREATE TABLE line_bot_settings (
    id VARCHAR PRIMARY KEY,
    setting_key VARCHAR UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚨 **ความเสี่ยงและข้อควรระวัง**

### **🔴 High Risk**
- **Database Migration:** ต้องระมัดระวังไม่ให้กระทบ chat_messages ที่มีอยู่
- **WebSocket Connections:** ต้องแยกการจัดการ WebSocket สำหรับ 2 ระบบ
- **Shared Database:** ต้องระวังการ conflict เมื่อใช้ตารางร่วมกัน

### **🟡 Medium Risk**
- **Authentication System:** ต้องสร้างระบบ login ใหม่สำหรับ Forms Admin
- **Static Files:** ต้องแยก assets สำหรับ 2 ระบบ
- **Configuration:** ต้องแยก settings สำหรับ Forms

### **🟢 Low Risk**
- **Database Models:** เพิ่มตารางใหม่ไม่กระทบของเก่า
- **Templates:** สร้าง templates ใหม่แยกส่วน

---

## 📋 **แผนการดำเนินงานแบบระมัดระวัง**

### **Phase 0: Backup & Safety** 🛡️
```bash
# 1. Backup Database
cp chatbot.db chatbot_backup_$(date +%Y%m%d_%H%M%S).db

# 2. Backup Code
git add . && git commit -m "Before system separation"

# 3. Create development branch
git checkout -b feature/admin-forms-separation
```

### **Phase 1: URL Structure Planning** 🗺️
```
ปัจจุบัน:
/admin → LINE Admin Live Chat

แยกใหม่:
/admin → LINE Admin Live Chat (เหมือนเดิม - ไม่ต้องย้าย)
/form-admin → Admin Panel Forms (ใหม่)
```

### **Phase 2: Database Migration** 📊
```sql
-- สร้างตารางใหม่โดยไม่กระทบของเก่า
-- ทดสอบการ migrate ใน development ก่อน
-- ใช้ transaction เพื่อ rollback ได้
```

### **Phase 3: API Separation** 🔌
```
เดิม: app/api/routers/admin.py → LINE Admin
ใหม่: 
- app/api/routers/admin.py → LINE Admin (เหมือนเดิม)
- app/api/routers/form_admin.py → Forms Admin (ใหม่)
```

---

## ✅ **Next Steps Recommendation**

**ลำดับความปลอดภัย:**

1. **สร้าง backup** database และ code
2. **สร้าง Forms Admin** ที่ URL ใหม่ (/form-admin)
3. **สร้างตารางใหม่** สำหรับ Forms System
4. **พัฒนา Admin Panel UI** ตาม mockup
5. **สร้าง API endpoints** สำหรับ Forms
6. **Integration Testing** ระหว่าง 2 ระบบ
7. **ทดสอบการทำงานร่วมกัน**

---

**🎯 พร้อมเริ่มขั้นตอนไหนก่อน?**

**A)** Phase 0: สร้าง Backup และ Safety
**B)** Phase 1: สร้าง Forms Admin ที่ /form-admin  
**C)** Phase 2: สร้างตารางใหม่สำหรับ Forms System
**D)** อื่นๆ (ระบุ)

รอคำสั่งถัดไป! 🔥
