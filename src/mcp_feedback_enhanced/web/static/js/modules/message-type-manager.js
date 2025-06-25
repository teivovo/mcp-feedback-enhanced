/**
 * MCP Feedback Enhanced - 訊息類型管理模組
 * =======================================
 * 
 * 管理訊息類型常數、驗證和相關行為配置
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};

    /**
     * 訊息類型常數
     */
    const MESSAGE_TYPES = {
        GENERAL: 'general',
        CODE_REVIEW: 'code_review',
        ERROR_REPORT: 'error_report',
        FEATURE_REQUEST: 'feature_request',
        DOCUMENTATION: 'documentation',
        TESTING: 'testing',
        DEPLOYMENT: 'deployment',
        SECURITY: 'security'
    };

    /**
     * 訊息類型元數據
     */
    const MESSAGE_TYPE_METADATA = {
        [MESSAGE_TYPES.GENERAL]: {
            name: '一般訊息',
            icon: '💬',
            color: '#007acc',
            description: '一般用途的訊息和回饋',
            autoSubmitDefault: false,
            timeoutDefault: 600
        },
        [MESSAGE_TYPES.CODE_REVIEW]: {
            name: '程式碼審查',
            icon: '🔍',
            color: '#28a745',
            description: '程式碼審查和建議',
            autoSubmitDefault: false,
            timeoutDefault: 900
        },
        [MESSAGE_TYPES.ERROR_REPORT]: {
            name: '錯誤報告',
            icon: '🐛',
            color: '#dc3545',
            description: '錯誤報告和問題回饋',
            autoSubmitDefault: true,
            timeoutDefault: 300
        },
        [MESSAGE_TYPES.FEATURE_REQUEST]: {
            name: '功能請求',
            icon: '✨',
            color: '#6f42c1',
            description: '新功能請求和改進建議',
            autoSubmitDefault: false,
            timeoutDefault: 1200
        },
        [MESSAGE_TYPES.DOCUMENTATION]: {
            name: '文件相關',
            icon: '📚',
            color: '#17a2b8',
            description: '文件撰寫和更新',
            autoSubmitDefault: false,
            timeoutDefault: 600
        },
        [MESSAGE_TYPES.TESTING]: {
            name: '測試相關',
            icon: '🧪',
            color: '#fd7e14',
            description: '測試執行和結果驗證',
            autoSubmitDefault: true,
            timeoutDefault: 450
        },
        [MESSAGE_TYPES.DEPLOYMENT]: {
            name: '部署相關',
            icon: '🚀',
            color: '#20c997',
            description: '部署和發布相關',
            autoSubmitDefault: true,
            timeoutDefault: 300
        },
        [MESSAGE_TYPES.SECURITY]: {
            name: '安全相關',
            icon: '🔒',
            color: '#e83e8c',
            description: '安全審查和漏洞報告',
            autoSubmitDefault: false,
            timeoutDefault: 900
        }
    };

    /**
     * 訊息類型管理器
     */
    function MessageTypeManager() {
        this.currentMessageType = MESSAGE_TYPES.GENERAL;
        this.typeChangeCallbacks = [];
        this.rulesEngine = null;
    }

    /**
     * 驗證訊息類型
     */
    MessageTypeManager.prototype.isValidMessageType = function(messageType) {
        return Object.values(MESSAGE_TYPES).includes(messageType);
    };

    /**
     * 獲取訊息類型元數據
     */
    MessageTypeManager.prototype.getMessageTypeMetadata = function(messageType) {
        return MESSAGE_TYPE_METADATA[messageType] || MESSAGE_TYPE_METADATA[MESSAGE_TYPES.GENERAL];
    };

    /**
     * 獲取所有訊息類型
     */
    MessageTypeManager.prototype.getAllMessageTypes = function() {
        return Object.keys(MESSAGE_TYPE_METADATA).map(type => ({
            type: type,
            ...MESSAGE_TYPE_METADATA[type]
        }));
    };

    /**
     * 更新當前訊息類型
     */
    MessageTypeManager.prototype.updateMessageType = function(messageType) {
        if (!this.isValidMessageType(messageType)) {
            console.warn('⚠️ 無效的訊息類型:', messageType);
            messageType = MESSAGE_TYPES.GENERAL;
        }

        const oldType = this.currentMessageType;
        this.currentMessageType = messageType;

        console.log('🏷️ 訊息類型更新:', oldType, '->', messageType);

        // 觸發變更回調
        this.typeChangeCallbacks.forEach(callback => {
            try {
                callback(messageType, oldType);
            } catch (error) {
                console.error('❌ 訊息類型變更回調執行失敗:', error);
            }
        });

        // 更新 UI 顯示
        this.updateUIDisplay(messageType);

        // 應用規則（如果有規則引擎）
        if (this.rulesEngine) {
            this.rulesEngine.applyRules(messageType);
        }
    };

    /**
     * 獲取當前訊息類型
     */
    MessageTypeManager.prototype.getCurrentMessageType = function() {
        return this.currentMessageType;
    };

    /**
     * 添加類型變更回調
     */
    MessageTypeManager.prototype.addTypeChangeCallback = function(callback) {
        if (typeof callback === 'function') {
            this.typeChangeCallbacks.push(callback);
        }
    };

    /**
     * 移除類型變更回調
     */
    MessageTypeManager.prototype.removeTypeChangeCallback = function(callback) {
        const index = this.typeChangeCallbacks.indexOf(callback);
        if (index > -1) {
            this.typeChangeCallbacks.splice(index, 1);
        }
    };

    /**
     * 更新 UI 顯示
     */
    MessageTypeManager.prototype.updateUIDisplay = function(messageType) {
        const metadata = this.getMessageTypeMetadata(messageType);
        
        // 更新訊息類型指示器
        const indicator = document.getElementById('messageTypeIndicator');
        if (indicator) {
            indicator.innerHTML = `
                <span class="message-type-icon">${metadata.icon}</span>
                <span class="message-type-name">${metadata.name}</span>
            `;
            indicator.className = `message-type-indicator ${messageType}`;
            indicator.style.borderColor = metadata.color;
            indicator.style.color = metadata.color;
        }

        // 更新頁面標題（如果需要）
        const titleElement = document.querySelector('.message-type-title');
        if (titleElement) {
            titleElement.textContent = metadata.name;
        }

        // 更新描述
        const descElement = document.querySelector('.message-type-description');
        if (descElement) {
            descElement.textContent = metadata.description;
        }
    };

    /**
     * 設置規則引擎
     */
    MessageTypeManager.prototype.setRulesEngine = function(rulesEngine) {
        this.rulesEngine = rulesEngine;
    };

    /**
     * 獲取訊息類型的預設設定
     */
    MessageTypeManager.prototype.getDefaultSettings = function(messageType) {
        const metadata = this.getMessageTypeMetadata(messageType);
        return {
            autoSubmit: metadata.autoSubmitDefault,
            timeout: metadata.timeoutDefault,
            color: metadata.color,
            icon: metadata.icon
        };
    };

    /**
     * 創建訊息類型選擇器
     */
    MessageTypeManager.prototype.createTypeSelector = function(containerId, options) {
        options = options || {};
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('❌ 找不到容器:', containerId);
            return;
        }

        const selector = document.createElement('select');
        selector.className = 'message-type-selector';
        selector.id = options.selectorId || 'messageTypeSelect';

        // 添加選項
        this.getAllMessageTypes().forEach(typeInfo => {
            const option = document.createElement('option');
            option.value = typeInfo.type;
            option.textContent = `${typeInfo.icon} ${typeInfo.name}`;
            if (typeInfo.type === this.currentMessageType) {
                option.selected = true;
            }
            selector.appendChild(option);
        });

        // 添加變更事件
        const self = this;
        selector.addEventListener('change', function() {
            self.updateMessageType(this.value);
        });

        container.appendChild(selector);
        return selector;
    };

    /**
     * 初始化訊息類型管理器
     */
    MessageTypeManager.prototype.initialize = function() {
        console.log('🏷️ 訊息類型管理器初始化完成');
        
        // 初始化 UI 顯示
        this.updateUIDisplay(this.currentMessageType);
    };

    // 創建全域實例
    const messageTypeManager = new MessageTypeManager();

    // 將常數和管理器加入命名空間
    window.MCPFeedback.MESSAGE_TYPES = MESSAGE_TYPES;
    window.MCPFeedback.MESSAGE_TYPE_METADATA = MESSAGE_TYPE_METADATA;
    window.MCPFeedback.MessageTypeManager = messageTypeManager;

    // 自動初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            messageTypeManager.initialize();
        });
    } else {
        messageTypeManager.initialize();
    }

})();
