/**
 * MCP Feedback Enhanced - WebSocket 管理模組
 * =========================================
 * 
 * 處理 WebSocket 連接、訊息傳遞和重連邏輯
 */

(function() {
    'use strict';

    // 確保命名空間和依賴存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * WebSocket 管理器建構函數
     */
    function WebSocketManager(options) {
        options = options || {};

        this.websocket = null;
        this.isConnected = false;
        this.connectionReady = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || Utils.CONSTANTS.MAX_RECONNECT_ATTEMPTS;
        this.reconnectDelay = options.reconnectDelay || Utils.CONSTANTS.DEFAULT_RECONNECT_DELAY;
        this.heartbeatInterval = null;
        this.heartbeatFrequency = options.heartbeatFrequency || Utils.CONSTANTS.DEFAULT_HEARTBEAT_FREQUENCY;

        // 事件回調
        this.onOpen = options.onOpen || null;
        this.onMessage = options.onMessage || null;
        this.onClose = options.onClose || null;
        this.onError = options.onError || null;
        this.onConnectionStatusChange = options.onConnectionStatusChange || null;

        // 標籤頁管理器引用
        this.tabManager = options.tabManager || null;

        // 連線監控器引用
        this.connectionMonitor = options.connectionMonitor || null;

        // UI 管理器引用（用於智能滾動）
        this.uiManager = options.uiManager || null;

        // 待處理的提交
        this.pendingSubmission = null;
        this.sessionUpdatePending = false;

        // 網路狀態檢測
        this.networkOnline = navigator.onLine;
        this.setupNetworkStatusDetection();
    }

    /**
     * 建立 WebSocket 連接
     */
    WebSocketManager.prototype.connect = function() {
        if (!Utils.isWebSocketSupported()) {
            console.error('❌ 瀏覽器不支援 WebSocket');
            return;
        }

        // 確保 WebSocket URL 格式正確
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = protocol + '//' + host + '/ws';

        console.log('嘗試連接 WebSocket:', wsUrl);
        const connectingMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.connecting') : '連接中...';
        this.updateConnectionStatus('connecting', connectingMessage);

        try {
            // 如果已有連接，先關閉
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }

            this.websocket = new WebSocket(wsUrl);
            this.setupWebSocketEvents();

        } catch (error) {
            console.error('WebSocket 連接失敗:', error);
            const connectionFailedMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.connectionFailed') : '連接失敗';
            this.updateConnectionStatus('error', connectionFailedMessage);
        }
    };

    /**
     * 設置 WebSocket 事件監聽器
     */
    WebSocketManager.prototype.setupWebSocketEvents = function() {
        const self = this;

        this.websocket.onopen = function() {
            self.handleOpen();
        };

        this.websocket.onmessage = function(event) {
            self.handleMessage(event);
        };

        this.websocket.onclose = function(event) {
            self.handleClose(event);
        };

        this.websocket.onerror = function(error) {
            self.handleError(error);
        };
    };

    /**
     * 處理連接開啟
     */
    WebSocketManager.prototype.handleOpen = function() {
        this.isConnected = true;
        this.connectionReady = false; // 等待連接確認
        const connectedMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.connected') : '已連接';
        this.updateConnectionStatus('connected', connectedMessage);
        console.log('WebSocket 連接已建立');

        // 重置重連計數器和延遲
        this.reconnectAttempts = 0;
        this.reconnectDelay = Utils.CONSTANTS.DEFAULT_RECONNECT_DELAY;

        // 通知連線監控器
        if (this.connectionMonitor) {
            this.connectionMonitor.startMonitoring();
        }

        // 開始心跳
        this.startHeartbeat();

        // 請求會話狀態
        this.requestSessionStatus();

        // 調用外部回調
        if (this.onOpen) {
            this.onOpen();
        }
    };

    /**
     * 處理訊息接收
     */
    WebSocketManager.prototype.handleMessage = function(event) {
        try {
            const data = Utils.safeJsonParse(event.data, null);
            if (data) {
                // 記錄訊息到監控器
                if (this.connectionMonitor) {
                    this.connectionMonitor.recordMessage();
                }

                this.processMessage(data);

                // 觸發智能滾動處理
                if (this.uiManager && this.uiManager.handleNewMessage) {
                    this.uiManager.handleNewMessage(data);
                }

                // 調用外部回調
                if (this.onMessage) {
                    this.onMessage(data);
                }
            }
        } catch (error) {
            console.error('解析 WebSocket 訊息失敗:', error);
        }
    };

    /**
     * 處理連接關閉
     */
    WebSocketManager.prototype.handleClose = function(event) {
        this.isConnected = false;
        this.connectionReady = false;
        console.log('WebSocket 連接已關閉, code:', event.code, 'reason:', event.reason);

        // 停止心跳
        this.stopHeartbeat();

        // 通知連線監控器
        if (this.connectionMonitor) {
            this.connectionMonitor.stopMonitoring();
        }

        // 處理不同的關閉原因
        if (event.code === 4004) {
            const noActiveSessionMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.noActiveSession') : '沒有活躍會話';
            this.updateConnectionStatus('disconnected', noActiveSessionMessage);
        } else {
            const disconnectedMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.disconnected') : '已斷開';
            this.updateConnectionStatus('disconnected', disconnectedMessage);
            this.handleReconnection(event);
        }

        // 調用外部回調
        if (this.onClose) {
            this.onClose(event);
        }
    };

    /**
     * 處理連接錯誤
     */
    WebSocketManager.prototype.handleError = function(error) {
        console.error('WebSocket 錯誤:', error);
        const connectionErrorMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.connectionError') : '連接錯誤';
        this.updateConnectionStatus('error', connectionErrorMessage);

        // 調用外部回調
        if (this.onError) {
            this.onError(error);
        }
    };

    /**
     * 處理重連邏輯
     */
    WebSocketManager.prototype.handleReconnection = function(event) {
        // 會話更新導致的正常關閉，立即重連
        if (event.code === 1000 && event.reason === '會話更新') {
            console.log('🔄 會話更新導致的連接關閉，立即重連...');
            this.sessionUpdatePending = true;
            const self = this;
            setTimeout(function() {
                self.connect();
            }, 200);
        }
        // 檢查是否應該重連
        else if (this.shouldAttemptReconnect(event)) {
            this.reconnectAttempts++;

            // 改進的指數退避算法：基礎延遲 * 2^重試次數，加上隨機抖動
            const baseDelay = Utils.CONSTANTS.DEFAULT_RECONNECT_DELAY;
            const exponentialDelay = baseDelay * Math.pow(2, this.reconnectAttempts - 1);
            const jitter = Math.random() * 1000; // 0-1秒的隨機抖動
            this.reconnectDelay = Math.min(exponentialDelay + jitter, 30000); // 最大 30 秒

            console.log(Math.round(this.reconnectDelay / 1000) + '秒後嘗試重連... (第' + this.reconnectAttempts + '次)');

            // 更新狀態為重連中
            const reconnectingTemplate = window.i18nManager ? window.i18nManager.t('connectionMonitor.reconnecting') : '重連中... (第{attempt}次)';
            const reconnectingMessage = reconnectingTemplate.replace('{attempt}', this.reconnectAttempts);
            this.updateConnectionStatus('reconnecting', reconnectingMessage);

            const self = this;
            setTimeout(function() {
                console.log('🔄 開始重連 WebSocket... (第' + self.reconnectAttempts + '次)');
                self.connect();
            }, this.reconnectDelay);
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('❌ 達到最大重連次數，停止重連');
            const maxReconnectMessage = window.i18nManager ? window.i18nManager.t('connectionMonitor.maxReconnectReached') : 'WebSocket 連接失敗，請刷新頁面重試';
            Utils.showMessage(maxReconnectMessage, Utils.CONSTANTS.MESSAGE_ERROR);
        }
    };

    /**
     * 處理訊息
     */
    WebSocketManager.prototype.processMessage = function(data) {
        console.log('收到 WebSocket 訊息:', data);

        switch (data.type) {
            case 'connection_established':
                console.log('WebSocket 連接確認');
                this.connectionReady = true;
                this.handleConnectionReady();
                break;
            case 'heartbeat_response':
                this.handleHeartbeatResponse();
                // 記錄 pong 時間到監控器
                if (this.connectionMonitor) {
                    this.connectionMonitor.recordPong();
                }
                break;
            case 'session_update':
                this.handleSessionUpdate(data);
                break;
            case 'message_type_update':
                this.handleMessageTypeUpdate(data);
                break;
            default:
                // 其他訊息類型由外部處理
                break;
        }
    };

    /**
     * 處理連接就緒
     */
    WebSocketManager.prototype.handleConnectionReady = function() {
        // 如果有待提交的內容，現在可以提交了
        if (this.pendingSubmission) {
            console.log('🔄 連接就緒，提交待處理的內容');
            const self = this;
            setTimeout(function() {
                if (self.pendingSubmission) {
                    self.send(self.pendingSubmission);
                    self.pendingSubmission = null;
                }
            }, 100);
        }
    };

    /**
     * 處理心跳回應
     */
    WebSocketManager.prototype.handleHeartbeatResponse = function() {
        if (this.tabManager) {
            this.tabManager.updateLastActivity();
        }
    };

    /**
     * 發送訊息
     */
    WebSocketManager.prototype.send = function(data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            try {
                this.websocket.send(JSON.stringify(data));
                return true;
            } catch (error) {
                console.error('發送 WebSocket 訊息失敗:', error);
                return false;
            }
        } else {
            console.warn('WebSocket 未連接，無法發送訊息');
            return false;
        }
    };

    /**
     * 請求會話狀態
     */
    WebSocketManager.prototype.requestSessionStatus = function() {
        this.send({
            type: 'get_status'
        });
    };

    /**
     * 開始心跳
     */
    WebSocketManager.prototype.startHeartbeat = function() {
        this.stopHeartbeat();

        const self = this;
        this.heartbeatInterval = setInterval(function() {
            if (self.websocket && self.websocket.readyState === WebSocket.OPEN) {
                // 記錄 ping 時間到監控器
                if (self.connectionMonitor) {
                    self.connectionMonitor.recordPing();
                }

                self.send({
                    type: 'heartbeat',
                    tabId: self.tabManager ? self.tabManager.getTabId() : null,
                    timestamp: Date.now()
                });
            }
        }, this.heartbeatFrequency);

        console.log('💓 WebSocket 心跳已啟動，頻率: ' + this.heartbeatFrequency + 'ms');
    };

    /**
     * 停止心跳
     */
    WebSocketManager.prototype.stopHeartbeat = function() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
            console.log('💔 WebSocket 心跳已停止');
        }
    };

    /**
     * 更新連接狀態
     */
    WebSocketManager.prototype.updateConnectionStatus = function(status, text) {
        if (this.onConnectionStatusChange) {
            this.onConnectionStatusChange(status, text);
        }
    };

    /**
     * 設置待處理的提交
     */
    WebSocketManager.prototype.setPendingSubmission = function(data) {
        this.pendingSubmission = data;
    };

    /**
     * 檢查是否已連接且就緒
     */
    WebSocketManager.prototype.isReady = function() {
        return this.isConnected && this.connectionReady;
    };

    /**
     * 設置網路狀態檢測
     */
    WebSocketManager.prototype.setupNetworkStatusDetection = function() {
        const self = this;

        // 監聽網路狀態變化
        window.addEventListener('online', function() {
            console.log('🌐 網路已恢復，嘗試重新連接...');
            self.networkOnline = true;

            // 如果 WebSocket 未連接且不在重連過程中，立即嘗試連接
            if (!self.isConnected && self.reconnectAttempts < self.maxReconnectAttempts) {
                // 重置重連計數器，因為網路問題已解決
                self.reconnectAttempts = 0;
                self.reconnectDelay = Utils.CONSTANTS.DEFAULT_RECONNECT_DELAY;

                setTimeout(function() {
                    self.connect();
                }, 1000); // 延遲 1 秒確保網路穩定
            }
        });

        window.addEventListener('offline', function() {
            console.log('🌐 網路已斷開');
            self.networkOnline = false;

            // 更新連接狀態
            const offlineMessage = window.i18nManager ?
                window.i18nManager.t('connectionMonitor.offline', '網路已斷開') :
                '網路已斷開';
            self.updateConnectionStatus('offline', offlineMessage);
        });
    };

    /**
     * 檢查是否應該嘗試重連
     */
    WebSocketManager.prototype.shouldAttemptReconnect = function(event) {
        // 如果網路離線，不嘗試重連
        if (!this.networkOnline) {
            console.log('🌐 網路離線，跳過重連');
            return false;
        }

        // 如果是正常關閉，不重連
        if (event.code === 1000) {
            return false;
        }

        // 如果達到最大重連次數，不重連
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            return false;
        }

        return true;
    };

    /**
     * 關閉連接
     */
    WebSocketManager.prototype.close = function() {
        this.stopHeartbeat();
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        this.connectionReady = false;
    };

    /**
     * 處理會話更新
     */
    WebSocketManager.prototype.handleSessionUpdate = function(data) {
        console.log('🔄 收到會話更新:', data);

        // 更新會話信息，包括 message_type
        if (data.session_data) {
            this.currentSessionData = data.session_data;

            // 如果有 message_type，觸發相關處理
            if (data.session_data.message_type) {
                this.handleMessageTypeChange(data.session_data.message_type);
            }

            // 觸發會話更新事件
            if (this.onSessionUpdate) {
                this.onSessionUpdate(data.session_data);
            }
        }
    };

    /**
     * 處理訊息類型更新
     */
    WebSocketManager.prototype.handleMessageTypeUpdate = function(data) {
        console.log('📝 收到訊息類型更新:', data);

        if (data.message_type) {
            this.handleMessageTypeChange(data.message_type);
        }
    };

    /**
     * 處理訊息類型變更
     */
    WebSocketManager.prototype.handleMessageTypeChange = function(messageType) {
        console.log('🏷️ 訊息類型變更為:', messageType);

        // 更新當前訊息類型
        this.currentMessageType = messageType;

        // 觸發訊息類型變更事件
        if (this.onMessageTypeChange) {
            this.onMessageTypeChange(messageType);
        }

        // 通知其他模組
        if (window.MCPFeedback && window.MCPFeedback.MessageTypeManager) {
            window.MCPFeedback.MessageTypeManager.updateMessageType(messageType);
        }
    };

    /**
     * 獲取當前訊息類型
     */
    WebSocketManager.prototype.getCurrentMessageType = function() {
        return this.currentMessageType || 'general';
    };

    /**
     * 設置訊息類型變更回調
     */
    WebSocketManager.prototype.setMessageTypeChangeCallback = function(callback) {
        this.onMessageTypeChange = callback;
    };

    /**
     * 設置會話更新回調
     */
    WebSocketManager.prototype.setSessionUpdateCallback = function(callback) {
        this.onSessionUpdate = callback;
    };

    // 將 WebSocketManager 加入命名空間
    window.MCPFeedback.WebSocketManager = WebSocketManager;

    console.log('✅ WebSocketManager 模組載入完成');

})();
