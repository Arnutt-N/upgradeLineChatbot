/* Loading Animations for Admin Panel */

// Loading Animation Manager Class
class LoadingManager {
    constructor() {
        this.loadingStates = new Map();
        this.initializeLoadingElements();
    }

    initializeLoadingElements() {
        // สร้าง Loading Overlay
        this.createLoadingOverlay();
        // สร้าง Message Loading Indicators
        this.createMessageLoadingIndicators();
    }

    createLoadingOverlay() {
        if (document.getElementById('loadingOverlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                <div class="loading-text">กำลังโหลด...</div>
                <div class="loading-subtext">กรุณารอสักครู่</div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    createMessageLoadingIndicators() {
        const styles = `
        .message-loading {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 4px 0;
            background: rgba(37, 99, 235, 0.1);
            border-radius: 12px;
            font-size: 14px;
            color: var(--primary);
            border-left: 3px solid var(--primary);
        }

        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
            margin-right: 8px;
        }

        .typing-dot {
            width: 6px;
            height: 6px;
            background: var(--primary);
            border-radius: 50%;
            animation: typingDots 1.4s infinite ease-in-out both;
        }

        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        .typing-dot:nth-child(3) { animation-delay: 0s; }

        @keyframes typingDots {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease-in-out;
        }

        .loading-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .loading-content {
            text-align: center;
            color: white;
            max-width: 300px;
        }

        .loading-spinner {
            position: relative;
            display: inline-block;
            width: 64px;
            height: 64px;
            margin-bottom: 20px;
        }

        .spinner-ring {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 3px solid transparent;
            border-radius: 50%;
            animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        }

        .spinner-ring:nth-child(1) {
            border-top-color: #3b82f6;
            animation-delay: -0.45s;
        }

        .spinner-ring:nth-child(2) {
            border-top-color: #10b981;
            animation-delay: -0.3s;
        }

        .spinner-ring:nth-child(3) {
            border-top-color: #f59e0b;
            animation-delay: -0.15s;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .loading-subtext {
            font-size: 14px;
            opacity: 0.8;
        }

        /* Button Loading States */
        .btn-loading {
            position: relative;
            pointer-events: none;
            opacity: 0.7;
        }

        .btn-loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 16px;
            height: 16px;
            margin: -8px 0 0 -8px;
            border: 2px solid transparent;
            border-top: 2px solid currentColor;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        `;

        // เพิ่ม styles ไปยัง document
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    // แสดง Full Screen Loading
    showFullScreenLoading(text = 'กำลังโหลด...', subtext = 'กรุณารอสักครู่') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.querySelector('.loading-text').textContent = text;
            overlay.querySelector('.loading-subtext').textContent = subtext;
            overlay.classList.add('active');
        }
    }

    // ซ่อน Full Screen Loading
    hideFullScreenLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    // แสดง Button Loading
    showButtonLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button && !button.classList.contains('btn-loading')) {
            button.setAttribute('data-original-text', button.textContent);
            button.textContent = '';
            button.classList.add('btn-loading');
        }
    }

    // ซ่อน Button Loading
    hideButtonLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button && button.classList.contains('btn-loading')) {
            button.classList.remove('btn-loading');
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.textContent = originalText;
                button.removeAttribute('data-original-text');
            }
        }
    }

    // แสดง Message Loading Indicator
    showMessageLoading(userId, message = 'กำลังส่งข้อความ...') {
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer && !document.querySelector('.message-loading')) {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message-loading';
            loadingDiv.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span>${message}</span>
            `;
            messagesContainer.appendChild(loadingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        this.loadingStates.set('message_' + userId, true);
    }

    // ซ่อน Message Loading Indicator
    hideMessageLoading(userId) {
        const loadingElement = document.querySelector('.message-loading');
        if (loadingElement) {
            loadingElement.remove();
        }
        this.loadingStates.delete('message_' + userId);
    }

    // ตรวจสอบสถานะการโหลด
    isLoading(key) {
        return this.loadingStates.has(key) && this.loadingStates.get(key);
    }

    // เคลียร์การโหลดทั้งหมด
    clearAllLoading() {
        this.hideFullScreenLoading();
        document.querySelectorAll('.btn-loading').forEach(btn => {
            btn.classList.remove('btn-loading');
            const originalText = btn.getAttribute('data-original-text');
            if (originalText) {
                btn.textContent = originalText;
                btn.removeAttribute('data-original-text');
            }
        });
        document.querySelectorAll('.message-loading').forEach(el => el.remove());
        this.loadingStates.clear();
    }
}

// Global Loading Manager Instance
window.loadingManager = new LoadingManager();

// Helper Functions สำหรับใช้ง่าย
function showLoading(text, subtext) {
    window.loadingManager.showFullScreenLoading(text, subtext);
}

function hideLoading() {
    window.loadingManager.hideFullScreenLoading();
}

function showButtonLoading(buttonId) {
    window.loadingManager.showButtonLoading(buttonId);
}

function hideButtonLoading(buttonId) {
    window.loadingManager.hideButtonLoading(buttonId);
}

function showMessageLoading(userId, message) {
    window.loadingManager.showMessageLoading(userId, message);
}

function hideMessageLoading(userId) {
    window.loadingManager.hideMessageLoading(userId);
}

console.log('✅ Loading Animation Manager initialized successfully');
