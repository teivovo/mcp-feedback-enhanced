/**
 * MCP Feedback Enhanced - 會話管理模組（重構版）
 * =============================================
 *
 * 整合會話數據管理、UI 渲染和面板控制功能
 * 使用模組化架構提升可維護性
 */

(function() {
    'use strict';

    // 確保命名空間和依賴存在
    window.MCPFeedback = window.MCPFeedback || {};

    // 獲取 DOMUtils 的安全方法
    function getDOMUtils() {
        return window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.DOM;
    }

    /**
     * 會話管理器建構函數（重構版）
     */
    function SessionManager(options) {
        options = options || {};

        // 子模組實例
        this.dataManager = null;
        this.uiRenderer = null;
        this.detailsModal = null;

        // UI 狀態
        this.isLoading = false;

        // 設定管理器引用
        this.settingsManager = options.settingsManager || null;

        // 回調函數
        this.onSessionChange = options.onSessionChange || null;
        this.onSessionSelect = options.onSessionSelect || null;

        // 專案上下文管理
        this.projectContextManager = null;

        this.initializeModules(options);
        this.setupEventListeners();
        this.initializeProjectContext();

        console.log('📋 SessionManager (重構版) 初始化完成');
    }

    /**
     * 初始化子模組
     */
    SessionManager.prototype.initializeModules = function(options) {
        const self = this;

        // 先初始化 UI 渲染器（避免數據管理器回調時 UI 組件尚未準備好）
        this.uiRenderer = new window.MCPFeedback.Session.UIRenderer({
            showFullSessionId: options.showFullSessionId || false,
            enableAnimations: options.enableAnimations !== false
        });

        // 初始化詳情彈窗
        this.detailsModal = new window.MCPFeedback.Session.DetailsModal({
            enableEscapeClose: options.enableEscapeClose !== false,
            enableBackdropClose: options.enableBackdropClose !== false,
            showFullSessionId: options.showFullSessionId || false
        });

        // 初始化防抖處理器
        this.initDebounceHandlers();

        // 最後初始化數據管理器（確保 UI 組件已準備好接收回調）
        this.dataManager = new window.MCPFeedback.Session.DataManager({
            settingsManager: this.settingsManager,
            onSessionChange: function(sessionData) {
                self.handleSessionChange(sessionData);
            },
            onHistoryChange: function(history) {
                self.handleHistoryChange(history);
            },
            onStatsChange: function(stats) {
                self.handleStatsChange(stats);
            },
            onDataChanged: function() {
                self.handleDataChanged();
            }
        });
    };

    /**
     * 初始化防抖處理器
     */
    SessionManager.prototype.initDebounceHandlers = function() {
        // 為會話變更處理添加防抖
        this._debouncedHandleSessionChange = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleSessionChange.bind(this),
            100,
            false
        );

        // 為歷史記錄變更處理添加防抖
        this._debouncedHandleHistoryChange = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleHistoryChange.bind(this),
            150,
            false
        );

        // 為統計資訊變更處理添加防抖
        this._debouncedHandleStatsChange = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleStatsChange.bind(this),
            100,
            false
        );

        // 為資料變更處理添加防抖
        this._debouncedHandleDataChanged = window.MCPFeedback.Utils.DOM.debounce(
            this._originalHandleDataChanged.bind(this),
            200,
            false
        );
    };

    /**
     * 處理會話變更（原始版本，供防抖使用）
     */
    SessionManager.prototype._originalHandleSessionChange = function(sessionData) {
        // 減少重複日誌：只在會話 ID 變化時記錄
        const sessionId = sessionData ? sessionData.session_id : null;
        if (!this._lastSessionId || this._lastSessionId !== sessionId) {
            console.log('📋 處理會話變更:', sessionData);
            this._lastSessionId = sessionId;
        }

        // 更新 UI 渲染
        this.uiRenderer.renderCurrentSession(sessionData);

        // 調用外部回調
        if (this.onSessionChange) {
            this.onSessionChange(sessionData);
        }
    };

    /**
     * 處理會話變更（防抖版本）
     */
    SessionManager.prototype.handleSessionChange = function(sessionData) {
        if (this._debouncedHandleSessionChange) {
            this._debouncedHandleSessionChange(sessionData);
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleSessionChange(sessionData);
        }
    };

    /**
     * 處理歷史記錄變更（原始版本，供防抖使用）
     */
    SessionManager.prototype._originalHandleHistoryChange = function(history) {
        // 減少重複日誌：只在歷史記錄數量變化時記錄
        if (!this._lastHistoryCount || this._lastHistoryCount !== history.length) {
            console.log('📋 處理歷史記錄變更:', history.length, '個會話');
            this._lastHistoryCount = history.length;
        }

        // 更新 UI 渲染
        this.uiRenderer.renderSessionHistory(history);
    };

    /**
     * 處理歷史記錄變更（防抖版本）
     */
    SessionManager.prototype.handleHistoryChange = function(history) {
        if (this._debouncedHandleHistoryChange) {
            this._debouncedHandleHistoryChange(history);
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleHistoryChange(history);
        }
    };

    /**
     * 處理統計資訊變更（原始版本，供防抖使用）
     */
    SessionManager.prototype._originalHandleStatsChange = function(stats) {
        // 減少重複日誌：只在統計資訊有意義變化時記錄
        const statsKey = stats ? JSON.stringify(stats) : null;
        if (!this._lastStatsKey || this._lastStatsKey !== statsKey) {
            console.log('📋 處理統計資訊變更:', stats);
            this._lastStatsKey = statsKey;
        }

        // 更新 UI 渲染
        this.uiRenderer.renderStats(stats);
    };

    /**
     * 處理統計資訊變更（防抖版本）
     */
    SessionManager.prototype.handleStatsChange = function(stats) {
        if (this._debouncedHandleStatsChange) {
            this._debouncedHandleStatsChange(stats);
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleStatsChange(stats);
        }
    };

    /**
     * 處理資料變更（原始版本，供防抖使用）
     */
    SessionManager.prototype._originalHandleDataChanged = function() {
        console.log('📋 處理資料變更，重新渲染所有內容');

        // 重新渲染所有內容
        const currentSession = this.dataManager.getCurrentSession();
        const history = this.dataManager.getSessionHistory();
        const stats = this.dataManager.getStats();

        this.uiRenderer.renderCurrentSession(currentSession);
        this.uiRenderer.renderSessionHistory(history);
        this.uiRenderer.renderStats(stats);
    };

    /**
     * 處理資料變更（防抖版本）
     */
    SessionManager.prototype.handleDataChanged = function() {
        if (this._debouncedHandleDataChanged) {
            this._debouncedHandleDataChanged();
        } else {
            // 回退到原始方法（防抖未初始化時）
            this._originalHandleDataChanged();
        }
    };

    /**
     * 設置事件監聽器
     */
    SessionManager.prototype.setupEventListeners = function() {
        const self = this;
        const DOMUtils = getDOMUtils();



        // 刷新按鈕
        const refreshButton = DOMUtils ?
            DOMUtils.safeQuerySelector('#refreshSessions') :
            document.querySelector('#refreshSessions');
        if (refreshButton) {
            refreshButton.addEventListener('click', function() {
                self.refreshSessionData();
            });
        }

        // 詳細資訊按鈕
        const detailsButton = DOMUtils ?
            DOMUtils.safeQuerySelector('#viewSessionDetails') :
            document.querySelector('#viewSessionDetails');
        if (detailsButton) {
            detailsButton.addEventListener('click', function() {
                self.showSessionDetails();
            });
        }
    };

    /**
     * 更新當前會話（委託給數據管理器）
     */
    SessionManager.prototype.updateCurrentSession = function(sessionData) {
        return this.dataManager.updateCurrentSession(sessionData);
    };

    /**
     * 更新狀態資訊（委託給數據管理器）
     */
    SessionManager.prototype.updateStatusInfo = function(statusInfo) {
        return this.dataManager.updateStatusInfo(statusInfo);
    };












    /**
     * 刷新會話數據
     */
    SessionManager.prototype.refreshSessionData = function() {
        if (this.isLoading) return;

        console.log('📋 刷新會話數據');
        this.isLoading = true;

        const self = this;
        // 這裡可以發送 WebSocket 請求獲取最新數據
        setTimeout(function() {
            self.isLoading = false;
            console.log('📋 會話數據刷新完成');
        }, 1000);
    };

    /**
     * 顯示當前會話詳情
     */
    SessionManager.prototype.showSessionDetails = function() {
        const currentSession = this.dataManager.getCurrentSession();

        if (!currentSession) {
            this.showMessage('目前沒有活躍的會話數據', 'warning');
            return;
        }

        this.detailsModal.showSessionDetails(currentSession);
    };



    /**
     * 查看會話詳情（通過會話ID）
     */
    SessionManager.prototype.viewSessionDetails = function(sessionId) {
        console.log('📋 查看會話詳情:', sessionId);

        const sessionData = this.dataManager.findSessionById(sessionId);

        if (sessionData) {
            this.detailsModal.showSessionDetails(sessionData);
        } else {
            this.showMessage('找不到會話資料', 'error');
        }
    };



    /**
     * 獲取當前會話（便利方法）
     */
    SessionManager.prototype.getCurrentSession = function() {
        return this.dataManager.getCurrentSession();
    };

    /**
     * 獲取會話歷史（便利方法）
     */
    SessionManager.prototype.getSessionHistory = function() {
        return this.dataManager.getSessionHistory();
    };

    /**
     * 獲取統計資訊（便利方法）
     */
    SessionManager.prototype.getStats = function() {
        return this.dataManager.getStats();
    };

    /**
     * 獲取當前會話數據（相容性方法）
     */
    SessionManager.prototype.getCurrentSessionData = function() {
        console.log('📋 嘗試獲取當前會話數據...');

        const currentSession = this.dataManager.getCurrentSession();

        if (currentSession && currentSession.session_id) {
            console.log('📋 從 dataManager 獲取數據:', currentSession.session_id);
            return currentSession;
        }

        // 嘗試從 app 的 WebSocketManager 獲取
        if (window.feedbackApp && window.feedbackApp.webSocketManager) {
            const wsManager = window.feedbackApp.webSocketManager;
            if (wsManager.sessionId) {
                console.log('📋 從 WebSocketManager 獲取數據:', wsManager.sessionId);
                return {
                    session_id: wsManager.sessionId,
                    status: this.getCurrentSessionStatus(),
                    created_at: this.getSessionCreatedTime(),
                    project_directory: this.getProjectDirectory(),
                    summary: this.getAISummary()
                };
            }
        }

        // 嘗試從 app 的 currentSessionId 獲取
        if (window.feedbackApp && window.feedbackApp.currentSessionId) {
            console.log('📋 從 app.currentSessionId 獲取數據:', window.feedbackApp.currentSessionId);
            return {
                session_id: window.feedbackApp.currentSessionId,
                status: this.getCurrentSessionStatus(),
                created_at: this.getSessionCreatedTime(),
                project_directory: this.getProjectDirectory(),
                summary: this.getAISummary()
            };
        }

        console.log('📋 無法獲取會話數據');
        return null;
    };

    /**
     * 獲取會話建立時間
     */
    SessionManager.prototype.getSessionCreatedTime = function() {
        // 嘗試從 WebSocketManager 的連線開始時間獲取
        if (window.feedbackApp && window.feedbackApp.webSocketManager) {
            const wsManager = window.feedbackApp.webSocketManager;
            if (wsManager.connectionStartTime) {
                return wsManager.connectionStartTime / 1000;
            }
        }

        // 嘗試從最後收到的狀態更新中獲取
        if (this.dataManager && this.dataManager.lastStatusUpdate && this.dataManager.lastStatusUpdate.created_at) {
            return this.dataManager.lastStatusUpdate.created_at;
        }

        // 如果都沒有，返回 null
        return null;
    };

    /**
     * 獲取當前會話狀態
     */
    SessionManager.prototype.getCurrentSessionStatus = function() {
        // 嘗試從 UIManager 獲取當前狀態
        if (window.feedbackApp && window.feedbackApp.uiManager) {
            const currentState = window.feedbackApp.uiManager.getFeedbackState();
            if (currentState) {
                // 將內部狀態轉換為會話狀態
                const stateMap = {
                    'waiting_for_feedback': 'waiting',
                    'processing': 'active',
                    'feedback_submitted': 'feedback_submitted'
                };
                return stateMap[currentState] || currentState;
            }
        }

        // 嘗試從最後收到的狀態更新中獲取
        if (this.dataManager && this.dataManager.lastStatusUpdate && this.dataManager.lastStatusUpdate.status) {
            return this.dataManager.lastStatusUpdate.status;
        }

        // 預設狀態
        return 'waiting';
    };

    /**
     * 獲取專案目錄
     */
    SessionManager.prototype.getProjectDirectory = function() {
        const projectElement = document.querySelector('.session-project');
        if (projectElement) {
            return projectElement.textContent.replace('專案: ', '');
        }

        // 從頂部狀態列獲取
        const topProjectInfo = document.querySelector('.project-info');
        if (topProjectInfo) {
            return topProjectInfo.textContent.replace('專案目錄: ', '');
        }

        return '未知';
    };

    /**
     * 獲取 AI 摘要
     */
    SessionManager.prototype.getAISummary = function() {
        const summaryElement = document.querySelector('.session-summary');
        if (summaryElement && summaryElement.textContent !== 'AI 摘要: 載入中...') {
            return summaryElement.textContent.replace('AI 摘要: ', '');
        }

        // 嘗試從主要內容區域獲取
        const mainSummary = document.querySelector('#combinedSummaryContent');
        if (mainSummary && mainSummary.textContent.trim()) {
            return mainSummary.textContent.trim();
        }

        return '暫無摘要';
    };





    /**
     * 更新顯示
     */
    SessionManager.prototype.updateDisplay = function() {
        const currentSession = this.dataManager.getCurrentSession();
        const history = this.dataManager.getSessionHistory();
        const stats = this.dataManager.getStats();

        this.uiRenderer.renderCurrentSession(currentSession);
        this.uiRenderer.renderSessionHistory(history);
        this.uiRenderer.renderStats(stats);
    };

    /**
     * 顯示訊息
     */
    SessionManager.prototype.showMessage = function(message, type) {
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            window.MCPFeedback.Utils.showMessage(message, type);
        } else {
            console.log('📋 ' + message);
        }
    };

    /**
     * 匯出會話歷史
     */
    SessionManager.prototype.exportSessionHistory = function() {
        if (!this.dataManager) {
            console.error('📋 DataManager 未初始化');
            return;
        }

        try {
            const filename = this.dataManager.exportSessionHistory();

            // 顯示成功訊息
            if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                const message = window.i18nManager ?
                    window.i18nManager.t('sessionHistory.management.exportSuccess') :
                    '會話歷史已匯出';
                window.MCPFeedback.Utils.showMessage(message + ': ' + filename, 'success');
            }
        } catch (error) {
            console.error('📋 匯出會話歷史失敗:', error);
            if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                window.MCPFeedback.Utils.showMessage('匯出失敗: ' + error.message, 'error');
            }
        }
    };

    /**
     * 匯出單一會話
     */
    SessionManager.prototype.exportSingleSession = function(sessionId) {
        if (!this.dataManager) {
            console.error('📋 DataManager 未初始化');
            return;
        }

        try {
            const filename = this.dataManager.exportSingleSession(sessionId);
            if (filename) {
                // 顯示成功訊息
                if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                    const message = window.i18nManager ?
                        window.i18nManager.t('sessionHistory.management.exportSuccess') :
                        '會話已匯出';
                    window.MCPFeedback.Utils.showMessage(message + ': ' + filename, 'success');
                }
            }
        } catch (error) {
            console.error('📋 匯出單一會話失敗:', error);
            if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                window.MCPFeedback.Utils.showMessage('匯出失敗: ' + error.message, 'error');
            }
        }
    };

    /**
     * 清空會話歷史
     */
    SessionManager.prototype.clearSessionHistory = function() {
        if (!this.dataManager) {
            console.error('📋 DataManager 未初始化');
            return;
        }

        // 確認對話框
        const confirmMessage = window.i18nManager ?
            window.i18nManager.t('sessionHistory.management.confirmClear') :
            '確定要清空所有會話歷史嗎？';

        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            this.dataManager.clearHistory();

            // 顯示成功訊息
            if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                const message = window.i18nManager ?
                    window.i18nManager.t('sessionHistory.management.clearSuccess') :
                    '會話歷史已清空';
                window.MCPFeedback.Utils.showMessage(message, 'success');
            }
        } catch (error) {
            console.error('📋 清空會話歷史失敗:', error);
            if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                window.MCPFeedback.Utils.showMessage('清空失敗: ' + error.message, 'error');
            }
        }
    };

    /**
     * 清理資源
     */
    SessionManager.prototype.cleanup = function() {
        // 清理子模組
        if (this.dataManager) {
            this.dataManager.cleanup();
            this.dataManager = null;
        }

        if (this.uiRenderer) {
            this.uiRenderer.cleanup();
            this.uiRenderer = null;
        }

        if (this.detailsModal) {
            this.detailsModal.cleanup();
            this.detailsModal = null;
        }



        console.log('📋 SessionManager (重構版) 清理完成');
    };

    /**
     * 初始化專案上下文
     */
    SessionManager.prototype.initializeProjectContext = function() {
        // 創建專案上下文管理器
        this.projectContextManager = new ProjectContextManager();

        // 設置事件監聽器
        this.setupProjectContextEvents();

        // 初始化專案信息
        this.updateProjectContext();

        console.log('📂 專案上下文管理器初始化完成');
    };

    /**
     * 設置專案上下文事件
     */
    SessionManager.prototype.setupProjectContextEvents = function() {
        const projectDetailsBtn = document.getElementById('projectDetailsBtn');
        const projectNameDisplay = document.getElementById('projectNameDisplay');
        const projectPathDisplay = document.getElementById('projectPathDisplay');

        // 專案詳情按鈕
        if (projectDetailsBtn) {
            projectDetailsBtn.addEventListener('click', () => {
                this.showProjectDetails();
            });
        }

        // 專案名稱點擊
        if (projectNameDisplay) {
            projectNameDisplay.addEventListener('click', () => {
                this.showProjectDetails();
            });
        }

        // 專案路徑點擊複製
        if (projectPathDisplay) {
            projectPathDisplay.addEventListener('click', () => {
                this.copyProjectPath();
            });
        }
    };

    /**
     * 更新專案上下文
     */
    SessionManager.prototype.updateProjectContext = function() {
        if (!this.projectContextManager) return;

        const projectData = this.projectContextManager.getCurrentProject();
        this.updateProjectDisplay(projectData);
    };

    /**
     * 更新專案顯示
     */
    SessionManager.prototype.updateProjectDisplay = function(projectData) {
        const projectNameDisplay = document.getElementById('projectNameDisplay');
        const projectIcon = document.getElementById('projectIcon');
        const projectTypeIndicator = document.getElementById('projectTypeIndicator');
        const projectTypeText = document.getElementById('projectTypeText');

        if (projectNameDisplay) {
            projectNameDisplay.textContent = projectData.name || 'Unknown Project';
        }

        if (projectIcon) {
            projectIcon.textContent = this.getProjectIcon(projectData.type);
        }

        if (projectTypeIndicator && projectTypeText) {
            projectTypeIndicator.className = `project-type-indicator ${projectData.type}-project`;
            projectTypeText.textContent = this.getProjectTypeLabel(projectData.type);
        }

        // 更新 agent 上下文（如果有）
        this.updateAgentContext(projectData.agent);
    };

    /**
     * 更新 Agent 上下文
     */
    SessionManager.prototype.updateAgentContext = function(agentInfo) {
        const agentContextIndicator = document.getElementById('agentContextIndicator');
        const agentContextText = document.getElementById('agentContextText');

        if (!agentContextIndicator || !agentContextText) return;

        if (agentInfo && agentInfo.name) {
            agentContextIndicator.style.display = 'flex';
            agentContextIndicator.className = 'agent-context-indicator active';
            agentContextText.textContent = agentInfo.name;
        } else {
            agentContextIndicator.style.display = 'none';
        }
    };

    /**
     * 獲取專案圖標
     */
    SessionManager.prototype.getProjectIcon = function(type) {
        const icons = {
            'web': '🌐',
            'mobile': '📱',
            'desktop': '🖥️',
            'api': '🔌',
            'data': '📊',
            'general': '📂'
        };
        return icons[type] || icons.general;
    };

    /**
     * 獲取專案類型標籤
     */
    SessionManager.prototype.getProjectTypeLabel = function(type) {
        const labels = {
            'web': 'Web',
            'mobile': 'Mobile',
            'desktop': 'Desktop',
            'api': 'API',
            'data': 'Data',
            'general': 'General'
        };
        return labels[type] || labels.general;
    };

    /**
     * 顯示專案詳情
     */
    SessionManager.prototype.showProjectDetails = function() {
        if (!this.projectContextManager) return;

        const projectData = this.projectContextManager.getCurrentProject();
        this.projectContextManager.showProjectDetailsModal(projectData);
    };

    /**
     * 複製專案路徑
     */
    SessionManager.prototype.copyProjectPath = function() {
        const projectPathDisplay = document.getElementById('projectPathDisplay');
        if (!projectPathDisplay) return;

        const fullPath = projectPathDisplay.getAttribute('data-full-path') || projectPathDisplay.textContent;

        if (navigator.clipboard) {
            navigator.clipboard.writeText(fullPath).then(() => {
                console.log('📋 專案路徑已複製到剪貼板');
                this.showCopyFeedback(projectPathDisplay);
            }).catch(err => {
                console.error('❌ 複製失敗:', err);
            });
        } else {
            // 備用方法
            const textArea = document.createElement('textarea');
            textArea.value = fullPath;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            console.log('📋 專案路徑已複製到剪貼板（備用方法）');
            this.showCopyFeedback(projectPathDisplay);
        }
    };

    /**
     * 顯示複製回饋
     */
    SessionManager.prototype.showCopyFeedback = function(element) {
        const originalText = element.textContent;
        element.textContent = '已複製!';
        element.style.color = 'var(--accent-color)';

        setTimeout(() => {
            element.textContent = originalText;
            element.style.color = '';
        }, 1000);
    };

    /**
     * 專案上下文管理器
     */
    function ProjectContextManager() {
        this.currentProject = this.initializeCurrentProject();
        this.projectHistory = this.loadProjectHistory();
    }

    /**
     * 初始化當前專案
     */
    ProjectContextManager.prototype.initializeCurrentProject = function() {
        // 從頁面獲取專案信息
        const projectPathElement = document.getElementById('projectPathDisplay');
        const projectNameElement = document.getElementById('projectNameDisplay');

        const projectPath = projectPathElement ?
            (projectPathElement.getAttribute('data-full-path') || projectPathElement.textContent) : '';
        const projectName = projectNameElement ? projectNameElement.textContent : '';

        const project = {
            name: projectName || this.extractProjectNameFromPath(projectPath),
            path: projectPath,
            type: this.detectProjectType(projectPath),
            agent: this.detectAgentContext(),
            lastAccessed: new Date().toISOString(),
            metadata: this.gatherProjectMetadata(projectPath)
        };

        // 保存到歷史
        this.addToProjectHistory(project);

        return project;
    };

    /**
     * 從路徑提取專案名稱
     */
    ProjectContextManager.prototype.extractProjectNameFromPath = function(path) {
        if (!path) return 'Unknown Project';

        const parts = path.replace(/\\/g, '/').split('/');
        return parts[parts.length - 1] || parts[parts.length - 2] || 'Unknown Project';
    };

    /**
     * 檢測專案類型
     */
    ProjectContextManager.prototype.detectProjectType = function(path) {
        if (!path) return 'general';

        const pathLower = path.toLowerCase();

        // Web 專案指標
        if (pathLower.includes('web') || pathLower.includes('frontend') ||
            pathLower.includes('react') || pathLower.includes('vue') ||
            pathLower.includes('angular') || pathLower.includes('next')) {
            return 'web';
        }

        // Mobile 專案指標
        if (pathLower.includes('mobile') || pathLower.includes('android') ||
            pathLower.includes('ios') || pathLower.includes('flutter') ||
            pathLower.includes('react-native')) {
            return 'mobile';
        }

        // Desktop 專案指標
        if (pathLower.includes('desktop') || pathLower.includes('electron') ||
            pathLower.includes('tauri') || pathLower.includes('wpf')) {
            return 'desktop';
        }

        // API 專案指標
        if (pathLower.includes('api') || pathLower.includes('backend') ||
            pathLower.includes('server') || pathLower.includes('service')) {
            return 'api';
        }

        // Data 專案指標
        if (pathLower.includes('data') || pathLower.includes('analytics') ||
            pathLower.includes('ml') || pathLower.includes('ai')) {
            return 'data';
        }

        return 'general';
    };

    /**
     * 檢測 Agent 上下文
     */
    ProjectContextManager.prototype.detectAgentContext = function() {
        // 這裡可以從 MCP 調用或其他來源獲取 agent 信息
        // 目前返回 null，未來可以擴展
        return null;
    };

    /**
     * 收集專案元數據
     */
    ProjectContextManager.prototype.gatherProjectMetadata = function(path) {
        return {
            detectedAt: new Date().toISOString(),
            userAgent: navigator.userAgent,
            sessionId: this.getCurrentSessionId()
        };
    };

    /**
     * 獲取當前會話 ID
     */
    ProjectContextManager.prototype.getCurrentSessionId = function() {
        const sessionElement = document.getElementById('currentSessionId');
        return sessionElement ? sessionElement.textContent : null;
    };

    /**
     * 載入專案歷史
     */
    ProjectContextManager.prototype.loadProjectHistory = function() {
        try {
            const history = localStorage.getItem('mcp_project_history');
            return history ? JSON.parse(history) : [];
        } catch (e) {
            console.warn('⚠️ 載入專案歷史失敗:', e);
            return [];
        }
    };

    /**
     * 保存專案歷史
     */
    ProjectContextManager.prototype.saveProjectHistory = function() {
        try {
            localStorage.setItem('mcp_project_history', JSON.stringify(this.projectHistory));
        } catch (e) {
            console.warn('⚠️ 保存專案歷史失敗:', e);
        }
    };

    /**
     * 添加到專案歷史
     */
    ProjectContextManager.prototype.addToProjectHistory = function(project) {
        // 移除重複項目
        this.projectHistory = this.projectHistory.filter(p => p.path !== project.path);

        // 添加到開頭
        this.projectHistory.unshift(project);

        // 限制歷史數量
        if (this.projectHistory.length > 10) {
            this.projectHistory = this.projectHistory.slice(0, 10);
        }

        this.saveProjectHistory();
    };

    /**
     * 獲取當前專案
     */
    ProjectContextManager.prototype.getCurrentProject = function() {
        return this.currentProject;
    };

    /**
     * 獲取專案歷史
     */
    ProjectContextManager.prototype.getProjectHistory = function() {
        return this.projectHistory;
    };

    /**
     * 顯示專案詳情模態框
     */
    ProjectContextManager.prototype.showProjectDetailsModal = function(projectData) {
        const modal = this.createProjectDetailsModal(projectData);
        document.body.appendChild(modal);

        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    };

    /**
     * 創建專案詳情模態框
     */
    ProjectContextManager.prototype.createProjectDetailsModal = function(projectData) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container project-details-modal">
                <div class="modal-header">
                    <div class="project-details-header">
                        <span class="project-details-icon">${this.getProjectIcon(projectData.type)}</span>
                        <h3 class="project-details-title">${this.escapeHtml(projectData.name)}</h3>
                    </div>
                    <button type="button" class="modal-close-btn" aria-label="關閉">×</button>
                </div>
                <div class="modal-body">
                    <div class="project-details-content">
                        ${this.renderProjectDetailsContent(projectData)}
                    </div>
                </div>
                <div class="modal-footer">
                    <div class="project-actions">
                        <button type="button" class="project-action-btn" onclick="this.closest('.modal-overlay').remove()">關閉</button>
                        <button type="button" class="project-action-btn primary" onclick="navigator.clipboard.writeText('${projectData.path}')">複製路徑</button>
                    </div>
                </div>
            </div>
        `;

        // 設置事件監聽器
        this.setupProjectDetailsEvents(modal);

        return modal;
    };

    /**
     * 渲染專案詳情內容
     */
    ProjectContextManager.prototype.renderProjectDetailsContent = function(projectData) {
        const history = this.getProjectHistory();

        return `
            <div class="project-detail-section">
                <h4><span class="section-icon">📋</span>基本信息</h4>
                <div class="project-detail-item">
                    <span class="project-detail-label">專案名稱:</span>
                    <span class="project-detail-value">${this.escapeHtml(projectData.name)}</span>
                </div>
                <div class="project-detail-item">
                    <span class="project-detail-label">專案類型:</span>
                    <span class="project-detail-value">${this.getProjectTypeLabel(projectData.type)}</span>
                </div>
                <div class="project-detail-item">
                    <span class="project-detail-label">專案路徑:</span>
                    <span class="project-detail-value clickable" onclick="navigator.clipboard.writeText('${projectData.path}')" title="點擊複製">${this.escapeHtml(projectData.path)}</span>
                </div>
                <div class="project-detail-item">
                    <span class="project-detail-label">最後訪問:</span>
                    <span class="project-detail-value">${this.formatDate(projectData.lastAccessed)}</span>
                </div>
            </div>

            <div class="project-detail-section">
                <h4><span class="section-icon">🕒</span>專案歷史</h4>
                <div class="project-history-list">
                    ${this.renderProjectHistory(history, projectData.path)}
                </div>
            </div>

            ${projectData.agent ? `
            <div class="project-detail-section">
                <h4><span class="section-icon">🤖</span>Agent 上下文</h4>
                <div class="project-detail-item">
                    <span class="project-detail-label">Agent 名稱:</span>
                    <span class="project-detail-value">${this.escapeHtml(projectData.agent.name)}</span>
                </div>
            </div>
            ` : ''}
        `;
    };

    /**
     * 渲染專案歷史
     */
    ProjectContextManager.prototype.renderProjectHistory = function(history, currentPath) {
        if (!history || history.length === 0) {
            return '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">尚無專案歷史</div>';
        }

        return history.map(project => {
            const isCurrent = project.path === currentPath;
            return `
                <div class="project-history-item ${isCurrent ? 'current' : ''}" onclick="this.selectProject('${project.path}')">
                    <span class="project-history-icon">${this.getProjectIcon(project.type)}</span>
                    <div class="project-history-info">
                        <div class="project-history-name">${this.escapeHtml(project.name)}</div>
                        <div class="project-history-path">${this.escapeHtml(project.path)}</div>
                    </div>
                    <div class="project-history-time">${this.formatRelativeTime(project.lastAccessed)}</div>
                </div>
            `;
        }).join('');
    };

    /**
     * 設置專案詳情事件
     */
    ProjectContextManager.prototype.setupProjectDetailsEvents = function(modal) {
        // 關閉按鈕
        const closeBtn = modal.querySelector('.modal-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeProjectDetailsModal(modal);
            });
        }

        // 點擊背景關閉
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeProjectDetailsModal(modal);
            }
        });

        // ESC 鍵關閉
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                this.closeProjectDetailsModal(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        }.bind(this));
    };

    /**
     * 關閉專案詳情模態框
     */
    ProjectContextManager.prototype.closeProjectDetailsModal = function(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    };

    /**
     * 輔助方法
     */
    ProjectContextManager.prototype.getProjectIcon = function(type) {
        const icons = {
            'web': '🌐',
            'mobile': '📱',
            'desktop': '🖥️',
            'api': '🔌',
            'data': '📊',
            'general': '📂'
        };
        return icons[type] || icons.general;
    };

    ProjectContextManager.prototype.getProjectTypeLabel = function(type) {
        const labels = {
            'web': 'Web 應用',
            'mobile': '移動應用',
            'desktop': '桌面應用',
            'api': 'API 服務',
            'data': '數據項目',
            'general': '通用項目'
        };
        return labels[type] || labels.general;
    };

    ProjectContextManager.prototype.escapeHtml = function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    ProjectContextManager.prototype.formatDate = function(dateString) {
        if (!dateString) return '未知';
        try {
            return new Date(dateString).toLocaleString('zh-TW');
        } catch (e) {
            return '未知';
        }
    };

    ProjectContextManager.prototype.formatRelativeTime = function(dateString) {
        if (!dateString) return '未知';
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (days > 0) return `${days}天前`;
            if (hours > 0) return `${hours}小時前`;
            if (minutes > 0) return `${minutes}分鐘前`;
            return '剛剛';
        } catch (e) {
            return '未知';
        }
    };

    // 將 SessionManager 加入命名空間
    window.MCPFeedback.SessionManager = SessionManager;

    // 全域方法供 HTML 調用
    window.MCPFeedback.SessionManager.viewSessionDetails = function(sessionId) {
        console.log('📋 全域查看會話詳情:', sessionId);

        // 找到當前的 SessionManager 實例
        if (window.MCPFeedback && window.MCPFeedback.app && window.MCPFeedback.app.sessionManager) {
            const sessionManager = window.MCPFeedback.app.sessionManager;
            sessionManager.viewSessionDetails(sessionId);
        } else {
            // 如果找不到實例，顯示錯誤訊息
            console.warn('找不到 SessionManager 實例');
            if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
                window.MCPFeedback.Utils.showMessage('會話管理器未初始化', 'error');
            }
        }
    };

    // 全域匯出會話歷史方法
    window.MCPFeedback.SessionManager.exportSessionHistory = function() {
        if (window.MCPFeedback && window.MCPFeedback.app && window.MCPFeedback.app.sessionManager) {
            window.MCPFeedback.app.sessionManager.exportSessionHistory();
        } else {
            console.warn('找不到 SessionManager 實例');
        }
    };

    // 全域匯出單一會話方法
    window.MCPFeedback.SessionManager.exportSingleSession = function(sessionId) {
        if (window.MCPFeedback && window.MCPFeedback.app && window.MCPFeedback.app.sessionManager) {
            window.MCPFeedback.app.sessionManager.exportSingleSession(sessionId);
        } else {
            console.warn('找不到 SessionManager 實例');
        }
    };

    // 全域清空會話歷史方法
    window.MCPFeedback.SessionManager.clearSessionHistory = function() {
        if (window.MCPFeedback && window.MCPFeedback.app && window.MCPFeedback.app.sessionManager) {
            window.MCPFeedback.app.sessionManager.clearSessionHistory();
        } else {
            console.warn('找不到 SessionManager 實例');
        }
    };

    console.log('✅ SessionManager (重構版) 模組載入完成');

})();
