# แนวทางแก้ไขปัญหาการแสดงข้อความซ้ำ

## ปัญหาที่พบ

1. **ข้อความจาก AI ถูกบันทึก 2 ประเภท**:
   - `ai_bot` - จาก handle_live_chat_message และ handle_bot_mode_message
   - `ai_response` - จาก handle_image_message และ handle_file_message

2. **การแสดงผลซ้ำเมื่อรีเฟรช**:
   - ข้อความเดียวกันอาจถูกแสดงเป็น 2 บรรทัดเพราะมี message_type ต่างกัน

## วิธีแก้ไข

### 1. แก้ไขการแสดงผลในหน้าแอดมิน (admin.html)

```javascript
// เพิ่มฟังก์ชันกรองข้อความซ้ำเมื่อโหลดจากฐานข้อมูล
function filterDuplicateMessages(messages) {
    const seen = new Map();
    const filtered = [];
    
    messages.forEach(msg => {
        // สร้าง key จาก user_id + content + timestamp (ภายใน 5 วินาที)
        const timestamp = new Date(msg.created_at).getTime();
        const timeKey = Math.floor(timestamp / 5000); // กลุ่มทุก 5 วินาที
        const key = `${msg.user_id}_${msg.message}_${timeKey}`;
        
        // ถ้ายังไม่เคยเห็น หรือ เป็นประเภทที่ต้องการมากกว่า
        if (!seen.has(key) || shouldPreferType(msg.sender_type, seen.get(key).sender_type)) {
            seen.set(key, msg);
        }
    });
    
    // แปลง Map กลับเป็น array และเรียงตามเวลา
    return Array.from(seen.values()).sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
    );
}

// กำหนดลำดับความสำคัญของ message type
function shouldPreferType(newType, existingType) {
    const priority = {
        'user': 1,
        'admin': 2,
        'ai_bot': 3,
        'bot': 4,
        'ai_response': 5,
        'system': 6
    };
    
    return (priority[newType] || 999) < (priority[existingType] || 999);
}
```

### 2. แก้ไขใน loadMessagesFromDatabase

```javascript
// แก้ไขส่วนที่แสดงข้อความ
if (data.messages && data.messages.length > 0) {
    // กรองข้อความซ้ำก่อนแสดง
    const filteredMessages = filterDuplicateMessages(data.messages);
    
    let messageCount = 0;
    filteredMessages.forEach(msg => {
        if (msg.message && msg.sender_type && msg.created_at) {
            // แปลง ai_response เป็น bot สำหรับการแสดงผล
            const displayType = msg.sender_type === 'ai_response' ? 'bot' : msg.sender_type;
            displayMessage(msg.message, displayType, msg.created_at);
            messageCount++;
        }
    });
    console.log(`✅ Displayed ${messageCount} messages (filtered from ${data.messages.length})`);
}
```

### 3. ป้องกันการบันทึกซ้ำในอนาคต (ไม่จำเป็นต้องทำตอนนี้)

สำหรับอนาคต อาจพิจารณา:
- ใช้ message_type เดียวสำหรับ AI responses ทั้งหมด
- เพิ่ม unique constraint ในฐานข้อมูลเพื่อป้องกันการบันทึกซ้ำ
- ตรวจสอบก่อนบันทึกว่ามีข้อความเดียวกันภายใน 5 วินาทีหรือไม่

---
สร้างเมื่อ: ${new Date().toISOString()}
