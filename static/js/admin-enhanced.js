/* Enhanced Admin Panel Functions */

// Enhanced Functions for Admin Panel
class AdminPanelEnhanced {
    constructor() {
        this.currentUserId = null;
        this.users = new Map();
        this.websocket = null;
        this.retryCount = 0;
        this.maxRetries = 5;
        this.isOnline = navigator.onLine;
        this.initializeEnhancedFeatures();
    }

    initializeEnhancedFeatures() {
        // เพิ่ม Online/Offline Detection
        this.setupOnlineOfflineDetection();
        // เพิ่ม Auto-refresh capabilities
        this.setupAutoRefresh();
        // เพิ่ม Enhanced Error Handling
        this.setupErrorHandling();
    }

    setupOnlineOfflineDetection() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            console.log('🟢 Connection restored');
            this.showStatusMessage('เชื่อมต่ออินเทอร์เน็ตแล้ว', 'success');
            this.reconnectWebSocket();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('🔴 Connection lost');
            this.showStatusMessage('ขาดการเชื่อมต่ออินเทอร์เน็ต', 'error');
        });
    }

    setupAutoRefresh() {
        // รีเฟรชรายชื่อผู้ใช้ทุก 30 วินาที
        setInterval(() => {
            if (this.isOnline && !window.loadingManager.isLoading('users')) {
                this.refreshUsersQuietly();
            }
        }, 30000);
    }

    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('🚨 JavaScript Error:', event.error);
            this.logError('JavaScript Error', event.error.message, event.filename, event.lineno);
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('🚨 Unhandled Promise Rejection:', event.reason);
            this.logError('Promise Rejection', event.reason.toString());
        });
    }

    logError(type, message, file = '', line = 0) {
        const errorData = {
            type: type,
            message: message,
            file: file,
            line: line,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        };
        
        // ส่งข้อมูล error ไปยัง server (ถ้าต้องการ)
        // this.sendErrorToServer(errorData);
    }

    // Enhanced User Loading with retry mechanism
    async loadUsersWithRetry() {
        let attempt = 0;
        while (attempt < this.maxRetries) {
            try {
                showLoading('กำลังโหลดรายชื่อผู้ใช้...', `ความพยายามครั้งที่ ${attempt + 1}`);
                
                const response = await fetch('/admin/users');
                if (response.ok) {
                    const data = await response.json();
                    this.processUsersData(data);
                    hideLoading();
                    this.retryCount = 0; // Reset retry count on success
                    return true;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            } catch (error) {
                attempt++;
                console.error(`❌ Users load attempt ${attempt} failed:`, error);
                
                if (attempt >= this.maxRetries) {
                    hideLoading();
                    this.showError('ไม่สามารถโหลดรายชื่อผู้ใช้ได้', 'กรุณาตรวจสอบการเชื่อมต่อและลองใหม่');
                    return false;
                }
                
                // รอก่อนลองใหม่ (exponential backoff)
                const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
                await this.sleep(delay);
            }
        }
        return false;
    }

    processUsersData(data) {
        if (!data || !data.users) {
            console.warn('⚠️ Invalid users data received');
            return;
        }

        console.log(`📊 Processing ${data.users.length} users...`);
        
        // อัปเดต users map
        this.users.clear();
        data.users.forEach(user => {
            this.users.set(user.user_id, user);
        });

        // อัปเดต UI
        this.updateUsersDisplay(data.users);
    }

    updateUsersDisplay(users) {
        const usersList = document.getElementById('usersList');
        if (!usersList) return;

        if (users.length === 0) {
            usersList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">👥</div>
                    <h3>ยังไม่มีผู้ใช้</h3>
                    <p>รอผู้ใช้เข้ามาแชทใหม่</p>
                    <button onclick="adminPanel.loadUsersWithRetry()" class="btn-primary">
                        <i class="fas fa-refresh"></i> รีเฟรช
                    </button>
                </div>
            `;
            return;
        }

        usersList.innerHTML = users.map(user => this.createUserElement(user)).join('');
    }

    createUserElement(user) {
        const isActive = user.user_id === this.currentUserId;
        const lastActivity = user.last_activity ? 
            new Date(user.last_activity).toLocaleString('th-TH') : 
            'ไม่มีข้อมูล';
        
        const statusClass = user.is_in_live_chat ? 'online' : 'offline';
        const statusText = user.is_in_live_chat ? 'กำลังแชท' : 'ออฟไลน์';
        
        return `
            <div class="user-item ${isActive ? 'active' : ''}" 
                 onclick="adminPanel.selectUser('${user.user_id}')" 
                 data-user-id="${user.user_id}">
                <div class="user-avatar">
                    <img src="${user.picture_url || '/static/images/avatars/default_user_avatar.png'}" 
                         alt="${user.display_name}"
                         onerror="this.onerror=null; this.src='/static/images/avatars/default_user_avatar.png';">
                    <div class="status-indicator ${statusClass}"></div>
                </div>
                <div class="user-info">
                    <div class="user-name">${user.display_name}</div>
                    <div class="user-status">${statusText}</div>
                    <div class="user-last-message">${user.latest_message || 'ยังไม่มีข้อความ'}</div>
                    <div class="user-last-activity">${lastActivity}</div>
                </div>
                ${user.unread_count > 0 ? `<div class="unread-count">${user.unread_count}</div>` : ''}
            </div>
        `;
    }

    // Enhanced Message Loading
    async loadUserMessages(userId) {
        if (!userId) return;

        try {
            showMessageLoading(userId, 'กำลังโหลดข้อความ...');
            
            const response = await fetch(`/admin/messages/${userId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            hideMessageLoading(userId);

            if (data.messages) {
                this.displayMessages(data.messages);
                this.showStatusMessage(`โหลดข้อความ ${data.messages.length} ข้อความเรียบร้อย`, 'success');
            } else if (data.error) {
                throw new Error(data.error);
            }

        } catch (error) {
            hideMessageLoading(userId);
            console.error(`❌ Error loading messages for user ${userId}:`, error);
            this.showError('ไม่สามารถโหลดข้อความได้', error.message);
        }
    }

    displayMessages(messages) {
        const container = document.getElementById('messagesContainer');
        if (!container) return;

        if (messages.length === 0) {
            container.innerHTML = `
                <div class="empty-messages">
                    <div class="empty-icon">💬</div>
                    <h3>ยังไม่มีการสนทนา</h3>
                    <p>รอผู้ใช้ส่งข้อความเข้ามา</p>
                </div>
            `;
            return;
        }

        container.innerHTML = messages.map(message => this.createMessageElement(message)).join('');
        container.scrollTop = container.scrollHeight;
    }

    createMessageElement(message) {
        const time = new Date(message.created_at).toLocaleString('th-TH', {
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: '2-digit'
        });

        const senderClass = message.sender_type || 'unknown';
        const senderName = this.getSenderName(message.sender_type);

        return `
            <div class="message ${senderClass}">
                <div class="message-content">
                    <div class="message-text">${this.formatMessageText(message.message)}</div>
                    <div class="message-info">
                        <span class="sender">${senderName}</span>
                        <span class="time">${time}</span>
                    </div>
                </div>
            </div>
        `;
    }

    getSenderName(senderType) {
        const names = {
            'user': '👤 ลูกค้า',
            'admin': '👨‍💼 แอดมิน',
            'bot': '🤖 บอท',
            'system': '⚙️ ระบบ'
        };
        return names[senderType] || '❓ ไม่ระบุ';
    }

    formatMessageText(text) {
        if (!text) return '';
        
        // แปลง URL เป็น links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        text = text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // แปลง line breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    // Enhanced Send Message with Loading States
    async sendMessageEnhanced(message, userId = null) {
        const targetUserId = userId || this.currentUserId;
        if (!message || !targetUserId) return;

        try {
            // แสดง loading states
            showButtonLoading('sendBtn');
            showMessageLoading(targetUserId, 'กำลังส่งข้อความ...');

            const response = await fetch('/admin/reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: targetUserId,
                    message: message
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            // แสดงข้อความในอินเทอร์เฟซทันที
            this.addMessageToDisplay(message, 'admin');
            
            // เคลียร์ input
            const input = document.getElementById('messageInput');
            if (input) {
                input.value = '';
                this.autoResizeTextarea();
            }

            // แสดงข้อความสำเร็จ
            this.showStatusMessage('ส่งข้อความเรียบร้อย', 'success');

        } catch (error) {
            console.error('❌ Error sending message:', error);
            this.showError('ไม่สามารถส่งข้อความได้', error.message);
        } finally {
            hideButtonLoading('sendBtn');
            hideMessageLoading(targetUserId);
        }
    }

    addMessageToDisplay(message, senderType) {
        const container = document.getElementById('messagesContainer');
        if (!container) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${senderType}`;
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.formatMessageText(message)}</div>
                <div class="message-info">
                    <span class="sender">${this.getSenderName(senderType)}</span>
                    <span class="time">${new Date().toLocaleString('th-TH', {
                        hour: '2-digit',
                        minute: '2-digit'
                    })}</span>
                </div>
            </div>
        `;

        container.appendChild(messageElement);
        container.scrollTop = container.scrollHeight;

        // เพิ่ม animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(10px)';
        setTimeout(() => {
            messageElement.style.transition = 'all 0.3s ease';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
    }

    // Utility Functions
    showStatusMessage(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${this.getStatusIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    }

    getStatusIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    showError(title, message) {
        this.showStatusMessage(`${title}: ${message}`, 'error', 5000);
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async refreshUsersQuietly() {
        try {
            const response = await fetch('/admin/users');
            if (response.ok) {
                const data = await response.json();
                this.processUsersData(data);
            }
        } catch (error) {
            console.warn('⚠️ Quiet refresh failed:', error);
        }
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('messageInput');
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            
            const sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                sendBtn.disabled = !textarea.value.trim();
            }
        }
    }

    selectUser(userId) {
        this.currentUserId = userId;
        
        // อัปเดต active state
        document.querySelectorAll('.user-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`[data-user-id="${userId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // โหลดข้อความ
        this.loadUserMessages(userId);
        
        // อัปเดต header
        const user = this.users.get(userId);
        if (user) {
            this.updateChatHeader(user);
        }
    }

    updateChatHeader(user) {
        const header = document.querySelector('.chat-header');
        if (header && user) {
            header.innerHTML = `
                <div class="chat-user-info">
                    <img src="${user.picture_url || '/static/images/avatars/default_user_avatar.png'}" 
                         alt="${user.display_name}" class="user-avatar-small">
                    <div>
                        <div class="user-name">${user.display_name}</div>
                        <div class="user-status">${user.is_in_live_chat ? 'กำลังแชท' : 'ออฟไลน์'}</div>
                    </div>
                </div>
                <div class="chat-actions">
                    <button onclick="adminPanel.refreshChat()" class="btn-icon" title="รีเฟรชการแชท">
                        <i class="fas fa-sync"></i>
                    </button>
                </div>
            `;
        }
    }

    refreshChat() {
        if (this.currentUserId) {
            this.loadUserMessages(this.currentUserId);
        }
    }

    reconnectWebSocket() {
        if (this.websocket) {
            try {
                this.websocket.close();
            } catch (e) {
                console.warn('Error closing existing websocket:', e);
            }
        }
        
        // รอสักครู่แล้วค่อยเชื่อมต่อใหม่
        setTimeout(() => {
            if (window.connectWebSocket) {
                window.connectWebSocket();
            }
        }, 1000);
    }
}

// Global Admin Panel Instance
window.adminPanel = new AdminPanelEnhanced();

console.log('✅ Enhanced Admin Panel initialized successfully');
