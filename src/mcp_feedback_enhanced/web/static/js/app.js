/**
 * MCP Feedback Enhanced - 主應用程式
 * =================================
 *
 * 模組化重構版本，整合所有功能模組
 * 依賴模組載入順序：utils -> tab-manager -> websocket-manager -> connection-monitor ->
 *                  session-manager -> image-handler -> settings-manager -> ui-manager ->
 *                  auto-refresh-manager -> app
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};

    /**
     * 主應用程式建構函數
     */
    function FeedbackApp(sessionId) {
        // 會話信息
        this.sessionId = sessionId;
        this.currentSessionId = null;

        // 模組管理器
        this.tabManager = null;
        this.webSocketManager = null;
        this.connectionMonitor = null;
        this.sessionManager = null;
        this.imageHandler = null;
        this.settingsManager = null;
        this.uiManager = null;

        // 提示詞管理器
        this.promptManager = null;
        this.promptModal = null;
        this.promptSettingsUI = null;
        this.promptInputButtons = null;

        // 音效管理器
        this.audioManager = null;
        this.audioSettingsUI = null;

        // 自動提交管理器
        this.autoSubmitManager = null;

        // 應用程式狀態
        this.isInitialized = false;
        this.pendingSubmission = null;

        // 初始化防抖函數
        this.initDebounceHandlers();

        console.log('🚀 FeedbackApp 建構函數初始化完成');
    }

    /**
     * 初始化防抖處理器
     */
    FeedbackApp.prototype.initDebounceHandlers = function() {
        // 為自動提交檢查添加防抖
        this._debouncedCheckAndStartAutoSubmit = window.MCPFeedback.Utils.DOM.debounce(
            this._originalCheckAndStartAutoSubmit.bind(this),
            200,
            false
        );

        // 為 WebSocket 訊息處理添加防抖
        this._debouncedHandleWebSocketMessage = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleWebSocketMessage.bind(this),
            50,
            false
        );

        // 為會話更新處理添加防抖
        this._debouncedHandleSessionUpdated = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleSessionUpdated.bind(this),
            100,
            false
        );

        // 為狀態更新處理添加防抖
        this._debouncedHandleStatusUpdate = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleStatusUpdate.bind(this),
            100,
            false
        );
    };

    /**
     * 初始化應用程式
     */
    FeedbackApp.prototype.init = function() {
        const self = this;

        console.log('🚀 初始化 MCP Feedback Enhanced 應用程式');

        return new Promise(function(resolve, reject) {
            try {
                // 等待國際化系統
                self.waitForI18n()
                    .then(function() {
                        return self.initializeManagers();
                    })
                    .then(function() {
                        return self.setupEventListeners();
                    })
                    .then(function() {
                        return self.setupCleanupHandlers();
                    })
                    .then(function() {
                        self.isInitialized = true;
                        console.log('✅ MCP Feedback Enhanced 應用程式初始化完成');
                        resolve();
                    })
                    .catch(function(error) {
                        console.error('❌ 應用程式初始化失敗:', error);
                        reject(error);
                    });
            } catch (error) {
                console.error('❌ 應用程式初始化異常:', error);
                reject(error);
            }
        });
    };

    /**
     * 等待國際化系統載入
     */
    FeedbackApp.prototype.waitForI18n = function() {
        return new Promise(function(resolve) {
            if (window.i18nManager) {
                window.i18nManager.init().then(resolve).catch(resolve);
            } else {
                resolve();
            }
        });
    };

    /**
     * 初始化所有管理器
     */
    FeedbackApp.prototype.initializeManagers = function() {
        const self = this;

        return new Promise(function(resolve, reject) {
            try {
                console.log('🔧 初始化管理器...');

                // 1. 初始化設定管理器
                self.settingsManager = new window.MCPFeedback.SettingsManager({
                    onSettingsChange: function(settings) {
                        self.handleSettingsChange(settings);
                    },
                    onLanguageChange: function(language) {
                        self.handleLanguageChange(language);
                    },
                    onAutoSubmitStateChange: function(enabled, settings) {
                        self.handleAutoSubmitStateChange(enabled, settings);
                    }
                });

                // 2. 載入設定
                self.settingsManager.loadSettings()
                    .then(function(settings) {
                        console.log('📋 設定載入完成:', settings);

                        // 3. 初始化 UI 管理器
                        self.uiManager = new window.MCPFeedback.UIManager({
                            currentTab: settings.activeTab,
                            layoutMode: settings.layoutMode,
                            onTabChange: function(tabName) {
                                self.handleTabChange(tabName);
                            },
                            onLayoutModeChange: function(layoutMode) {
                                self.handleLayoutModeChange(layoutMode);
                            }
                        });

                        // 4. 初始化標籤頁管理器
                        self.tabManager = new window.MCPFeedback.TabManager();

                        // 5. 初始化連線監控器
                        self.connectionMonitor = new window.MCPFeedback.ConnectionMonitor({
                            onStatusChange: function(status, message) {
                                console.log('🔍 連線狀態變更:', status, message);
                            },
                            onQualityChange: function(quality, latency) {
                                console.log('🔍 連線品質變更:', quality, latency + 'ms');
                            }
                        });

                        // 6. 初始化會話管理器
                        self.sessionManager = new window.MCPFeedback.SessionManager({
                            settingsManager: self.settingsManager,
                            onSessionChange: function(sessionData) {
                                console.log('📋 會話變更:', sessionData);
                            },
                            onSessionSelect: function(sessionId) {
                                console.log('📋 會話選擇:', sessionId);
                            }
                        });

                        // 7. 初始化 WebSocket 管理器
                        self.webSocketManager = new window.MCPFeedback.WebSocketManager({
                            tabManager: self.tabManager,
                            connectionMonitor: self.connectionMonitor,
                            onOpen: function() {
                                self.handleWebSocketOpen();
                            },
                            onMessage: function(data) {
                                self.handleWebSocketMessage(data);
                            },
                            onClose: function(event) {
                                self.handleWebSocketClose(event);
                            },
                            onConnectionStatusChange: function(status, text) {
                                self.uiManager.updateConnectionStatus(status, text);
                                // 同時更新連線監控器
                                if (self.connectionMonitor) {
                                    self.connectionMonitor.updateConnectionStatus(status, text);
                                }
                            }
                        });

                        // 8. 初始化圖片處理器
                        self.imageHandler = new window.MCPFeedback.ImageHandler({
                            imageSizeLimit: settings.imageSizeLimit,
                            enableBase64Detail: settings.enableBase64Detail,
                            layoutMode: settings.layoutMode,
                            onSettingsChange: function() {
                                self.saveImageSettings();
                            }
                        });

                        // 9. 初始化提示詞管理器
                        self.initializePromptManagers();

                        // 10. 初始化音效管理器
                        self.initializeAudioManagers();

                        // 11. 初始化自動提交管理器
                        self.initializeAutoSubmitManager();

                        // 12. 初始化 Textarea 高度管理器
                        self.initializeTextareaHeightManager();

                        // 13. 應用設定到 UI
                        self.settingsManager.applyToUI();

                        // 14. 初始化各個管理器
                        self.uiManager.initTabs();
                        self.imageHandler.init();

                        // 15. 檢查並啟動自動提交（如果條件滿足）
                        setTimeout(function() {
                            self.checkAndStartAutoSubmit();
                            // 初始化主頁面自動提交控制項狀態
                            self.initializeMainAutoSubmitControl();
                            // 確保事件監聽器也被設置
                            self.setupMainAutoSubmitControl();
                        }, 1000); // 延遲 1 秒確保所有初始化完成

                        // 16. 播放啟動音效（如果音效已啟用）
                        setTimeout(function() {
                            if (self.audioManager) {
                                self.audioManager.playStartupNotification();
                            }
                        }, 800); // 延遲 800ms 確保所有初始化完成且避免與其他音效衝突

                        // 17. 建立 WebSocket 連接
                        self.webSocketManager.connect();

                        resolve();
                    })
                    .catch(reject);
            } catch (error) {
                reject(error);
            }
        });
    };

    /**
     * 設置事件監聽器
     */
    FeedbackApp.prototype.setupEventListeners = function() {
        const self = this;

        return new Promise(function(resolve) {
            // 提交按鈕事件
            const submitButtons = [
                window.MCPFeedback.Utils.safeQuerySelector('#submitBtn')
            ].filter(function(btn) { return btn !== null; });

            submitButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    self.submitFeedback();
                });
            });

            // 取消按鈕事件 - 已移除取消按鈕，保留 ESC 快捷鍵功能

            // 命令執行事件
            const runCommandBtn = window.MCPFeedback.Utils.safeQuerySelector('#runCommandBtn');
            if (runCommandBtn) {
                runCommandBtn.addEventListener('click', function() {
                    self.runCommand();
                });
            }

            const commandInput = window.MCPFeedback.Utils.safeQuerySelector('#commandInput');
            if (commandInput) {
                commandInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        self.runCommand();
                    }
                });
            }

            // 快捷鍵
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter 提交回饋
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    self.submitFeedback();
                }

                // Ctrl+I 聚焦輸入框
                if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
                    e.preventDefault();
                    self.focusInput();
                }

                // ESC 鍵功能已移除 - 避免意外清空用戶輸入的文字
            });

            // 設置設定管理器的事件監聽器
            self.settingsManager.setupEventListeners();

            // 主頁面自動提交控制項事件將在主初始化完成後設置

            console.log('✅ 事件監聽器設置完成');
            resolve();
        });
    };

    /**
     * 設置清理處理器
     */
    FeedbackApp.prototype.setupCleanupHandlers = function() {
        const self = this;

        return new Promise(function(resolve) {
            window.addEventListener('beforeunload', function() {
                self.cleanup();
            });

            console.log('✅ 清理處理器設置完成');
            resolve();
        });
    };

    /**
     * 處理設定變更
     */
    FeedbackApp.prototype.handleSettingsChange = function(settings) {
        console.log('🔧 處理設定變更:', settings);

        // 更新圖片處理器設定
        if (this.imageHandler) {
            this.imageHandler.updateSettings(settings);
        }



        // 更新 UI 管理器佈局模式
        if (this.uiManager && settings.layoutMode) {
            this.uiManager.applyLayoutMode(settings.layoutMode);
        }
    };

    /**
     * 處理語言變更
     */
    FeedbackApp.prototype.handleLanguageChange = function(language) {
        console.log('🌐 處理語言變更:', language);

        // 更新 UI 顯示
        if (this.uiManager) {
            this.uiManager.updateStatusIndicator();
        }


    };

    /**
     * 處理頁籤變更
     */
    FeedbackApp.prototype.handleTabChange = function(tabName) {
        console.log('📋 處理頁籤變更:', tabName);

        // 重新初始化圖片處理器（確保使用正確的佈局模式元素）
        if (this.imageHandler) {
            const layoutMode = this.settingsManager.get('layoutMode');
            this.imageHandler.reinitialize(layoutMode);
        }

        // 保存當前頁籤設定
        this.settingsManager.set('activeTab', tabName);
    };

    /**
     * 處理佈局模式變更
     */
    FeedbackApp.prototype.handleLayoutModeChange = function(layoutMode) {
        console.log('🎨 處理佈局模式變更:', layoutMode);

        // 重新初始化圖片處理器
        if (this.imageHandler) {
            this.imageHandler.reinitialize(layoutMode);
        }
    };

    /**
     * 保存圖片設定
     */
    FeedbackApp.prototype.saveImageSettings = function() {
        if (this.imageHandler && this.settingsManager) {
            this.settingsManager.setMultiple({
                imageSizeLimit: this.imageHandler.imageSizeLimit,
                enableBase64Detail: this.imageHandler.enableBase64Detail
            });
        }
    };

    /**
     * 初始化提示詞管理器
     */
    FeedbackApp.prototype.initializePromptManagers = function() {
        console.log('📝 初始化提示詞管理器...');

        try {
            // 檢查提示詞模組是否已載入
            if (!window.MCPFeedback.Prompt) {
                console.warn('⚠️ 提示詞模組未載入，跳過初始化');
                return;
            }

            // 1. 初始化提示詞管理器
            this.promptManager = new window.MCPFeedback.Prompt.PromptManager({
                settingsManager: this.settingsManager
            });
            this.promptManager.init();

            // 2. 初始化提示詞彈窗
            this.promptModal = new window.MCPFeedback.Prompt.PromptModal();

            // 3. 初始化設定頁籤 UI
            this.promptSettingsUI = new window.MCPFeedback.Prompt.PromptSettingsUI({
                promptManager: this.promptManager,
                promptModal: this.promptModal,
                settingsManager: this.settingsManager
            });
            this.promptSettingsUI.init('#promptManagementContainer');

            // 4. 初始化輸入按鈕
            this.promptInputButtons = new window.MCPFeedback.Prompt.PromptInputButtons({
                promptManager: this.promptManager,
                promptModal: this.promptModal
            });

            // 初始化輸入按鈕到回饋輸入區域
            const inputContainers = [
                '#combinedFeedbackText'    // 工作區分頁的 textarea
            ];
            this.promptInputButtons.init(inputContainers);

            console.log('✅ 提示詞管理器初始化完成');

        } catch (error) {
            console.error('❌ 提示詞管理器初始化失敗:', error);
        }
    };

    /**
     * 初始化音效管理器
     */
    FeedbackApp.prototype.initializeAudioManagers = function() {
        console.log('🔊 初始化音效管理器...');

        try {
            // 檢查音效模組是否已載入
            if (!window.MCPFeedback.AudioManager) {
                console.warn('⚠️ 音效模組未載入，跳過初始化');
                return;
            }

            // 1. 初始化音效管理器
            this.audioManager = new window.MCPFeedback.AudioManager({
                settingsManager: this.settingsManager,
                onSettingsChange: function(settings) {
                    console.log('🔊 音效設定已變更:', settings);
                }
            });
            this.audioManager.initialize();

            // 2. 初始化音效設定 UI
            this.audioSettingsUI = new window.MCPFeedback.AudioSettingsUI({
                container: document.querySelector('#audioManagementContainer'),
                audioManager: this.audioManager,
                t: window.i18nManager ? window.i18nManager.t.bind(window.i18nManager) : function(key, defaultValue) { return defaultValue || key; }
            });
            this.audioSettingsUI.initialize();

            console.log('✅ 音效管理器初始化完成');

        } catch (error) {
            console.error('❌ 音效管理器初始化失敗:', error);
        }
    };

    /**
     * 初始化 Textarea 高度管理器
     */
    FeedbackApp.prototype.initializeTextareaHeightManager = function() {
        console.log('📏 初始化 Textarea 高度管理器...');

        try {
            // 檢查 TextareaHeightManager 模組是否已載入
            if (!window.MCPFeedback.TextareaHeightManager) {
                console.warn('⚠️ TextareaHeightManager 模組未載入，跳過初始化');
                return;
            }

            // 建立 TextareaHeightManager 實例
            this.textareaHeightManager = new window.MCPFeedback.TextareaHeightManager({
                settingsManager: this.settingsManager,
                debounceDelay: 500 // 500ms 防抖延遲
            });

            // 初始化管理器
            this.textareaHeightManager.initialize();

            // 註冊 combinedFeedbackText textarea
            const success = this.textareaHeightManager.registerTextarea(
                'combinedFeedbackText',
                'combinedFeedbackTextHeight'
            );

            if (success) {
                console.log('✅ combinedFeedbackText 高度管理已啟用');
            } else {
                console.warn('⚠️ combinedFeedbackText 註冊失敗');
            }

            console.log('✅ Textarea 高度管理器初始化完成');

        } catch (error) {
            console.error('❌ Textarea 高度管理器初始化失敗:', error);
        }
    };

    /**
     * 處理 WebSocket 開啟
     */
    FeedbackApp.prototype.handleWebSocketOpen = function() {
        console.log('🔗 WebSocket 連接已開啟');

        // 如果有待處理的提交，處理它
        if (this.pendingSubmission) {
            console.log('🔄 處理待提交的回饋');
            this.submitFeedbackInternal(this.pendingSubmission);
            this.pendingSubmission = null;
        }
    };

    /**
     * 處理 WebSocket 訊息（原始版本，供防抖使用）
     */
    FeedbackApp.prototype._originalHandleWebSocketMessage = function(data) {
        console.log('📨 處理 WebSocket 訊息:', data);

        switch (data.type) {
            case 'command_output':
                this.appendCommandOutput(data.output);
                break;
            case 'command_complete':
                this.appendCommandOutput('\n[命令完成，退出碼: ' + data.exit_code + ']\n');
                this.enableCommandInput();
                break;
            case 'command_error':
                this.appendCommandOutput('\n[錯誤: ' + data.error + ']\n');
                this.enableCommandInput();
                break;
            case 'feedback_received':
                console.log('回饋已收到');
                this.handleFeedbackReceived(data);
                break;
            case 'status_update':
                console.log('狀態更新:', data.status_info);
                this._originalHandleStatusUpdate(data.status_info);
                break;
            case 'session_updated':
                console.log('🔄 收到會話更新訊息:', data.session_info);
                this._originalHandleSessionUpdated(data);
                break;
            case 'desktop_close_request':
                console.log('🖥️ 收到桌面關閉請求');
                this.handleDesktopCloseRequest(data);
                break;
        }
    };

    /**
     * 處理 WebSocket 訊息（防抖版本）
     */
    FeedbackApp.prototype.handleWebSocketMessage = function(data) {
        if (this._debouncedHandleWebSocketMessage) {
            this._debouncedHandleWebSocketMessage(data);
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleWebSocketMessage(data);
        }
    };

    /**
     * 處理 WebSocket 關閉
     */
    FeedbackApp.prototype.handleWebSocketClose = function(event) {
        console.log('🔗 WebSocket 連接已關閉');

        // 如果有待恢復的回饋內容，恢復它
        if (this.pendingFeedbackData) {
            console.log('🔄 WebSocket 斷開，恢復回饋內容');
            this.restoreFeedbackContent();
        }

        // 重置回饋狀態，避免卡在處理狀態
        if (this.uiManager && this.uiManager.getFeedbackState() === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_PROCESSING) {
            console.log('🔄 WebSocket 斷開，重置處理狀態');
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
        }
    };

    /**
     * 處理回饋接收
     */
    FeedbackApp.prototype.handleFeedbackReceived = function(data) {
        // 確認回饋已被 MCP 接收，清空保存的內容
        this.confirmFeedbackReceived();

        // 使用 UI 管理器設置狀態
        this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED);
        this.uiManager.setLastSubmissionTime(Date.now());

        // 顯示成功訊息
        const successMessage = window.i18nManager ? window.i18nManager.t('feedback.submitSuccess') : '回饋提交成功！';
        window.MCPFeedback.Utils.showMessage(data.message || successMessage, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_SUCCESS);

        // 更新 AI 摘要區域顯示「已送出反饋」狀態
        const submittedMessage = window.i18nManager ? window.i18nManager.t('feedback.submittedWaiting') : '已送出反饋，等待下次 MCP 調用...';
        this.updateSummaryStatus(submittedMessage);

        console.log('反饋已提交，頁面保持開啟狀態');
    };

    /**
     * 處理桌面關閉請求
     */
    FeedbackApp.prototype.handleDesktopCloseRequest = function(data) {
        console.log('🖥️ 處理桌面關閉請求:', data.message);

        // 顯示關閉訊息
        const closeMessage = data.message || '正在關閉桌面應用程式...';
        window.MCPFeedback.Utils.showMessage(closeMessage, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_INFO);

        // 檢查是否在 Tauri 環境中
        if (window.__TAURI__) {
            console.log('🖥️ 檢測到 Tauri 環境，關閉桌面視窗');
            try {
                // 使用 Tauri API 關閉視窗
                window.__TAURI__.window.getCurrent().close();
            } catch (error) {
                console.error('關閉 Tauri 視窗失敗:', error);
                // 備用方案：關閉瀏覽器視窗
                window.close();
            }
        } else {
            console.log('🖥️ 非 Tauri 環境，嘗試關閉瀏覽器視窗');
            // 在瀏覽器環境中嘗試關閉視窗
            window.close();
        }
    };

    /**
     * 處理會話更新（原始版本，供防抖使用）
     */
    FeedbackApp.prototype._originalHandleSessionUpdated = function(data) {
        console.log('🔄 處理會話更新:', data);
        console.log('🔍 檢查 action 字段:', data.action);

        // Check if this is a new session creation
        if (data.action === 'new_session_created' || data.type === 'new_session_created') {
            console.log('🆕 檢測到新會話創建，強制重置狀態');

            // 播放音效通知
            if (this.audioManager) {
                this.audioManager.playNotification();
            }

            // 顯示更新通知
            window.MCPFeedback.Utils.showMessage(data.message || '新會話已創建', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_SUCCESS);

            // 更新會話信息
            if (data.session_info) {
                const newSessionId = data.session_info.session_id;
                console.log('📋 新會話 ID:', newSessionId);

                // 更新當前會話 ID
                this.currentSessionId = newSessionId;

                // 更新會話管理器
                if (this.sessionManager) {
                    this.sessionManager.updateCurrentSession(data.session_info);
                }

                // 強制重置回饋狀態為等待新回饋
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, newSessionId);

                // 清空表單
                this.clearFeedback();

                // 檢查並啟動自動提交（如果條件滿足）
                const self = this;
                setTimeout(function() {
                    self.checkAndStartAutoSubmit();
                }, 200);

                // 更新頁面標題
                if (data.session_info.project_directory) {
                    const projectName = data.session_info.project_directory.split(/[/\\]/).pop();
                    document.title = 'MCP Feedback - ' + projectName;
                }

                // 使用局部更新替代整頁刷新
                this.refreshPageContent();
            }

            console.log('✅ 新會話創建處理完成');
            return; // Early return for new session
        }

        // Regular page refresh - protect SUBMITTED state
        console.log('🔄 普通頁面刷新，保護已提交狀態');

        // 播放音效通知
        if (this.audioManager) {
            this.audioManager.playNotification();
        }

        // 顯示更新通知
        window.MCPFeedback.Utils.showMessage(data.message || '會話已更新，正在局部更新內容...', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_SUCCESS);

        // 更新會話信息
        if (data.session_info) {
            const newSessionId = data.session_info.session_id;
            console.log('📋 會話 ID 更新: ' + this.currentSessionId + ' -> ' + newSessionId);

            // 保存舊會話到歷史記錄（在更新當前會話之前）
            if (this.currentSessionId && this.sessionManager && this.currentSessionId !== newSessionId) {
                console.log('📋 嘗試獲取當前會話數據...');
                // 從 SessionManager 獲取當前會話的完整數據
                const currentSessionData = this.sessionManager.getCurrentSessionData();
                console.log('📋 從 currentSession 獲取數據:', this.currentSessionId);

                if (currentSessionData) {
                    // 計算實際持續時間
                    const now = Date.now() / 1000;
                    let duration = 300; // 預設 5 分鐘

                    if (currentSessionData.created_at) {
                        let createdAt = currentSessionData.created_at;
                        // 處理時間戳格式
                        if (createdAt > 1e12) {
                            createdAt = createdAt / 1000;
                        }
                        duration = Math.max(1, Math.round(now - createdAt));
                    }

                    const oldSessionData = {
                        session_id: this.currentSessionId,
                        status: 'completed',
                        created_at: currentSessionData.created_at || (now - duration),
                        completed_at: now,
                        duration: duration,
                        project_directory: currentSessionData.project_directory,
                        summary: currentSessionData.summary
                    };

                    console.log('📋 準備將舊會話加入歷史記錄:', oldSessionData);

                    // 先更新當前會話 ID，再調用 addSessionToHistory
                    this.currentSessionId = newSessionId;

                    // 更新會話管理器的當前會話（這樣 addSessionToHistory 檢查時就不會認為是當前活躍會話）
                    if (this.sessionManager) {
                        this.sessionManager.updateCurrentSession(data.session_info);
                    }

                    // 現在可以安全地將舊會話加入歷史記錄
                    this.sessionManager.dataManager.addSessionToHistory(oldSessionData);
                } else {
                    console.log('⚠️ 無法獲取當前會話數據，跳過歷史記錄保存');
                    // 仍然需要更新當前會話 ID
                    this.currentSessionId = newSessionId;
                    // 更新會話管理器
                    if (this.sessionManager) {
                        this.sessionManager.updateCurrentSession(data.session_info);
                    }
                }
            } else {
                // 沒有舊會話或會話 ID 相同，直接更新
                this.currentSessionId = newSessionId;
                // 更新會話管理器
                if (this.sessionManager) {
                    this.sessionManager.updateCurrentSession(data.session_info);
                }
            }

            // 重置回饋狀態為等待新回饋（但保護已提交狀態）
            const currentState = this.uiManager.getFeedbackState();
            if (currentState !== window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED) {
                // Only reset if NOT in SUBMITTED state
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, newSessionId);
            } else {
                console.log('🔒 保護已提交狀態，不重置');
            }

            // 檢查並啟動自動提交（如果條件滿足）
            const self = this;
            setTimeout(function() {
                self.checkAndStartAutoSubmit();
            }, 200); // 延遲確保狀態更新完成

            // 更新頁面標題
            if (data.session_info.project_directory) {
                const projectName = data.session_info.project_directory.split(/[/\\]/).pop();
                document.title = 'MCP Feedback - ' + projectName;
            }

            // 使用局部更新替代整頁刷新
            this.refreshPageContent();
        } else {
            console.log('⚠️ 會話更新沒有包含會話信息，僅重置狀態');
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
        }

        console.log('✅ 會話更新處理完成');
    };

    /**
     * 處理會話更新（防抖版本）
     */
    FeedbackApp.prototype.handleSessionUpdated = function(data) {
        if (this._debouncedHandleSessionUpdated) {
            this._debouncedHandleSessionUpdated(data);
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleSessionUpdated(data);
        }
    };

    /**
     * 處理狀態更新（原始版本，供防抖使用）
     */
    FeedbackApp.prototype._originalHandleStatusUpdate = function(statusInfo) {
        console.log('處理狀態更新:', statusInfo);

        // 更新 SessionManager 的狀態資訊
        if (this.sessionManager && this.sessionManager.updateStatusInfo) {
            this.sessionManager.updateStatusInfo(statusInfo);
        }

        // 更新頁面標題顯示會話信息
        if (statusInfo.project_directory) {
            const projectName = statusInfo.project_directory.split(/[/\\]/).pop();
            document.title = 'MCP Feedback - ' + projectName;
        }

        // 提取會話 ID
        const sessionId = statusInfo.session_id || this.currentSessionId;

        // 根據狀態更新 UI
        switch (statusInfo.status) {
            case 'feedback_submitted':
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED, sessionId);
                const submittedMessage = window.i18nManager ? window.i18nManager.t('feedback.submittedWaiting') : '已送出反饋，等待下次 MCP 調用...';
                this.updateSummaryStatus(submittedMessage);
                break;

            case 'active':
            case 'waiting':
                // 檢查是否是新會話
                if (sessionId && sessionId !== this.currentSessionId) {
                    this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionId);
                } else if (this.uiManager.getFeedbackState() !== window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED) {
                    this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionId);
                }

                if (statusInfo.status === 'waiting') {
                    const waitingMessage = window.i18nManager ? window.i18nManager.t('feedback.waitingForUser') : '等待用戶回饋...';
                    this.updateSummaryStatus(waitingMessage);

                    // 檢查並啟動自動提交（如果條件滿足）
                    const self = this;
                    setTimeout(function() {
                        self.checkAndStartAutoSubmit();
                    }, 100); // 短暫延遲確保狀態更新完成
                }
                break;
        }
    };

    /**
     * 處理狀態更新（防抖版本）
     */
    FeedbackApp.prototype.handleStatusUpdate = function(statusInfo) {
        if (this._debouncedHandleStatusUpdate) {
            this._debouncedHandleStatusUpdate(statusInfo);
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleStatusUpdate(statusInfo);
        }
    };

    /**
     * 提交回饋
     */
    FeedbackApp.prototype.submitFeedback = function() {
        console.log('📤 嘗試提交回饋...');

        // 檢查是否可以提交回饋
        if (!this.canSubmitFeedback()) {
            console.log('⚠️ 無法提交回饋');
            this.handleSubmitError();
            return;
        }

        // 收集回饋數據並提交
        const feedbackData = this.collectFeedbackData();
        if (!feedbackData) {
            return;
        }

        this.submitFeedbackInternal(feedbackData);
    };

    /**
     * 檢查是否可以提交回饋
     */
    FeedbackApp.prototype.canSubmitFeedback = function() {
        return this.webSocketManager &&
               this.webSocketManager.isReady() &&
               this.uiManager &&
               this.uiManager.getFeedbackState() === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING;
    };

    /**
     * 處理提交錯誤
     */
    FeedbackApp.prototype.handleSubmitError = function() {
        const feedbackState = this.uiManager ? this.uiManager.getFeedbackState() : null;

        if (feedbackState === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_SUBMITTED) {
            const submittedWarning = window.i18nManager ? window.i18nManager.t('feedback.alreadySubmitted') : '回饋已提交，請等待下次 MCP 調用';
            window.MCPFeedback.Utils.showMessage(submittedWarning, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        } else if (feedbackState === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_PROCESSING) {
            const processingWarning = window.i18nManager ? window.i18nManager.t('feedback.processingFeedback') : '正在處理中，請稍候';
            window.MCPFeedback.Utils.showMessage(processingWarning, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        } else if (!this.webSocketManager || !this.webSocketManager.isReady()) {
            // 收集回饋數據，等待連接就緒後提交
            const feedbackData = this.collectFeedbackData();
            if (feedbackData) {
                this.pendingSubmission = feedbackData;
                const connectingMessage = window.i18nManager ? window.i18nManager.t('feedback.connectingMessage') : 'WebSocket 連接中，回饋將在連接就緒後自動提交...';
                window.MCPFeedback.Utils.showMessage(connectingMessage, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_INFO);
            }
        } else {
            const invalidStateMessage = window.i18nManager ? window.i18nManager.t('feedback.invalidState') : '當前狀態不允許提交';
            window.MCPFeedback.Utils.showMessage(invalidStateMessage + ': ' + feedbackState, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        }
    };

    /**
     * 收集回饋數據
     */
    FeedbackApp.prototype.collectFeedbackData = function() {
        // 獲取合併模式的回饋內容
        let feedback = '';
        const combinedFeedbackInput = window.MCPFeedback.Utils.safeQuerySelector('#combinedFeedbackText');
        feedback = combinedFeedbackInput ? combinedFeedbackInput.value.trim() : '';

        const images = this.imageHandler ? this.imageHandler.getImages() : [];

        if (!feedback && images.length === 0) {
            window.MCPFeedback.Utils.showMessage('請提供回饋文字或上傳圖片', window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
            return null;
        }

        return {
            feedback: feedback,
            images: images,
            settings: {
                image_size_limit: this.imageHandler ? this.imageHandler.imageSizeLimit : 0,
                enable_base64_detail: this.imageHandler ? this.imageHandler.enableBase64Detail : false
            }
        };
    };

    /**
     * 內部提交回饋方法
     */
    FeedbackApp.prototype.submitFeedbackInternal = function(feedbackData) {
        console.log('📤 內部提交回饋...');

        try {
            // 1. 首先記錄用戶訊息到會話歷史（立即保存到伺服器）
            this.recordUserMessage(feedbackData);

            // 2. 設置處理狀態
            if (this.uiManager) {
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_PROCESSING);
            }

            // 3. 發送回饋到 AI 助手
            const success = this.webSocketManager.send({
                type: 'submit_feedback',
                feedback: feedbackData.feedback,
                images: feedbackData.images,
                settings: feedbackData.settings
            });

            if (success) {
                // 保存當前回饋內容以備錯誤時恢復
                this.saveFeedbackForRecovery(feedbackData);

                // 不立即清空表單，等待 MCP 確認
                console.log('📤 回饋已發送，等待 MCP 確認...');

                // 設置超時處理，如果長時間沒有回應則恢復表單
                this.setFeedbackRecoveryTimeout();
            } else {
                throw new Error('WebSocket 發送失敗');
            }

        } catch (error) {
            console.error('❌ 發送回饋失敗:', error);
            const sendFailedMessage = window.i18nManager ? window.i18nManager.t('feedback.sendFailed') : '發送失敗，請重試';
            window.MCPFeedback.Utils.showMessage(sendFailedMessage, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_ERROR);

            // 恢復到等待狀態
            if (this.uiManager) {
                this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
            }
        }
    };

    /**
     * 記錄用戶訊息到會話歷史
     */
    FeedbackApp.prototype.recordUserMessage = function(feedbackData) {
        console.log('📝 記錄用戶訊息到會話歷史...');

        try {
            // 檢查是否有會話管理器
            if (!this.sessionManager || !this.sessionManager.dataManager) {
                console.warn('📝 會話管理器未初始化，跳過用戶訊息記錄');
                return;
            }

            // 判斷提交方式
            const submissionMethod = this.autoSubmitManager && this.autoSubmitManager.isEnabled ? 'auto' : 'manual';

            // 建立訊息記錄資料
            const messageData = {
                content: feedbackData.feedback || '',
                images: feedbackData.images || [],
                submission_method: submissionMethod
            };

            // 記錄到會話歷史
            const success = this.sessionManager.dataManager.addUserMessage(messageData);

            if (success) {
                console.log('📝 用戶訊息已記錄到會話歷史');
            } else {
                console.log('📝 用戶訊息記錄被跳過（可能因隱私設定或其他原因）');
            }

        } catch (error) {
            console.error('❌ 記錄用戶訊息失敗:', error);
            // 不影響主要功能，只記錄錯誤
        }
    };

    /**
     * 清空回饋內容
     */
    FeedbackApp.prototype.clearFeedback = function() {
        console.log('🧹 清空回饋內容...');

        // 使用 UI 管理器重置表單
        if (this.uiManager) {
            this.uiManager.resetFeedbackForm();
        }

        // 清空圖片數據
        if (this.imageHandler) {
            this.imageHandler.clearImages();
        }

        console.log('✅ 回饋內容清空完成');
    };

    /**
     * 取消回饋
     */
    FeedbackApp.prototype.cancelFeedback = function() {
        console.log('❌ 取消回饋');
        this.clearFeedback();
    };

    /**
     * 聚焦到輸入框 (Ctrl+I 快捷鍵)
     */
    FeedbackApp.prototype.focusInput = function() {
        console.log('🎯 執行聚焦輸入框...');

        // 聚焦到合併模式的輸入框
        const targetInput = window.MCPFeedback.Utils.safeQuerySelector('#combinedFeedbackText');

        // 確保在工作區分頁
        if (this.uiManager && this.uiManager.getCurrentTab() !== 'combined') {
            this.uiManager.switchTab('combined');
        }

        if (targetInput) {
            // 聚焦並滾動到可見區域
            targetInput.focus();
            targetInput.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            console.log('✅ 已聚焦到輸入框');
        } else {
            console.warn('⚠️ 未找到目標輸入框');
        }
    };

    /**
     * 執行命令
     */
    FeedbackApp.prototype.runCommand = function() {
        const commandInput = window.MCPFeedback.Utils.safeQuerySelector('#commandInput');
        const command = commandInput ? commandInput.value.trim() : '';

        if (!command) {
            const emptyCommandMessage = window.i18nManager ? window.i18nManager.t('commands.emptyCommand') : '請輸入命令';
            this.appendCommandOutput('⚠️ ' + emptyCommandMessage + '\n');
            return;
        }

        if (!this.webSocketManager || !this.webSocketManager.isConnected) {
            const notConnectedMessage = window.i18nManager ? window.i18nManager.t('commands.notConnected') : 'WebSocket 未連接，無法執行命令';
            this.appendCommandOutput('❌ ' + notConnectedMessage + '\n');
            return;
        }

        // 顯示執行的命令
        this.appendCommandOutput('$ ' + command + '\n');

        // 發送命令
        try {
            const success = this.webSocketManager.send({
                type: 'run_command',
                command: command
            });

            if (success) {
                // 清空輸入框
                commandInput.value = '';
                const executingMessage = window.i18nManager ? window.i18nManager.t('commands.executing') : '正在執行...';
                this.appendCommandOutput('[' + executingMessage + ']\n');
            } else {
                const sendFailedMessage = window.i18nManager ? window.i18nManager.t('commands.sendFailed') : '發送命令失敗';
                this.appendCommandOutput('❌ ' + sendFailedMessage + '\n');
            }

        } catch (error) {
            const sendFailedMessage = window.i18nManager ? window.i18nManager.t('commands.sendFailed') : '發送命令失敗';
            this.appendCommandOutput('❌ ' + sendFailedMessage + ': ' + error.message + '\n');
        }
    };

    /**
     * 添加命令輸出
     */
    FeedbackApp.prototype.appendCommandOutput = function(output) {
        const commandOutput = window.MCPFeedback.Utils.safeQuerySelector('#commandOutput');
        if (commandOutput) {
            commandOutput.textContent += output;
            commandOutput.scrollTop = commandOutput.scrollHeight;
        }
    };

    /**
     * 啟用命令輸入
     */
    FeedbackApp.prototype.enableCommandInput = function() {
        const commandInput = window.MCPFeedback.Utils.safeQuerySelector('#commandInput');
        const runCommandBtn = window.MCPFeedback.Utils.safeQuerySelector('#runCommandBtn');

        if (commandInput) commandInput.disabled = false;
        if (runCommandBtn) {
            runCommandBtn.disabled = false;
            runCommandBtn.textContent = '▶️ 執行';
        }
    };

    /**
     * 更新摘要狀態
     */
    FeedbackApp.prototype.updateSummaryStatus = function(message) {
        const summaryElements = document.querySelectorAll('.ai-summary-content');
        summaryElements.forEach(function(element) {
            element.innerHTML = '<div style="padding: 16px; background: var(--success-color); color: white; border-radius: 6px; text-align: center;">✅ ' + message + '</div>';
        });
    };

    /**
     * 處理會話更新（來自自動刷新）
     */
    FeedbackApp.prototype.handleSessionUpdate = function(sessionData) {
        console.log('🔄 處理自動檢測到的會話更新:', sessionData);

        // 更新當前會話 ID
        this.currentSessionId = sessionData.session_id;

        // 重置回饋狀態
        if (this.uiManager) {
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionData.session_id);
        }

        // 局部更新頁面內容
        this.refreshPageContent();
    };

    /**
     * 刷新頁面內容
     */
    FeedbackApp.prototype.refreshPageContent = function() {
        console.log('🔄 局部更新頁面內容...');

        const self = this;

        fetch('/api/current-session')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('API 請求失敗: ' + response.status);
                }
                return response.json();
            })
            .then(function(sessionData) {
                console.log('📥 獲取到最新會話資料:', sessionData);

                // 重置回饋狀態
                if (sessionData.session_id && self.uiManager) {
                    self.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING, sessionData.session_id);
                }

                // 更新 AI 摘要內容
                if (self.uiManager) {
                    // console.log('🔧 準備更新 AI 摘要內容，summary 長度:', sessionData.summary ? sessionData.summary.length : 'undefined');
                    self.uiManager.updateAISummaryContent(sessionData.summary);
                    self.uiManager.resetFeedbackForm();
                    self.uiManager.updateStatusIndicator();
                }

                // 更新頁面標題
                if (sessionData.project_directory) {
                    const projectName = sessionData.project_directory.split(/[/\\]/).pop();
                    document.title = 'MCP Feedback - ' + projectName;
                }

                console.log('✅ 局部更新完成');
            })
            .catch(function(error) {
                console.error('❌ 局部更新失敗:', error);
                const updateFailedMessage = window.i18nManager ? window.i18nManager.t('app.updateFailed') : '更新內容失敗，請手動刷新頁面以查看新的 AI 工作摘要';
                window.MCPFeedback.Utils.showMessage(updateFailedMessage, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
            });
    };

    /**
     * 初始化自動提交管理器
     */
    FeedbackApp.prototype.initializeAutoSubmitManager = function() {
        console.log('⏰ 初始化自動提交管理器...');

        try {
            const self = this;

            // 創建自動提交管理器
            this.autoSubmitManager = {
                countdown: null,
                isEnabled: false,
                currentPromptId: null,

                // 啟動自動提交
                start: function(timeoutSeconds, promptId) {
                    this.stop(); // 先停止現有的倒數計時

                    this.isEnabled = true;
                    this.currentPromptId = promptId;

                    // 顯示倒數計時器
                    self.showCountdownDisplay();

                    // 創建倒數計時器
                    this.countdown = window.MCPFeedback.Utils.Time.createAutoSubmitCountdown(
                        timeoutSeconds,
                        function(remainingTime, isCompleted) {
                            // 更新倒數計時顯示
                            self.updateCountdownDisplay(remainingTime);
                            // 更新主頁面倒數計時顯示
                            self.updateMainPageCountdown(remainingTime);
                        },
                        function() {
                            // 時間到，自動提交
                            self.performAutoSubmit();
                        }
                    );

                    this.countdown.start();
                    console.log('⏰ 自動提交倒數計時已啟動:', timeoutSeconds + '秒');
                },

                // 停止自動提交
                stop: function() {
                    if (this.countdown) {
                        this.countdown.stop();
                        this.countdown = null;
                    }

                    this.isEnabled = false;
                    this.currentPromptId = null;

                    // 隱藏倒數計時器
                    self.hideCountdownDisplay();

                    console.log('⏸️ 自動提交倒數計時已停止');
                }
            };

            console.log('✅ 自動提交管理器初始化完成');

        } catch (error) {
            console.error('❌ 自動提交管理器初始化失敗:', error);
        }
    };

    /**
     * 檢查並啟動自動提交（原始版本，供防抖使用）
     */
    FeedbackApp.prototype._originalCheckAndStartAutoSubmit = function() {
        // 減少重複日誌：只在首次檢查或條件變化時記錄
        if (!this._lastAutoSubmitCheck || Date.now() - this._lastAutoSubmitCheck > 1000) {
            console.log('🔍 檢查自動提交條件...');
            this._lastAutoSubmitCheck = Date.now();
        }

        if (!this.autoSubmitManager || !this.settingsManager || !this.promptManager) {
            console.log('⚠️ 自動提交管理器、設定管理器或提示詞管理器未初始化');
            return;
        }

        // 檢查自動提交是否已啟用
        const autoSubmitEnabled = this.settingsManager.get('autoSubmitEnabled');
        const autoSubmitPromptId = this.settingsManager.get('autoSubmitPromptId');
        const autoSubmitTimeout = this.settingsManager.get('autoSubmitTimeout');

        console.log('🔍 自動提交設定檢查:', {
            enabled: autoSubmitEnabled,
            promptId: autoSubmitPromptId,
            timeout: autoSubmitTimeout
        });

        // 雙重檢查：設定中的 promptId 和提示詞的 isAutoSubmit 狀態
        let validAutoSubmitPrompt = null;
        if (autoSubmitPromptId) {
            const prompt = this.promptManager.getPromptById(autoSubmitPromptId);
            if (prompt && prompt.isAutoSubmit) {
                validAutoSubmitPrompt = prompt;
            } else {
                console.log('⚠️ 自動提交提示詞驗證失敗:', {
                    promptExists: !!prompt,
                    isAutoSubmit: prompt ? prompt.isAutoSubmit : false,
                    reason: !prompt ? '提示詞不存在' : '提示詞未標記為自動提交'
                });
                // 只清空無效的 promptId，保留用戶的 autoSubmitEnabled 設定
                // 這樣避免因為提示詞問題而強制關閉用戶的自動提交偏好
                this.settingsManager.set('autoSubmitPromptId', null);
                console.log('🔧 已清空無效的 autoSubmitPromptId，保留 autoSubmitEnabled 設定:', autoSubmitEnabled);
            }
        }

        // 檢查當前狀態是否為等待回饋
        const currentState = this.uiManager ? this.uiManager.getFeedbackState() : null;
        const isWaitingForFeedback = currentState === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING;

        console.log('🔍 當前回饋狀態:', currentState, '是否等待回饋:', isWaitingForFeedback);

        // 如果所有條件都滿足，啟動自動提交
        if (autoSubmitEnabled && validAutoSubmitPrompt && autoSubmitTimeout && isWaitingForFeedback) {
            console.log('✅ 自動提交條件滿足，啟動倒數計時器');
            this.autoSubmitManager.start(autoSubmitTimeout, autoSubmitPromptId);
            this.updateAutoSubmitStatus('enabled', autoSubmitTimeout);
        } else {
            console.log('❌ 自動提交條件不滿足，停止倒數計時器');
            this.autoSubmitManager.stop();
            this.updateAutoSubmitStatus('disabled');
        }
    };

    /**
     * 檢查並啟動自動提交（防抖版本）
     */
    FeedbackApp.prototype.checkAndStartAutoSubmit = function() {
        if (this._debouncedCheckAndStartAutoSubmit) {
            this._debouncedCheckAndStartAutoSubmit();
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalCheckAndStartAutoSubmit();
        }
    };

    /**
     * 處理自動提交狀態變更
     */
    FeedbackApp.prototype.handleAutoSubmitStateChange = function(enabled, settings) {
        console.log('⏰ 處理自動提交狀態變更:', enabled, settings);

        if (!this.autoSubmitManager) {
            console.warn('⚠️ 自動提交管理器未初始化');
            return;
        }

        if (enabled && settings.promptId && settings.timeout) {
            // 檢查當前狀態是否適合啟動自動提交
            const currentState = this.uiManager ? this.uiManager.getFeedbackState() : null;
            const isWaitingForFeedback = currentState === window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING;

            if (isWaitingForFeedback) {
                // 啟動自動提交
                this.autoSubmitManager.start(settings.timeout, settings.promptId);
                this.updateAutoSubmitStatus('enabled', settings.timeout);
                console.log('⏰ 自動提交已啟動（設定變更觸發）');
            } else {
                // 只更新狀態顯示，不啟動倒數計時器
                this.updateAutoSubmitStatus('enabled', settings.timeout);
                console.log('⏰ 自動提交設定已啟用，等待適當時機啟動');
            }
        } else {
            // 停止自動提交
            this.autoSubmitManager.stop();
            this.updateAutoSubmitStatus('disabled');
            console.log('⏸️ 自動提交已停用（設定變更觸發）');
        }
    };

    /**
     * 執行自動提交
     */
    FeedbackApp.prototype.performAutoSubmit = function() {
        console.log('⏰ 執行自動提交...');

        if (!this.autoSubmitManager || !this.promptManager || !this.settingsManager) {
            console.error('❌ 自動提交管理器、提示詞管理器或設定管理器未初始化');
            this.autoSubmitManager && this.autoSubmitManager.stop();
            return;
        }

        const promptId = this.autoSubmitManager.currentPromptId;
        const autoSubmitPromptId = this.settingsManager.get('autoSubmitPromptId');

        // 雙重檢查：確保 promptId 有效且與設定一致
        if (!promptId || !autoSubmitPromptId || promptId !== autoSubmitPromptId) {
            console.error('❌ 自動提交提示詞 ID 不一致或為空:', {
                currentPromptId: promptId,
                settingsPromptId: autoSubmitPromptId
            });
            this.pauseAutoSubmit('提示詞 ID 不一致');
            return;
        }

        const prompt = this.promptManager.getPromptById(promptId);

        if (!prompt) {
            console.error('❌ 找不到自動提交提示詞:', promptId);
            this.pauseAutoSubmit('找不到指定的提示詞');
            return;
        }

        // 檢查提示詞的 isAutoSubmit 狀態
        if (!prompt.isAutoSubmit) {
            console.error('❌ 提示詞不是自動提交狀態:', prompt.name);
            this.pauseAutoSubmit('提示詞不是自動提交狀態');
            return;
        }

        // 設定提示詞內容到回饋輸入框
        const feedbackInput = window.MCPFeedback.Utils.safeQuerySelector('#combinedFeedbackText');
        if (feedbackInput) {
            feedbackInput.value = prompt.content;
        }

        // 顯示自動提交訊息
        const message = window.i18nManager ?
            window.i18nManager.t('autoSubmit.executing', '正在執行自動提交...') :
            '正在執行自動提交...';
        window.MCPFeedback.Utils.showMessage(message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_INFO);

        // 執行提交
        this.submitFeedback();

        // 更新提示詞使用記錄
        this.promptManager.usePrompt(promptId);

        // 停止自動提交
        this.autoSubmitManager.stop();
    };

    /**
     * 暫停自動提交功能（當檢查失敗時）
     */
    FeedbackApp.prototype.pauseAutoSubmit = function(reason) {
        console.error('⏸️ 暫停自動提交功能，原因:', reason);

        // 停止倒數計時器
        if (this.autoSubmitManager) {
            this.autoSubmitManager.stop();
        }

        // 清空自動提交設定
        if (this.settingsManager) {
            this.settingsManager.set('autoSubmitEnabled', false);
            this.settingsManager.set('autoSubmitPromptId', null);
        }

        // 清空所有提示詞的自動提交標記
        if (this.promptManager) {
            this.promptManager.clearAutoSubmitPrompt();
        }

        // 更新 UI 狀態
        this.updateAutoSubmitStatus('disabled');

        // 顯示錯誤訊息
        const message = window.i18nManager ?
            window.i18nManager.t('autoSubmit.paused', '自動提交已暫停：') + reason :
            '自動提交已暫停：' + reason;
        window.MCPFeedback.Utils.showMessage(message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_ERROR);
    };

    /**
     * 顯示倒數計時器
     */
    FeedbackApp.prototype.showCountdownDisplay = function() {
        const countdownDisplay = document.getElementById('countdownDisplay');

        if (countdownDisplay) {
            countdownDisplay.style.display = 'flex';
        }
    };

    /**
     * 隱藏倒數計時器
     */
    FeedbackApp.prototype.hideCountdownDisplay = function() {
        const countdownDisplay = document.getElementById('countdownDisplay');

        if (countdownDisplay) {
            countdownDisplay.style.display = 'none';
        }
    };

    /**
     * 更新倒數計時顯示
     */
    FeedbackApp.prototype.updateCountdownDisplay = function(remainingSeconds) {
        const countdownTimer = document.getElementById('countdownTimer');

        const formattedTime = window.MCPFeedback.Utils.Time.formatAutoSubmitCountdown(remainingSeconds);

        // 更新倒數計時器
        if (countdownTimer) {
            countdownTimer.textContent = formattedTime;

            // 根據剩餘時間調整樣式
            countdownTimer.className = 'countdown-timer';
            if (remainingSeconds <= 10) {
                countdownTimer.classList.add('danger');
            } else if (remainingSeconds <= 30) {
                countdownTimer.classList.add('warning');
            }
        }
    };

    /**
     * 更新自動提交狀態顯示
     */
    FeedbackApp.prototype.updateAutoSubmitStatus = function(status, timeout) {
        // 更新設定頁面的狀態按鈕
        const statusElement = document.getElementById('autoSubmitStatus');
        if (statusElement) {
            const statusIcon = statusElement.querySelector('span:first-child');
            const statusText = statusElement.querySelector('.button-text');

            if (status === 'enabled') {
                // 直接設定 HTML 內容，就像提示詞按鈕一樣
                if (statusIcon) statusIcon.innerHTML = '⏰';
                if (statusText) {
                    const enabledText = window.i18nManager ?
                        window.i18nManager.t('autoSubmit.enabled', '已啟用') :
                        '已啟用';
                    statusText.textContent = `${enabledText} (${timeout}秒)`;
                }
                statusElement.className = 'auto-submit-status-btn enabled';
            } else {
                // 直接設定 HTML 內容，就像提示詞按鈕一樣
                if (statusIcon) statusIcon.innerHTML = '⏸️';
                if (statusText) {
                    const disabledText = window.i18nManager ?
                        window.i18nManager.t('autoSubmit.disabled', '已停用') :
                        '已停用';
                    statusText.textContent = disabledText;
                }
                statusElement.className = 'auto-submit-status-btn disabled';
            }
        }

        // 更新主頁面的自動提交控制項
        const promptId = this.settingsManager ? this.settingsManager.get('autoSubmitPromptId') : null;
        this.updateMainAutoSubmitControl(status, timeout, promptId);
    };

    /**
     * 設置主頁面自動提交控制項
     */
    FeedbackApp.prototype.setupMainAutoSubmitControl = function() {
        console.log('🔧 開始設置主頁面自動提交控制項...');
        const self = this;
        const autoSubmitBtn = document.getElementById('autoSubmitBtn');

        if (!autoSubmitBtn) {
            console.warn('⚠️ 主頁面自動提交按鈕未找到');
            return;
        }

        console.log('✅ 找到主頁面自動提交按鈕');

        // 設置按鈕點擊事件
        autoSubmitBtn.addEventListener('click', function() {
            console.log('🔄 主頁面自動提交按鈕被點擊');

            if (this.classList.contains('active')) {
                // 目前是啟用狀態，點擊後停用
                self.disableMainAutoSubmit();
            } else {
                // 目前是停用狀態，點擊後顯示模板選擇
                self.showAutoSubmitTemplateDropdown();
            }
        });

        console.log('✅ 主頁面自動提交控制項設置完成');
    };

    /**
     * 顯示增強的模板選擇器模態框
     */
    FeedbackApp.prototype.showAutoSubmitTemplateDropdown = function() {
        this.showEnhancedTemplateSelector();
    };

    /**
     * 顯示增強的模板選擇器
     */
    FeedbackApp.prototype.showEnhancedTemplateSelector = function() {
        const self = this;

        // 創建模態框
        const modal = this.createTemplateSelector();
        document.body.appendChild(modal);

        // 顯示模態框
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // 聚焦搜索框
        const searchInput = modal.querySelector('.template-search-input');
        if (searchInput) {
            setTimeout(() => searchInput.focus(), 300);
        }
    };

    /**
     * 創建模板選擇器模態框
     */
    FeedbackApp.prototype.createTemplateSelector = function() {
        const self = this;
        const prompts = this.promptManager ? this.promptManager.getAllPrompts() : [];

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container template-selector-modal">
                <div class="modal-header">
                    <h3 class="modal-title">📝 選擇自動提交模板</h3>
                    <button type="button" class="modal-close-btn" aria-label="關閉">×</button>
                </div>
                <div class="modal-body">
                    <div class="template-search-container">
                        <span class="template-search-icon">🔍</span>
                        <input type="text" class="template-search-input" placeholder="搜索模板..." />
                    </div>
                    <div class="template-grid" id="templateGrid">
                        ${this.renderTemplateCards(prompts)}
                    </div>
                </div>
                <div class="modal-footer template-selector-footer">
                    <div class="template-selection-info">
                        <span id="selectedTemplateInfo">請選擇一個模板</span>
                    </div>
                    <div class="template-footer-actions">
                        <button type="button" class="btn btn-secondary" id="templateCancelBtn">取消</button>
                        <button type="button" class="btn btn-primary" id="templateConfirmBtn" disabled>確認選擇</button>
                    </div>
                </div>
            </div>
        `;

        // 設置事件監聽器
        this.setupTemplateSelectorEvents(modal);

        return modal;
    };

    /**
     * 渲染模板卡片
     */
    FeedbackApp.prototype.renderTemplateCards = function(prompts) {
        if (!prompts || prompts.length === 0) {
            return `
                <div class="template-empty-state">
                    <div class="template-empty-icon">📝</div>
                    <div>尚無可用模板</div>
                    <div style="font-size: 12px; margin-top: 8px;">請先在設定中創建模板</div>
                </div>
            `;
        }

        return prompts.map(prompt => {
            const preview = prompt.content.length > 100
                ? prompt.content.substring(0, 100) + '...'
                : prompt.content;

            return `
                <div class="template-card" data-template-id="${prompt.id}">
                    <div class="template-card-header">
                        <h4 class="template-name">${this.escapeHtml(prompt.name)}</h4>
                        ${prompt.isAutoSubmit ? '<span class="template-auto-submit-badge">自動提交</span>' : ''}
                    </div>
                    <div class="template-content-preview">${this.escapeHtml(preview)}</div>
                    <div class="template-meta">
                        <span>長度: ${prompt.content.length} 字符</span>
                        <span>創建: ${this.formatDate(prompt.createdAt)}</span>
                    </div>
                    <div class="template-actions">
                        <button class="template-preview-btn" data-action="preview">預覽</button>
                    </div>
                </div>
            `;
        }).join('');
    };

    /**
     * 設置模板選擇器事件
     */
    FeedbackApp.prototype.setupTemplateSelectorEvents = function(modal) {
        const self = this;
        let selectedTemplateId = null;

        // 關閉按鈕
        const closeBtn = modal.querySelector('.modal-close-btn');
        const cancelBtn = modal.querySelector('#templateCancelBtn');

        [closeBtn, cancelBtn].forEach(btn => {
            if (btn) {
                btn.addEventListener('click', () => {
                    self.closeTemplateSelector(modal);
                });
            }
        });

        // 點擊背景關閉
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                self.closeTemplateSelector(modal);
            }
        });

        // ESC 鍵關閉
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                self.closeTemplateSelector(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        });

        // 搜索功能
        const searchInput = modal.querySelector('.template-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                self.filterTemplates(modal, e.target.value);
            });
        }

        // 模板卡片選擇
        const templateGrid = modal.querySelector('#templateGrid');
        if (templateGrid) {
            templateGrid.addEventListener('click', (e) => {
                const card = e.target.closest('.template-card');
                if (card) {
                    // 處理預覽按鈕
                    if (e.target.classList.contains('template-preview-btn')) {
                        self.previewTemplate(card.dataset.templateId);
                        return;
                    }

                    // 選擇模板
                    self.selectTemplateCard(modal, card);
                    selectedTemplateId = card.dataset.templateId;
                }
            });
        }

        // 確認按鈕
        const confirmBtn = modal.querySelector('#templateConfirmBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                if (selectedTemplateId) {
                    self.enableMainAutoSubmit(selectedTemplateId);
                    self.closeTemplateSelector(modal);
                }
            });
        }
    };

    /**
     * 關閉模板選擇器
     */
    FeedbackApp.prototype.closeTemplateSelector = function(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    };

    /**
     * 選擇模板卡片
     */
    FeedbackApp.prototype.selectTemplateCard = function(modal, card) {
        // 移除其他選中狀態
        const allCards = modal.querySelectorAll('.template-card');
        allCards.forEach(c => c.classList.remove('selected'));

        // 選中當前卡片
        card.classList.add('selected');

        // 更新選擇信息
        const templateName = card.querySelector('.template-name').textContent;
        const infoElement = modal.querySelector('#selectedTemplateInfo');
        if (infoElement) {
            infoElement.textContent = `已選擇: ${templateName}`;
        }

        // 啟用確認按鈕
        const confirmBtn = modal.querySelector('#templateConfirmBtn');
        if (confirmBtn) {
            confirmBtn.disabled = false;
        }
    };

    /**
     * 過濾模板
     */
    FeedbackApp.prototype.filterTemplates = function(modal, searchTerm) {
        const cards = modal.querySelectorAll('.template-card');
        const searchLower = searchTerm.toLowerCase();

        cards.forEach(card => {
            const name = card.querySelector('.template-name').textContent.toLowerCase();
            const content = card.querySelector('.template-content-preview').textContent.toLowerCase();

            if (name.includes(searchLower) || content.includes(searchLower)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    };

    /**
     * 預覽模板
     */
    FeedbackApp.prototype.previewTemplate = function(templateId) {
        if (!this.promptManager) return;

        const prompt = this.promptManager.getPrompt(templateId);
        if (!prompt) return;

        // 創建預覽模態框
        const previewModal = document.createElement('div');
        previewModal.className = 'modal-overlay';
        previewModal.innerHTML = `
            <div class="modal-container" style="max-width: 600px;">
                <div class="modal-header">
                    <h3 class="modal-title">📖 模板預覽: ${this.escapeHtml(prompt.name)}</h3>
                    <button type="button" class="modal-close-btn" aria-label="關閉">×</button>
                </div>
                <div class="modal-body">
                    <div style="background: var(--bg-tertiary); padding: 16px; border-radius: 8px; border: 1px solid var(--border-color);">
                        <pre style="white-space: pre-wrap; margin: 0; font-family: inherit; line-height: 1.5;">${this.escapeHtml(prompt.content)}</pre>
                    </div>
                    <div style="margin-top: 12px; font-size: 12px; color: var(--text-secondary);">
                        長度: ${prompt.content.length} 字符 | 創建時間: ${this.formatDate(prompt.createdAt)}
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">關閉</button>
                </div>
            </div>
        `;

        // 關閉事件
        const closeBtn = previewModal.querySelector('.modal-close-btn');
        closeBtn.addEventListener('click', () => {
            previewModal.remove();
        });

        previewModal.addEventListener('click', (e) => {
            if (e.target === previewModal) {
                previewModal.remove();
            }
        });

        document.body.appendChild(previewModal);
        setTimeout(() => previewModal.classList.add('show'), 10);
    };

    /**
     * 格式化日期
     */
    FeedbackApp.prototype.formatDate = function(dateString) {
        if (!dateString) return '未知';

        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-TW', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } catch (e) {
            return '未知';
        }
    };

    /**
     * HTML 轉義
     */
    FeedbackApp.prototype.escapeHtml = function(text) {
        if (!text) return '';

        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    /**
     * 啟用主頁面自動提交
     */
    FeedbackApp.prototype.enableMainAutoSubmit = function(promptId) {
        const autoSubmitBtn = document.getElementById('autoSubmitBtn');
        if (autoSubmitBtn) {
            autoSubmitBtn.classList.add('active');
            autoSubmitBtn.textContent = 'Auto-Submit: ON';
        }

        // 設置提示詞的自動提交標記
        if (this.promptManager && this.promptManager.setAutoSubmitPrompt) {
            this.promptManager.setAutoSubmitPrompt(promptId);
        }

        // 觸發狀態變更事件（這會同步到設定頁面）
        if (this.settingsManager.triggerAutoSubmitStateChange) {
            this.settingsManager.triggerAutoSubmitStateChange(true);
        }

        console.log('✅ 主頁面自動提交已啟用，模板ID:', promptId);
    };

    /**
     * 停用主頁面自動提交
     */
    FeedbackApp.prototype.disableMainAutoSubmit = function() {
        const autoSubmitBtn = document.getElementById('autoSubmitBtn');
        if (autoSubmitBtn) {
            autoSubmitBtn.classList.remove('active');
            autoSubmitBtn.textContent = 'Auto-Submit';
        }

        // 停止倒數計時
        this.stopAutoSubmitCountdown();

        // 清除提示詞的自動提交標記
        if (this.promptManager && this.promptManager.clearAutoSubmitPrompt) {
            this.promptManager.clearAutoSubmitPrompt();
        }

        // 觸發狀態變更事件（這會同步到設定頁面）
        if (this.settingsManager.triggerAutoSubmitStateChange) {
            this.settingsManager.triggerAutoSubmitStateChange(false);
        }

        console.log('✅ 主頁面自動提交已停用');
    };

    /**
     * 更新主頁面自動提交控制項狀態
     */
    FeedbackApp.prototype.updateMainAutoSubmitControl = function(status, timeout, promptId) {
        // 嘗試找到頭部控制項
        const headerToggle = document.getElementById('autoSubmitHeaderToggle');
        const headerTemplateSelect = document.getElementById('autoSubmitHeaderTemplateSelect');

        // 備用：原來的控制項
        const autoSubmitCheckbox = document.getElementById('autoSubmitCheckbox');
        const autoSubmitDropdownContainer = document.getElementById('autoSubmitDropdownContainer');
        const autoSubmitTemplateSelect = document.getElementById('autoSubmitTemplateSelect');

        // 倒數計時顯示
        const countdownDisplay = document.getElementById('countdownDisplay');
        const countdownTimer = document.getElementById('countdownTimer');

        // 使用頭部控制項或備用控制項
        const toggleElement = headerToggle || autoSubmitCheckbox;
        const templateSelectElement = headerTemplateSelect || autoSubmitTemplateSelect;

        if (!toggleElement) return;

        if (status === 'enabled' && promptId) {
            // 啟用狀態
            toggleElement.checked = true;

            // 顯示模板選擇器
            if (headerTemplateSelect) {
                headerTemplateSelect.style.display = 'inline-block';
            } else if (autoSubmitDropdownContainer) {
                autoSubmitDropdownContainer.style.display = 'flex';
            }

            // 設置選中的模板
            if (templateSelectElement) {
                this.populateAutoSubmitTemplates();
                templateSelectElement.value = promptId;
            }

            // 顯示倒數計時
            if (countdownDisplay && countdownTimer && timeout) {
                countdownTimer.textContent = `${timeout}s`;
                countdownDisplay.style.display = 'flex';
            }
        } else {
            // 停用狀態
            toggleElement.checked = false;

            // 隱藏模板選擇器
            if (headerTemplateSelect) {
                headerTemplateSelect.style.display = 'none';
            } else if (autoSubmitDropdownContainer) {
                autoSubmitDropdownContainer.style.display = 'none';
            }

            // 隱藏倒數計時
            if (countdownDisplay) {
                countdownDisplay.style.display = 'none';
            }
        }
    };

    /**
     * 填充自動提交模板選項
     */
    FeedbackApp.prototype.populateAutoSubmitTemplates = function() {
        // 嘗試找到頭部模板選擇器
        const headerTemplateSelect = document.getElementById('autoSubmitHeaderTemplateSelect');
        // 備用：原來的模板選擇器
        const autoSubmitTemplateSelect = document.getElementById('autoSubmitTemplateSelect');

        const templateSelect = headerTemplateSelect || autoSubmitTemplateSelect;

        if (!templateSelect || !this.promptManager) return;

        // 清空現有選項
        templateSelect.innerHTML = '<option value="">Select template...</option>';

        // 獲取所有提示詞
        const prompts = this.promptManager.getAllPrompts();

        prompts.forEach(prompt => {
            const option = document.createElement('option');
            option.value = prompt.id;
            option.textContent = prompt.name;
            templateSelect.appendChild(option);
        });

        console.log('🔄 自動提交模板選項已更新');
    };

    /**
     * 啟用自動提交並設置模板
     */
    FeedbackApp.prototype.enableAutoSubmitWithTemplate = function(promptId) {
        if (!this.settingsManager || !this.promptManager) {
            console.error('❌ 設定管理器或提示詞管理器未初始化');
            return;
        }

        try {
            // 獲取當前超時設定
            const currentTimeout = this.settingsManager.get('autoSubmitTimeout') || 30;

            // 設置自動提交設定
            this.settingsManager.set('autoSubmitEnabled', true);
            this.settingsManager.set('autoSubmitPromptId', promptId);
            this.settingsManager.set('autoSubmitTimeout', currentTimeout);

            // 設置提示詞的自動提交標記
            if (this.promptManager && this.promptManager.setAutoSubmitPrompt) {
                this.promptManager.setAutoSubmitPrompt(promptId);
            }

            // 觸發狀態變更事件（這會同步到設定頁面）
            if (this.settingsManager.triggerAutoSubmitStateChange) {
                this.settingsManager.triggerAutoSubmitStateChange(true);
            }

            // 更新主頁面控制項狀態
            this.updateMainAutoSubmitControl('enabled', currentTimeout, promptId);

            // 檢查並啟動自動提交（如果條件滿足）
            this.checkAndStartAutoSubmit();

            console.log('✅ 自動提交已啟用，模板:', promptId);

            // 顯示成功訊息
            const message = window.i18nManager ?
                window.i18nManager.t('autoSubmit.enabled', 'Auto Submit enabled') :
                'Auto Submit enabled';
            window.MCPFeedback.Utils.showMessage(message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_SUCCESS);

        } catch (error) {
            console.error('❌ 啟用自動提交失敗:', error);

            // 重置控制項狀態
            const autoSubmitCheckbox = document.getElementById('autoSubmitCheckbox');
            const autoSubmitDropdownContainer = document.getElementById('autoSubmitDropdownContainer');
            if (autoSubmitCheckbox) autoSubmitCheckbox.checked = false;
            if (autoSubmitDropdownContainer) autoSubmitDropdownContainer.style.display = 'none';

            // 顯示錯誤訊息
            window.MCPFeedback.Utils.showMessage(error.message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_ERROR);
        }
    };

    /**
     * 停用自動提交
     */
    FeedbackApp.prototype.disableAutoSubmit = function() {
        if (!this.settingsManager) {
            console.error('❌ 設定管理器未初始化');
            return;
        }

        try {
            // 停止自動提交
            if (this.autoSubmitManager) {
                this.autoSubmitManager.stop();
            }

            // 清除設定
            this.settingsManager.set('autoSubmitEnabled', false);
            this.settingsManager.set('autoSubmitPromptId', null);

            // 清除提示詞的自動提交標記
            if (this.promptManager && this.promptManager.clearAutoSubmitPrompt) {
                this.promptManager.clearAutoSubmitPrompt();
            }

            // 觸發狀態變更事件（這會同步到設定頁面）
            if (this.settingsManager.triggerAutoSubmitStateChange) {
                this.settingsManager.triggerAutoSubmitStateChange(false);
            }

            // 更新主頁面控制項狀態
            this.updateMainAutoSubmitControl('disabled');

            console.log('⏸️ 自動提交已停用');

            // 顯示訊息
            const message = window.i18nManager ?
                window.i18nManager.t('autoSubmit.disabled', 'Auto Submit disabled') :
                'Auto Submit disabled';
            window.MCPFeedback.Utils.showMessage(message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_INFO);

        } catch (error) {
            console.error('❌ 停用自動提交失敗:', error);
            window.MCPFeedback.Utils.showMessage(error.message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_ERROR);
        }
    };

    /**
     * 初始化主頁面自動提交控制項狀態
     */
    FeedbackApp.prototype.initializeMainAutoSubmitControl = function() {
        if (!this.settingsManager) {
            console.log('⚠️ 設定管理器未初始化，跳過主頁面自動提交控制項初始化');
            return;
        }

        const autoSubmitEnabled = this.settingsManager.get('autoSubmitEnabled');
        const autoSubmitPromptId = this.settingsManager.get('autoSubmitPromptId');
        const autoSubmitTimeout = this.settingsManager.get('autoSubmitTimeout') || 30;

        if (autoSubmitEnabled && autoSubmitPromptId) {
            this.updateMainAutoSubmitControl('enabled', autoSubmitTimeout, autoSubmitPromptId);
        } else {
            this.updateMainAutoSubmitControl('disabled');
        }

        console.log('✅ 主頁面自動提交控制項狀態初始化完成');
    };

    /**
     * 更新主頁面倒數計時顯示
     */
    FeedbackApp.prototype.updateMainPageCountdown = function(remainingTime) {
        // 更新頭部倒數計時顯示
        const countdownTimer = document.getElementById('countdownTimer');
        if (countdownTimer && remainingTime > 0) {
            countdownTimer.textContent = `${remainingTime}s`;
        }

        // 備用：更新原來的倒數計時顯示
        const autoSubmitCountdownText = document.getElementById('autoSubmitCountdownText');
        if (autoSubmitCountdownText && remainingTime > 0) {
            autoSubmitCountdownText.textContent = `Auto-Submit: ${remainingTime}s`;
        }
    };

    /**
     * 保存回饋內容以備錯誤時恢復
     */
    FeedbackApp.prototype.saveFeedbackForRecovery = function(feedbackData) {
        this.pendingFeedbackData = {
            feedback: feedbackData.feedback,
            images: feedbackData.images,
            timestamp: Date.now()
        };
        console.log('💾 已保存回饋內容以備恢復');
    };

    /**
     * 設置回饋恢復超時處理
     */
    FeedbackApp.prototype.setFeedbackRecoveryTimeout = function() {
        const self = this;

        // 清除之前的超時
        if (this.feedbackRecoveryTimeout) {
            clearTimeout(this.feedbackRecoveryTimeout);
        }

        // 設置 30 秒超時
        this.feedbackRecoveryTimeout = setTimeout(function() {
            console.warn('⚠️ MCP 回應超時，恢復回饋內容');
            self.restoreFeedbackContent();

            // 顯示警告訊息
            const message = window.i18nManager ?
                window.i18nManager.t('feedback.responseTimeout', 'MCP response timeout, feedback content restored') :
                'MCP response timeout, feedback content restored';
            window.MCPFeedback.Utils.showMessage(message, window.MCPFeedback.Utils.CONSTANTS.MESSAGE_WARNING);
        }, 30000); // 30 秒超時
    };

    /**
     * 恢復回饋內容
     */
    FeedbackApp.prototype.restoreFeedbackContent = function() {
        if (!this.pendingFeedbackData) {
            console.log('ℹ️ 沒有待恢復的回饋內容');
            return;
        }

        const feedbackInput = window.MCPFeedback.Utils.safeQuerySelector('#combinedFeedbackText');
        if (feedbackInput && this.pendingFeedbackData.feedback) {
            feedbackInput.value = this.pendingFeedbackData.feedback;
            feedbackInput.disabled = false;
        }

        // 恢復圖片（如果有的話）
        if (this.imageHandler && this.pendingFeedbackData.images && this.pendingFeedbackData.images.length > 0) {
            // 這裡可以添加圖片恢復邏輯，但由於圖片處理較複雜，暫時跳過
            console.log('ℹ️ 檢測到圖片數據，但圖片恢復功能暫未實現');
        }

        // 重新啟用提交按鈕
        const submitButtons = [
            window.MCPFeedback.Utils.safeQuerySelector('#submitBtn')
        ].filter(function(btn) { return btn !== null; });

        submitButtons.forEach(function(button) {
            button.disabled = false;
            const defaultText = window.i18nManager ? window.i18nManager.t('buttons.submit') : '提交回饋';
            button.textContent = button.getAttribute('data-original-text') || defaultText;
        });

        // 重置回饋狀態
        if (this.uiManager) {
            this.uiManager.setFeedbackState(window.MCPFeedback.Utils.CONSTANTS.FEEDBACK_WAITING);
        }

        console.log('🔄 回饋內容已恢復');
    };

    /**
     * 確認回饋已被 MCP 接收，清空保存的內容
     */
    FeedbackApp.prototype.confirmFeedbackReceived = function() {
        // 清除超時處理
        if (this.feedbackRecoveryTimeout) {
            clearTimeout(this.feedbackRecoveryTimeout);
            this.feedbackRecoveryTimeout = null;
        }

        // 清除保存的回饋數據
        this.pendingFeedbackData = null;

        // 現在可以安全地清空表單
        this.clearFeedback();

        console.log('✅ MCP 已確認接收回饋，表單已清空');
    };

    /**
     * 清理資源
     */
    FeedbackApp.prototype.cleanup = function() {
        console.log('🧹 清理應用程式資源...');

        if (this.autoSubmitManager) {
            this.autoSubmitManager.stop();
        }

        if (this.tabManager) {
            this.tabManager.cleanup();
        }

        if (this.webSocketManager) {
            this.webSocketManager.close();
        }

        if (this.connectionMonitor) {
            this.connectionMonitor.cleanup();
        }

        if (this.sessionManager) {
            this.sessionManager.cleanup();
        }

        if (this.imageHandler) {
            this.imageHandler.cleanup();
        }

        if (this.textareaHeightManager) {
            this.textareaHeightManager.destroy();
        }

        console.log('✅ 應用程式資源清理完成');
    };

    // 將 FeedbackApp 加入命名空間
    window.MCPFeedback.FeedbackApp = FeedbackApp;

    console.log('✅ FeedbackApp 主模組載入完成');

})();