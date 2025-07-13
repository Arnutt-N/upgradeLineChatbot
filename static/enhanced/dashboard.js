class EnhancedDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = 30000; // 30 seconds
        this.isLoading = false;
        
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        await this.loadRecentActivities();
        await this.loadSystemHealth();
        this.initializeTooltips();
        this.startAutoRefresh();
    }

    async fetchData(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    async loadDashboardData() {
        try {
            this.setLoadingState(true);
            
            const data = await this.fetchData('/api/enhanced/dashboard/summary');
            
            if (data.success) {
                this.updateDashboardStats(data.data);
                this.updateCharts(data.data);
            }
        } catch (error) {
            this.handleError(error, 'Loading dashboard data');
        } finally {
            this.setLoadingState(false);
        }
    }

    async loadRecentActivities() {
        try {
            const data = await this.fetchData('/api/enhanced/friends/recent?limit=10');
            
            if (data.success) {
                this.updateActivitiesList(data.data);
            }
        } catch (error) {
            this.handleError(error, 'Loading recent activities');
        }
    }

    async loadSystemHealth() {
        try {
            const data = await this.fetchData('/api/enhanced/system/health');
            
            if (data.success) {
                this.updateSystemHealth(data.data);
            }
        } catch (error) {
            this.handleError(error, 'Loading system health');
        }
    }

    updateDashboardStats(data) {
        // Update stats based on the dashboard summary structure
        this.updateStatElement('totalChats', data.chat?.total_messages_7d || 0);
        this.updateStatElement('todayChats', data.chat?.total_messages_7d || 0);
        this.updateStatElement('activeUsers', data.chat?.active_users_7d || 0);
        this.updateStatElement('systemUptime', 'Online');
        this.updateStatElement('totalUsers', data.friends?.net_growth_7d || 0);
        this.updateStatElement('queuedNotifications', data.telegram?.total_notifications_7d || 0);
    }

    updateStatElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    updateActivitiesList(activities) {
        const container = document.getElementById('activitiesList');
        if (!container) return;

        // Handle the friends recent data structure
        if (activities && activities.length > 0) {
            container.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-icon ${activity.activity_type || 'info'}" style="background: #e8f5e8;">
                        ${this.getActivityIcon(activity.activity_type || 'info')}
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.activity_type || 'Activity'} - ${activity.user_id || 'Unknown'}</div>
                        <div class="activity-time">${this.formatRelativeTime(activity.timestamp)}</div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon info" style="background: #e8f5e8;">📝</div>
                    <div class="activity-content">
                        <div class="activity-title">No recent activities</div>
                        <div class="activity-time">Check back later</div>
                    </div>
                </div>
            `;
        }
    }

    updateSystemHealth(health) {
        const container = document.getElementById('systemHealth');
        if (!container) return;

        const statusClass = health?.status === 'healthy' ? 'status-healthy' : 'status-warning';
        
        container.innerHTML = `
            <div class="health-status ${statusClass}">
                <div class="status-indicator"></div>
                <span>System ${health?.status || 'Unknown'}</span>
            </div>
            <div class="health-metrics">
                <div class="metric">
                    <span>CPU:</span>
                    <span>${health?.cpu_usage || 0}%</span>
                </div>
                <div class="metric">
                    <span>Memory:</span>
                    <span>${health?.memory_usage || 0}%</span>
                </div>
                <div class="metric">
                    <span>Database:</span>
                    <span class="status-${health?.database_status || 'unknown'}">${health?.database_status || 'Unknown'}</span>
                </div>
            </div>
        `;
    }

    updateCharts(data) {
        // Create mock chart data from the summary data
        const chatData = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            values: [
                Math.floor(Math.random() * 100),
                Math.floor(Math.random() * 100),
                Math.floor(Math.random() * 100),
                Math.floor(Math.random() * 100),
                Math.floor(Math.random() * 100),
                Math.floor(Math.random() * 100),
                data.chat?.total_messages_7d || 0
            ]
        };

        const activityData = {
            labels: ['Messages', 'New Followers', 'Notifications', 'Errors'],
            values: [
                data.chat?.total_messages_7d || 0,
                data.friends?.new_followers_7d || 0,
                data.telegram?.notifications_sent_7d || 0,
                data.system?.total_logs_24h || 0
            ]
        };

        this.updateChatTrendChart(chatData);
        this.updateUserActivityChart(activityData);
    }

    updateChatTrendChart(chartData) {
        const config = {
            type: 'line',
            data: {
                labels: chartData.labels || [],
                datasets: [{
                    label: 'Messages',
                    data: chartData.values || [],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        };
        
        this.createChart('chatTrendChart', config);
    }

    updateUserActivityChart(chartData) {
        const config = {
            type: 'doughnut',
            data: {
                labels: chartData.labels || [],
                datasets: [{
                    data: chartData.values || [],
                    backgroundColor: [
                        '#3B82F6',
                        '#10B981',
                        '#F59E0B',
                        '#EF4444'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        };
        
        this.createChart('userActivityChart', config);
    }

    getActivityIcon(type) {
        const icons = {
            'message': '💬',
            'user': '👤',
            'system': '⚙️',
            'error': '❌',
            'success': '✅',
            'follow': '➕',
            'unfollow': '➖',
            'join': '🎉',
            'leave': '👋',
            'info': '📝'
        };
        return icons[type] || '📝';
    }

    formatRelativeTime(timestamp) {
        const now = new Date();
        const date = new Date(timestamp);
        const diff = now - date;
        
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days > 0) return `${days} วันที่แล้ว`;
        if (hours > 0) return `${hours} ชั่วโมงที่แล้ว`;
        if (minutes > 0) return `${minutes} นาทีที่แล้ว`;
        return 'เมื่อสักครู่';
    }

    // Notification system
    showNotification(title, message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification-toast ${type}`;
        notification.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="font-semibold">${title}</div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto">×</button>
            </div>
            <div class="mt-1 text-sm">${message}</div>
        `;

        document.body.appendChild(notification);
        
        // Show animation
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 500);
        }, duration);
    }

    // API action methods
    async testTelegram() {
        try {
            this.showNotification('Testing', 'Testing Telegram connection...', 'info');
            
            const data = await this.fetchData('/api/enhanced/telegram/test', {
                method: 'POST'
            });
            
            if (data.success) {
                this.showNotification('Success', 'Telegram connection successful!', 'success');
            } else {
                this.showNotification('Error', `Telegram test failed: ${data.data?.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            this.showNotification('Error', `Test failed: ${error.message}`, 'error');
        }
    }

    async exportData() {
        try {
            this.showNotification('Exporting', 'Preparing data export...', 'info');
            
            const response = await fetch('/api/enhanced/chat/export');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `chat_history_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                this.showNotification('Success', 'Data exported successfully!', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            this.showNotification('Error', `Export failed: ${error.message}`, 'error');
        }
    }

    async processNotificationQueue() {
        try {
            this.showNotification('Processing', 'Processing notification queue...', 'info');
            
            const data = await this.fetchData('/api/enhanced/telegram/process-queue', {
                method: 'POST'
            });
            
            if (data.success) {
                const stats = data.data;
                const message = `Processed: ${stats.sent || 0} sent, ${stats.failed || 0} failed`;
                this.showNotification('Complete', message, 'success');
            }
        } catch (error) {
            this.showNotification('Error', `Queue processing failed: ${error.message}`, 'error');
        }
    }

    // Chart management
    createChart(canvasId, config) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Create new chart
        this.charts[canvasId] = new Chart(ctx.getContext('2d'), config);
        return this.charts[canvasId];
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    // Theme management
    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        
        this.showNotification('Theme', `Switched to ${isDark ? 'dark' : 'light'} mode`, 'info');
    }

    setLoadingState(isLoading) {
        this.isLoading = isLoading;
        const loadingElements = document.querySelectorAll('.loading-indicator');
        loadingElements.forEach(el => {
            el.style.display = isLoading ? 'block' : 'none';
        });
    }

    refreshAllData() {
        if (!this.isLoading) {
            this.loadDashboardData();
            this.loadRecentActivities();
            this.loadSystemHealth();
        }
    }

    initializeTooltips() {
        // Simple tooltip implementation
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = e.target.dataset.tooltip;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 0.8rem;
                    z-index: 1000;
                    pointer-events: none;
                `;
                
                document.body.appendChild(tooltip);
                
                const rect = e.target.getBoundingClientRect();
                tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
                tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
            });
            
            element.addEventListener('mouseleave', () => {
                document.querySelectorAll('.tooltip').forEach(tooltip => tooltip.remove());
            });
        });
    }

    // Auto refresh management
    startAutoRefresh() {
        setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.refreshAllData();
            }
        }, this.refreshInterval);
    }

    setRefreshInterval(seconds) {
        this.refreshInterval = seconds * 1000;
        this.showNotification('Settings', `Refresh interval set to ${seconds} seconds`, 'info');
    }

    // Utility methods
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(ms) {
        if (ms < 1000) return `${ms}ms`;
        if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
        if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
        return `${(ms / 3600000).toFixed(1)}h`;
    }

    // Error handling
    handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        this.showNotification('Error', `${context}: ${error.message}`, 'error');
    }

    // Performance monitoring
    measurePerformance(name, fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        
        console.log(`Performance [${name}]: ${(end - start).toFixed(2)}ms`);
        return result;
    }

    async measureAsyncPerformance(name, asyncFn) {
        const start = performance.now();
        const result = await asyncFn();
        const end = performance.now();
        
        console.log(`Async Performance [${name}]: ${(end - start).toFixed(2)}ms`);
        return result;
    }
}

