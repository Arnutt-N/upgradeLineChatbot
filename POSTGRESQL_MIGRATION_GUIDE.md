# PostgreSQL Migration Guide สำหรับ AI Agent น้อง HR Moj

## ภาพรวม

ระบบได้เตรียมพร้อมสำหรับการย้ายจาก SQLite ไปยัง PostgreSQL แล้ว โดยใช้กลยุทธ์ Environment-based switching ที่ไม่กระทบการทำงานที่มีอยู่

## การเตรียมพร้อมที่เสร็จสิ้นแล้ว

### ✅ 1. PostgreSQL Models
- **ไฟล์**: `app/db/postgresql/models_postgres.py`
- **ฟีเจอร์**: UUID primary keys, JSONB columns, Full-text search, Performance indexes
- **ตาราง**: UserStatus, ChatMessage, FormSubmission, AnalyticsEvent, SystemSettings

### ✅ 2. Database Configuration
- **ไฟล์**: `app/db/postgresql/database_config.py`
- **ฟีเจอร์**: Environment-based URL generation, Connection pooling, Async session management
- **รองรับ**: Development (SQLite), Production (PostgreSQL), Test environments

### ✅ 3. CRUD Layer Updates
- **ไฟล์**: `app/db/crud.py`
- **ฟีเจอร์**: Conditional imports based on ENVIRONMENT variable
- **ความเข้ากันได้**: SQLite และ PostgreSQL models

### ✅ 4. Dependencies
- **ไฟล์**: `requirements.txt`
- **เพิ่มแล้ว**: `asyncpg==0.29.0`, `psycopg2-binary==2.9.9`

### ✅ 5. Environment Configuration
- **ไฟล์**: `.env`
- **ตั้งค่า**: `DATABASE_URL`, `ENVIRONMENT` variable
- **พร้อมใช้**: PostgreSQL connection string

## การใช้งาน

### Development Mode (SQLite)
```bash
# ใน .env
ENVIRONMENT=development
# DATABASE_URL จะใช้ SQLite โดยอัตโนมัติ
```

### Production Mode (PostgreSQL)
```bash
# ใน .env
ENVIRONMENT=production
DATABASE_URL=postgresql://hrmoj_user:xxxx@dpg-xxxx.oregon-postgres.render.com/hrmoj_db
```

## การทดสอบ

### 1. ทดสอบการเชื่อมต่อ
```bash
python test_postgresql_connection.py
```

### 2. ทดสอบทั้งสองโหมด
```bash
python test_database_modes.py
```

## ข้อดีของ PostgreSQL Setup

### 🚀 Performance Features
- **UUID Primary Keys**: ป้องกัน ID collision
- **JSONB Columns**: การจัดเก็บข้อมูลที่ยืดหยุ่น
- **GIN Indexes**: การค้นหาที่รวดเร็วใน JSONB
- **Full-text Search**: การค้นหาข้อความภาษาไทย

### 🛡️ Advanced Features
- **Connection Pooling**: การจัดการ connection ที่มีประสิทธิภาพ
- **Async Operations**: การทำงานแบบ asynchronous
- **Time-series Optimization**: สำหรับ analytics data
- **Partitioning Support**: สำหรับข้อมูลขนาดใหญ่

## การย้ายข้อมูล (Migration Steps)

### Step 1: Backup Current Data
```bash
# Export SQLite data
python export_sqlite_data.py
```

### Step 2: Switch to Production
```bash
# ใน .env
ENVIRONMENT=production
```

### Step 3: Create Tables
```bash
python create_postgresql_tables.py
```

### Step 4: Import Data
```bash
python import_to_postgresql.py
```

## ความปลอดภัย

### 🔐 Security Features
- **Environment Variables**: API keys และ secrets ไม่ถูก hardcode
- **Connection Pooling**: ป้องกัน connection exhaustion
- **SQL Injection Protection**: ใช้ SQLAlchemy ORM
- **Input Validation**: ผ่าน Pydantic models

## การ Monitor

### 📊 Monitoring Points
- **Connection Pool Status**: ตรวจสอบ active connections
- **Query Performance**: ใช้ PostgreSQL EXPLAIN
- **Database Size**: ตรวจสอบการใช้ space
- **Index Usage**: ตรวจสอบประสิทธิภาพ indexes

## Troubleshooting

### ปัญหาที่อาจเกิดขึ้น
1. **Connection Timeout**: ตรวจสอบ network และ firewall
2. **Authentication Error**: ตรวจสอบ username/password
3. **Database Not Found**: ตรวจสอบ database name
4. **Permission Denied**: ตรวจสอบ user permissions

### การแก้ไข
```bash
# ทดสอบ connection
python test_postgresql_connection.py

# ตรวจสอบ environment
echo $ENVIRONMENT

# ตรวจสอบ URL
echo $DATABASE_URL
```

## สรุป

✅ **ระบบพร้อมสำหรับ PostgreSQL แล้ว**
- Environment-based switching ทำงานได้ปกติ
- PostgreSQL models และ configuration เตรียมพร้อมแล้ว
- CRUD layer รองรับทั้ง SQLite และ PostgreSQL
- Dependencies และ configuration ครบถ้วน
- การทดสอบผ่านทั้งสองโหมด

**หมายเหตุ**: การเปลี่ยนแปลงนี้ทำอย่างระมัดระวัง โดยไม่กระทบต่อส่วนอื่นที่ทำงานได้ดีอยู่แล้ว ระบบสามารถสลับระหว่าง SQLite และ PostgreSQL ได้โดยการเปลี่ยน `ENVIRONMENT` variable เท่านั้น