// Global dashboard instance
let dashboard;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new EnhancedDashboard();
    
    // Load saved theme
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        document.body.classList.add('dark-mode');
    }
    
    // Expose global functions for HTML onclick handlers
    window.testTelegram = () => dashboard.testTelegram();
    window.exportData = () => dashboard.exportData();
    window.refreshActivities = () => dashboard.loadRecentActivities();
    window.refreshSystemStatus = () => dashboard.loadSystemHealth();
    window.processQueue = () => dashboard.processNotificationQueue();
    window.toggleDarkMode = () => dashboard.toggleDarkMode();
    window.showSystemLogs = async () => {
        try {
            const data = await dashboard.fetchData('/api/enhanced/system/logs?limit=20');
            if (data.success) {
                const logs = data.data;
                const logHtml = logs.map(log => {
                    const levelColors = {
                        'error': '#ff6b6b',
                        'warning': '#ffa726',
                        'info': '#42a5f5',
                        'debug': '#66bb6a'
                    };
                    
                    const color = levelColors[log.log_level] || '#666';
                    const time = new Date(log.timestamp).toLocaleString('th-TH');
                    
                    return `
                        <div style="padding: 10px; border-left: 4px solid ${color}; margin-bottom: 10px; background: #f8f9fa;">
                            <div style="font-weight: 600; color: ${color};">[${log.log_level.toUpperCase()}] ${log.category}</div>
                            <div style="margin: 5px 0;">${log.message}</div>
                            <div style="font-size: 0.8rem; color: #666;">${time}</div>
                        </div>
                    `;
                }).join('');
                
                showModal('📝 System Logs', `<div style="max-height: 400px; overflow-y: auto;" class="custom-scrollbar">${logHtml}</div>`);
            }
        } catch (error) {
            dashboard.handleError(error, 'Loading system logs');
        }
    };
});

// Additional utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Show modal (global function for compatibility)
function showModal(title, content) {
    if (dashboard) {
        dashboard.showNotification(title, content, 'info', 5000);
    } else {
        alert(`${title}: ${content}`);
    }
}

// Close modal (global function for compatibility)
function closeModal() {
    document.querySelectorAll('.notification-toast').forEach(toast => toast.remove());
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EnhancedDashboard };
}