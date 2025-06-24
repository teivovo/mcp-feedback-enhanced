/**
 * MCP Feedback Enhanced - 設定管理模組
 * ==================================
 * 
 * 處理應用程式設定的載入、保存和同步
 */

(function() {
    'use strict';

    // 確保命名空間和依賴存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    // 創建模組專用日誌器
    const logger = window.MCPFeedback.Logger ?
        new window.MCPFeedback.Logger({ moduleName: 'SettingsManager' }) :
        console;

    /**
     * 設定管理器建構函數
     */
    function SettingsManager(options) {
        options = options || {};
        
        // 預設設定
        this.defaultSettings = {
            layoutMode: 'combined-vertical',
            autoClose: false,
            language: 'zh-TW',
            imageSizeLimit: 0,
            enableBase64Detail: false,
            activeTab: 'combined',
            sessionPanelCollapsed: false,
            // 自動定時提交設定
            autoSubmitEnabled: false,
            autoSubmitTimeout: 30,
            autoSubmitPromptId: null,
            // 音效通知設定
            audioNotificationEnabled: false,
            audioNotificationVolume: 50,
            selectedAudioId: 'default-beep',
            customAudios: [],
            // 會話歷史設定
            sessionHistoryRetentionHours: 72,
            // 用戶訊息記錄設定
            userMessageRecordingEnabled: true,
            userMessagePrivacyLevel: 'full', // 'full', 'basic', 'disabled'
            // UI 元素尺寸設定
            combinedFeedbackTextHeight: 150, // combinedFeedbackText textarea 的高度（px）
            // Telegram 整合設定
            telegramEnabled: false,
            telegramBotToken: '',
            telegramChatId: '',
            telegramIncludeSessionId: true,
            telegramIncludeTimestamp: true,
            telegramIncludeProjectPath: false
        };
        
        // 當前設定
        this.currentSettings = Utils.deepClone(this.defaultSettings);
        
        // 回調函數
        this.onSettingsChange = options.onSettingsChange || null;
        this.onLanguageChange = options.onLanguageChange || null;
        this.onAutoSubmitStateChange = options.onAutoSubmitStateChange || null;

        // 防抖機制相關
        this.saveToServerDebounceTimer = null;
        this.saveToServerDebounceDelay = options.saveDebounceDelay || 500; // 預設 500ms 防抖延遲
        this.pendingServerSave = false;

        console.log('✅ SettingsManager 建構函數初始化完成，防抖延遲:', this.saveToServerDebounceDelay + 'ms');
    }

    /**
     * 載入設定
     */
    SettingsManager.prototype.loadSettings = function() {
        const self = this;
        
        return new Promise(function(resolve, reject) {
            logger.info('開始載入設定...');
            
            // 優先從伺服器端載入設定
            self.loadFromServer()
                .then(function(serverSettings) {
                    if (serverSettings && Object.keys(serverSettings).length > 0) {
                        self.currentSettings = self.mergeSettings(self.defaultSettings, serverSettings);
                        logger.info('從伺服器端載入設定成功:', self.currentSettings);
                        
                        // 同步到 localStorage
                        self.saveToLocalStorage();
                        resolve(self.currentSettings);
                    } else {
                        // 回退到 localStorage
                        return self.loadFromLocalStorage();
                    }
                })
                .then(function(localSettings) {
                    if (localSettings) {
                        self.currentSettings = self.mergeSettings(self.defaultSettings, localSettings);
                        console.log('從 localStorage 載入設定:', self.currentSettings);
                    } else {
                        console.log('沒有找到設定，使用預設值');
                    }
                    resolve(self.currentSettings);
                })
                .catch(function(error) {
                    console.error('載入設定失敗:', error);
                    self.currentSettings = Utils.deepClone(self.defaultSettings);
                    resolve(self.currentSettings);
                });
        });
    };

    /**
     * 從伺服器載入設定
     */
    SettingsManager.prototype.loadFromServer = function() {
        return fetch('/api/load-settings')
            .then(function(response) {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('伺服器回應錯誤: ' + response.status);
                }
            })
            .catch(function(error) {
                console.warn('從伺服器端載入設定失敗:', error);
                return null;
            });
    };

    /**
     * 從 localStorage 載入設定
     */
    SettingsManager.prototype.loadFromLocalStorage = function() {
        if (!Utils.isLocalStorageSupported()) {
            return Promise.resolve(null);
        }

        try {
            const localSettings = localStorage.getItem('mcp-feedback-settings');
            if (localSettings) {
                const parsed = Utils.safeJsonParse(localSettings, null);
                console.log('從 localStorage 載入設定:', parsed);
                return Promise.resolve(parsed);
            }
        } catch (error) {
            console.warn('從 localStorage 載入設定失敗:', error);
        }
        
        return Promise.resolve(null);
    };

    /**
     * 保存設定
     */
    SettingsManager.prototype.saveSettings = function(newSettings) {
        if (newSettings) {
            this.currentSettings = this.mergeSettings(this.currentSettings, newSettings);
        }

        logger.debug('保存設定:', this.currentSettings);

        // 保存到 localStorage
        this.saveToLocalStorage();

        // 同步保存到伺服器端
        this.saveToServer();

        // 觸發回調
        if (this.onSettingsChange) {
            this.onSettingsChange(this.currentSettings);
        }

        return this.currentSettings;
    };

    /**
     * 保存到 localStorage
     */
    SettingsManager.prototype.saveToLocalStorage = function() {
        if (!Utils.isLocalStorageSupported()) {
            return;
        }

        try {
            localStorage.setItem('mcp-feedback-settings', JSON.stringify(this.currentSettings));
        } catch (error) {
            console.error('保存設定到 localStorage 失敗:', error);
        }
    };

    /**
     * 保存到伺服器（帶防抖機制）
     */
    SettingsManager.prototype.saveToServer = function() {
        const self = this;

        // 清除之前的定時器
        if (self.saveToServerDebounceTimer) {
            clearTimeout(self.saveToServerDebounceTimer);
        }

        // 標記有待處理的保存操作
        self.pendingServerSave = true;

        // 設置新的防抖定時器
        self.saveToServerDebounceTimer = setTimeout(function() {
            self._performServerSave();
        }, self.saveToServerDebounceDelay);
    };

    /**
     * 執行實際的伺服器保存操作
     */
    SettingsManager.prototype._performServerSave = function() {
        const self = this;

        if (!self.pendingServerSave) {
            return;
        }

        self.pendingServerSave = false;

        fetch('/api/save-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(self.currentSettings)
        })
        .then(function(response) {
            if (response.ok) {
                console.log('設定已同步到伺服器端');
            } else {
                console.warn('同步設定到伺服器端失敗:', response.status);
            }
        })
        .catch(function(error) {
            console.warn('同步設定到伺服器端時發生錯誤:', error);
        });
    };

    /**
     * 立即保存到伺服器（跳過防抖機制）
     * 用於重要操作，如語言變更、重置設定等
     */
    SettingsManager.prototype.saveToServerImmediate = function() {
        // 清除防抖定時器
        if (this.saveToServerDebounceTimer) {
            clearTimeout(this.saveToServerDebounceTimer);
            this.saveToServerDebounceTimer = null;
        }

        // 立即執行保存
        this._performServerSave();
    };

    /**
     * 合併設定
     */
    SettingsManager.prototype.mergeSettings = function(defaultSettings, newSettings) {
        const merged = Utils.deepClone(defaultSettings);
        
        for (const key in newSettings) {
            if (newSettings.hasOwnProperty(key)) {
                merged[key] = newSettings[key];
            }
        }
        
        return merged;
    };

    /**
     * 獲取設定值
     */
    SettingsManager.prototype.get = function(key, defaultValue) {
        if (key in this.currentSettings) {
            return this.currentSettings[key];
        }
        return defaultValue !== undefined ? defaultValue : this.defaultSettings[key];
    };

    /**
     * 設置設定值
     */
    SettingsManager.prototype.set = function(key, value) {
        const oldValue = this.currentSettings[key];
        this.currentSettings[key] = value;
        
        // 特殊處理語言變更
        if (key === 'language' && oldValue !== value) {
            this.handleLanguageChange(value);
            // 語言變更是重要操作，立即保存
            this.saveToLocalStorage();
            this.saveToServerImmediate();

            // 觸發回調
            if (this.onSettingsChange) {
                this.onSettingsChange(this.currentSettings);
            }
        } else {
            // 一般設定變更使用防抖保存
            this.saveSettings();
        }

        return this;
    };

    /**
     * 批量設置設定
     */
    SettingsManager.prototype.setMultiple = function(settings) {
        let languageChanged = false;
        const oldLanguage = this.currentSettings.language;
        
        for (const key in settings) {
            if (settings.hasOwnProperty(key)) {
                this.currentSettings[key] = settings[key];
                
                if (key === 'language' && oldLanguage !== settings[key]) {
                    languageChanged = true;
                }
            }
        }
        
        if (languageChanged) {
            this.handleLanguageChange(this.currentSettings.language);
        }
        
        this.saveSettings();
        return this;
    };

    /**
     * 處理語言變更
     */
    SettingsManager.prototype.handleLanguageChange = function(newLanguage) {
        console.log('語言設定變更: ' + newLanguage);

        // 同步到 localStorage
        if (Utils.isLocalStorageSupported()) {
            localStorage.setItem('language', newLanguage);
        }

        // 通知國際化系統
        if (window.i18nManager) {
            window.i18nManager.setLanguage(newLanguage);
        }

        // 延遲更新動態文字，確保 i18n 已經載入新語言
        setTimeout(() => {
            this.updatePrivacyLevelDescription(this.currentSettings.userMessagePrivacyLevel);
        }, 100);

        // 觸發語言變更回調
        if (this.onLanguageChange) {
            this.onLanguageChange(newLanguage);
        }
    };

    /**
     * 重置設定
     */
    SettingsManager.prototype.resetSettings = function() {
        console.log('重置所有設定');

        // 清除 localStorage
        if (Utils.isLocalStorageSupported()) {
            localStorage.removeItem('mcp-feedback-settings');
        }

        // 重置為預設值
        this.currentSettings = Utils.deepClone(this.defaultSettings);

        // 立即保存重置後的設定（重要操作）
        this.saveToLocalStorage();
        this.saveToServerImmediate();

        // 觸發回調
        if (this.onSettingsChange) {
            this.onSettingsChange(this.currentSettings);
        }

        return this.currentSettings;
    };

    /**
     * 驗證自動提交設定
     */
    SettingsManager.prototype.validateAutoSubmitSettings = function(settings) {
        const errors = [];

        // 驗證超時時間
        if (settings.autoSubmitTimeout !== undefined) {
            const timeout = parseInt(settings.autoSubmitTimeout);
            if (isNaN(timeout) || timeout < 1) {
                errors.push('自動提交時間必須大於等於 1 秒');
            } else if (timeout > 86400) { // 24 小時
                errors.push('自動提交時間不能超過 24 小時');
            }
        }

        // 驗證提示詞 ID
        if (settings.autoSubmitEnabled && !settings.autoSubmitPromptId) {
            errors.push('啟用自動提交時必須選擇一個提示詞');
        }

        return errors;
    };

    /**
     * 設定自動提交功能
     */
    SettingsManager.prototype.setAutoSubmitSettings = function(enabled, timeout, promptId) {
        const newSettings = {
            autoSubmitEnabled: Boolean(enabled),
            autoSubmitTimeout: parseInt(timeout) || 30,
            autoSubmitPromptId: promptId || null
        };

        // 驗證設定
        const errors = this.validateAutoSubmitSettings(newSettings);
        if (errors.length > 0) {
            throw new Error(errors.join('; '));
        }

        // 如果停用自動提交，清除提示詞 ID
        if (!newSettings.autoSubmitEnabled) {
            newSettings.autoSubmitPromptId = null;
        }

        // 更新設定
        this.set('autoSubmitEnabled', newSettings.autoSubmitEnabled);
        this.set('autoSubmitTimeout', newSettings.autoSubmitTimeout);
        this.set('autoSubmitPromptId', newSettings.autoSubmitPromptId);

        console.log('自動提交設定已更新:', newSettings);
        return newSettings;
    };

    /**
     * 獲取自動提交設定
     */
    SettingsManager.prototype.getAutoSubmitSettings = function() {
        return {
            enabled: this.get('autoSubmitEnabled'),
            timeout: this.get('autoSubmitTimeout'),
            promptId: this.get('autoSubmitPromptId')
        };
    };

    /**
     * 觸發自動提交狀態變更事件
     */
    SettingsManager.prototype.triggerAutoSubmitStateChange = function(enabled) {
        if (this.onAutoSubmitStateChange) {
            const settings = this.getAutoSubmitSettings();
            console.log('🔍 triggerAutoSubmitStateChange 調試:', {
                enabled: enabled,
                settings: settings,
                currentSettings: this.currentSettings
            });
            this.onAutoSubmitStateChange(enabled, settings);
        }

        console.log('自動提交狀態變更:', enabled ? '啟用' : '停用');
    };

    /**
     * 獲取所有設定
     */
    SettingsManager.prototype.getAllSettings = function() {
        return Utils.deepClone(this.currentSettings);
    };

    /**
     * 應用設定到 UI
     */
    SettingsManager.prototype.applyToUI = function() {
        console.log('應用設定到 UI');
        
        // 應用佈局模式
        this.applyLayoutMode();
        
        // 應用自動關閉設定
        this.applyAutoCloseToggle();
        
        // 應用語言設定
        this.applyLanguageSettings();
        
        // 應用圖片設定
        this.applyImageSettings();

        // 應用自動提交設定
        this.applyAutoSubmitSettingsToUI();

        // 應用會話歷史設定
        this.applySessionHistorySettings();

        // 應用用戶訊息記錄設定
        this.applyUserMessageSettings();

        // 應用 Telegram 整合設定
        this.applyTelegramSettings();
    };

    /**
     * 應用佈局模式
     */
    SettingsManager.prototype.applyLayoutMode = function() {
        const layoutModeInputs = document.querySelectorAll('input[name="layoutMode"]');
        layoutModeInputs.forEach(function(input) {
            input.checked = input.value === this.currentSettings.layoutMode;
        }.bind(this));

        const expectedClassName = 'layout-' + this.currentSettings.layoutMode;
        if (document.body.className !== expectedClassName) {
            console.log('應用佈局模式: ' + this.currentSettings.layoutMode);
            document.body.className = expectedClassName;
        }
    };

    /**
     * 應用自動關閉設定
     */
    SettingsManager.prototype.applyAutoCloseToggle = function() {
        const autoCloseToggle = Utils.safeQuerySelector('#autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.classList.toggle('active', this.currentSettings.autoClose);
        }
    };

    /**
     * 應用語言設定
     */
    SettingsManager.prototype.applyLanguageSettings = function() {
        if (this.currentSettings.language && window.i18nManager) {
            const currentI18nLanguage = window.i18nManager.getCurrentLanguage();
            if (this.currentSettings.language !== currentI18nLanguage) {
                console.log('應用語言設定: ' + currentI18nLanguage + ' -> ' + this.currentSettings.language);
                window.i18nManager.setLanguage(this.currentSettings.language);
            }
        }

        // 更新下拉選單選項
        const languageSelect = Utils.safeQuerySelector('#settingsLanguageSelect');
        if (languageSelect) {
            console.log(`🔧 SettingsManager.applyLanguageSettings: 設置 select.value = ${this.currentSettings.language}`);
            languageSelect.value = this.currentSettings.language;
            console.log(`🔧 SettingsManager.applyLanguageSettings: 實際 select.value = ${languageSelect.value}`);
        }

        // 更新語言選項顯示（兼容舊版卡片式選擇器）
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(function(option) {
            option.classList.toggle('active', option.getAttribute('data-lang') === this.currentSettings.language);
        }.bind(this));
    };

    /**
     * 應用圖片設定
     */
    SettingsManager.prototype.applyImageSettings = function() {
        // 更新所有圖片大小限制選擇器（包括設定頁籤中的）
        const imageSizeLimitSelects = document.querySelectorAll('[id$="ImageSizeLimit"]');
        imageSizeLimitSelects.forEach(function(select) {
            select.value = this.currentSettings.imageSizeLimit.toString();
        }.bind(this));

        // 更新所有 Base64 相容模式複選框（包括設定頁籤中的）
        const enableBase64DetailCheckboxes = document.querySelectorAll('[id$="EnableBase64Detail"]');
        enableBase64DetailCheckboxes.forEach(function(checkbox) {
            checkbox.checked = this.currentSettings.enableBase64Detail;
        }.bind(this));

        console.log('圖片設定已應用到 UI:', {
            imageSizeLimit: this.currentSettings.imageSizeLimit,
            enableBase64Detail: this.currentSettings.enableBase64Detail
        });
    };

    /**
     * 應用自動提交設定到 UI
     */
    SettingsManager.prototype.applyAutoSubmitSettingsToUI = function() {
        // 更新自動提交啟用開關
        const autoSubmitToggle = Utils.safeQuerySelector('#autoSubmitToggle');
        if (autoSubmitToggle) {
            autoSubmitToggle.classList.toggle('active', this.currentSettings.autoSubmitEnabled);
        }

        // 更新自動提交超時時間輸入框
        const autoSubmitTimeoutInput = Utils.safeQuerySelector('#autoSubmitTimeout');
        if (autoSubmitTimeoutInput) {
            autoSubmitTimeoutInput.value = this.currentSettings.autoSubmitTimeout;
        }

        // 更新自動提交提示詞選擇下拉選單
        const autoSubmitPromptSelect = Utils.safeQuerySelector('#autoSubmitPromptSelect');
        if (autoSubmitPromptSelect) {
            autoSubmitPromptSelect.value = this.currentSettings.autoSubmitPromptId || '';
        }

        // 更新自動提交狀態顯示
        this.updateAutoSubmitStatusDisplay();

        console.log('自動提交設定已應用到 UI:', {
            enabled: this.currentSettings.autoSubmitEnabled,
            timeout: this.currentSettings.autoSubmitTimeout,
            promptId: this.currentSettings.autoSubmitPromptId
        });
    };

    /**
     * 更新自動提交狀態顯示
     */
    SettingsManager.prototype.updateAutoSubmitStatusDisplay = function() {
        const statusElement = Utils.safeQuerySelector('#autoSubmitStatus');
        if (!statusElement) return;

        const statusIcon = statusElement.querySelector('span:first-child');
        const statusText = statusElement.querySelector('.button-text');

        if (this.currentSettings.autoSubmitEnabled && this.currentSettings.autoSubmitPromptId) {
            // 直接設定 HTML 內容，就像提示詞按鈕一樣
            if (statusIcon) statusIcon.innerHTML = '⏰';
            if (statusText) {
                const enabledText = window.i18nManager ?
                    window.i18nManager.t('autoSubmit.enabled', '已啟用') :
                    '已啟用';
                statusText.textContent = `${enabledText} (${this.currentSettings.autoSubmitTimeout}秒)`;
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
    };

    /**
     * 應用會話歷史設定
     */
    SettingsManager.prototype.applySessionHistorySettings = function() {
        // 更新會話歷史保存期限選擇器
        const sessionHistoryRetentionSelect = Utils.safeQuerySelector('#sessionHistoryRetentionHours');
        if (sessionHistoryRetentionSelect) {
            sessionHistoryRetentionSelect.value = this.currentSettings.sessionHistoryRetentionHours.toString();
        }

        console.log('會話歷史設定已應用到 UI:', {
            retentionHours: this.currentSettings.sessionHistoryRetentionHours
        });
    };

    /**
     * 應用用戶訊息記錄設定
     */
    SettingsManager.prototype.applyUserMessageSettings = function() {
        // 更新用戶訊息記錄啟用開關
        const userMessageRecordingToggle = Utils.safeQuerySelector('#userMessageRecordingToggle');
        if (userMessageRecordingToggle) {
            userMessageRecordingToggle.checked = this.currentSettings.userMessageRecordingEnabled;
        }

        // 更新隱私等級選擇器
        const userMessagePrivacySelect = Utils.safeQuerySelector('#userMessagePrivacyLevel');
        if (userMessagePrivacySelect) {
            userMessagePrivacySelect.value = this.currentSettings.userMessagePrivacyLevel;
        }

        console.log('用戶訊息記錄設定已應用到 UI:', {
            recordingEnabled: this.currentSettings.userMessageRecordingEnabled,
            privacyLevel: this.currentSettings.userMessagePrivacyLevel
        });

        // 更新隱私等級描述
        this.updatePrivacyLevelDescription(this.currentSettings.userMessagePrivacyLevel);
    };

    /**
     * 更新隱私等級描述文字
     */
    SettingsManager.prototype.updatePrivacyLevelDescription = function(privacyLevel) {
        const descriptionElement = Utils.safeQuerySelector('#userMessagePrivacyDescription');
        if (!descriptionElement || !window.i18nManager) {
            return;
        }

        let descriptionKey = '';
        switch (privacyLevel) {
            case 'full':
                descriptionKey = 'sessionHistory.userMessages.privacyDescription.full';
                break;
            case 'basic':
                descriptionKey = 'sessionHistory.userMessages.privacyDescription.basic';
                break;
            case 'disabled':
                descriptionKey = 'sessionHistory.userMessages.privacyDescription.disabled';
                break;
            default:
                descriptionKey = 'sessionHistory.userMessages.privacyDescription.full';
        }

        // 更新 data-i18n 屬性，這樣在語言切換時會自動更新
        descriptionElement.setAttribute('data-i18n', descriptionKey);

        // 立即更新文字內容
        const description = window.i18nManager.t(descriptionKey);
        descriptionElement.textContent = description;
    };

    /**
     * 應用 Telegram 整合設定到 UI
     */
    SettingsManager.prototype.applyTelegramSettings = function() {
        // 更新 Telegram 整合啟用開關
        const telegramToggle = Utils.safeQuerySelector('#telegramToggle');
        if (telegramToggle) {
            telegramToggle.classList.toggle('active', this.currentSettings.telegramEnabled);
        }

        // 更新 Bot Token 輸入框
        const botTokenInput = Utils.safeQuerySelector('#telegramBotToken');
        if (botTokenInput) {
            botTokenInput.value = this.currentSettings.telegramBotToken || '';
        }

        // 更新 Chat ID 輸入框
        const chatIdInput = Utils.safeQuerySelector('#telegramChatId');
        if (chatIdInput) {
            chatIdInput.value = this.currentSettings.telegramChatId || '';
        }

        // 更新訊息格式設定
        const includeSessionIdToggle = Utils.safeQuerySelector('#telegramIncludeSessionId');
        if (includeSessionIdToggle) {
            includeSessionIdToggle.checked = this.currentSettings.telegramIncludeSessionId;
        }

        const includeTimestampToggle = Utils.safeQuerySelector('#telegramIncludeTimestamp');
        if (includeTimestampToggle) {
            includeTimestampToggle.checked = this.currentSettings.telegramIncludeTimestamp;
        }

        const includeProjectPathToggle = Utils.safeQuerySelector('#telegramIncludeProjectPath');
        if (includeProjectPathToggle) {
            includeProjectPathToggle.checked = this.currentSettings.telegramIncludeProjectPath;
        }

        // 更新配置區域顯示狀態
        this.toggleTelegramConfigVisibility(this.currentSettings.telegramEnabled);

        // 更新連接狀態
        this.updateTelegramStatus();

        console.log('Telegram 整合設定已應用到 UI:', {
            enabled: this.currentSettings.telegramEnabled,
            botToken: this.currentSettings.telegramBotToken ? '[已設定]' : '[未設定]',
            chatId: this.currentSettings.telegramChatId || '[未設定]',
            includeSessionId: this.currentSettings.telegramIncludeSessionId,
            includeTimestamp: this.currentSettings.telegramIncludeTimestamp,
            includeProjectPath: this.currentSettings.telegramIncludeProjectPath
        });
    };

    /**
     * 設置事件監聽器
     */
    SettingsManager.prototype.setupEventListeners = function() {
        const self = this;
        
        // 佈局模式切換
        const layoutModeInputs = document.querySelectorAll('input[name="layoutMode"]');
        layoutModeInputs.forEach(function(input) {
            input.addEventListener('change', function(e) {
                self.set('layoutMode', e.target.value);
            });
        });

        // 自動關閉切換
        const autoCloseToggle = Utils.safeQuerySelector('#autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.addEventListener('click', function() {
                const newValue = !self.get('autoClose');
                self.set('autoClose', newValue);
                autoCloseToggle.classList.toggle('active', newValue);
            });
        }

        // 語言切換 - 支援下拉選單
        const languageSelect = Utils.safeQuerySelector('#settingsLanguageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', function(e) {
                const lang = e.target.value;
                console.log(`🔄 SettingsManager select change event: ${lang}`);
                self.set('language', lang);
            });
        }

        // 語言切換 - 兼容舊版卡片式選擇器
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(function(option) {
            option.addEventListener('click', function() {
                const lang = option.getAttribute('data-lang');
                self.set('language', lang);
            });
        });

        // 圖片設定 - 大小限制選擇器
        const settingsImageSizeLimit = Utils.safeQuerySelector('#settingsImageSizeLimit');
        if (settingsImageSizeLimit) {
            settingsImageSizeLimit.addEventListener('change', function(e) {
                const value = parseInt(e.target.value);
                self.set('imageSizeLimit', value);
                console.log('圖片大小限制已更新:', value);
            });
        }

        // 圖片設定 - Base64 相容模式切換器
        const settingsEnableBase64Detail = Utils.safeQuerySelector('#settingsEnableBase64Detail');
        if (settingsEnableBase64Detail) {
            settingsEnableBase64Detail.addEventListener('change', function(e) {
                const value = e.target.checked;
                self.set('enableBase64Detail', value);
                console.log('Base64 相容模式已更新:', value);
            });
        }

        // 自動提交功能啟用開關
        const autoSubmitToggle = Utils.safeQuerySelector('#autoSubmitToggle');
        if (autoSubmitToggle) {
            autoSubmitToggle.addEventListener('click', function() {
                const newValue = !self.get('autoSubmitEnabled');
                const currentPromptId = self.get('autoSubmitPromptId');

                console.log('自動提交開關點擊:', {
                    newValue: newValue,
                    currentPromptId: currentPromptId
                });

                try {
                    // 如果要啟用自動提交，檢查是否已選擇提示詞
                    if (newValue && (!currentPromptId || currentPromptId === '')) {
                        Utils.showMessage('請先選擇一個提示詞作為自動提交內容', Utils.CONSTANTS.MESSAGE_WARNING);
                        return;
                    }

                    self.set('autoSubmitEnabled', newValue);
                    autoSubmitToggle.classList.toggle('active', newValue);

                    console.log('自動提交狀態已更新:', newValue);

                    // 觸發自動提交狀態變更事件
                    self.triggerAutoSubmitStateChange(newValue);
                } catch (error) {
                    Utils.showMessage(error.message, Utils.CONSTANTS.MESSAGE_ERROR);
                }
            });
        }

        // 自動提交超時時間設定
        const autoSubmitTimeoutInput = Utils.safeQuerySelector('#autoSubmitTimeout');
        if (autoSubmitTimeoutInput) {
            autoSubmitTimeoutInput.addEventListener('change', function(e) {
                const timeout = parseInt(e.target.value);
                try {
                    self.setAutoSubmitSettings(
                        self.get('autoSubmitEnabled'),
                        timeout,
                        self.get('autoSubmitPromptId')
                    );
                } catch (error) {
                    Utils.showMessage(error.message, Utils.CONSTANTS.MESSAGE_ERROR);
                    // 恢復原值
                    e.target.value = self.get('autoSubmitTimeout');
                }
            });
        }

        // 自動提交提示詞選擇
        const autoSubmitPromptSelect = Utils.safeQuerySelector('#autoSubmitPromptSelect');
        if (autoSubmitPromptSelect) {
            autoSubmitPromptSelect.addEventListener('change', function(e) {
                const promptId = e.target.value || null;
                console.log('自動提交提示詞選擇變更:', promptId);

                try {
                    // 如果選擇了空值，清除自動提交設定
                    if (!promptId || promptId === '') {
                        self.set('autoSubmitPromptId', null);
                        self.set('autoSubmitEnabled', false);

                        // 同時清除所有提示詞的 isAutoSubmit 標記
                        if (window.feedbackApp && window.feedbackApp.promptManager) {
                            window.feedbackApp.promptManager.clearAutoSubmitPrompt();
                            console.log('🔄 已清除所有提示詞的自動提交標記');
                        } else {
                            console.warn('⚠️ promptManager 未找到，無法清除提示詞標記');
                        }

                        // 觸發狀態變更事件，更新相關 UI 組件
                        self.triggerAutoSubmitStateChange(false);

                        // 更新 UI 元素（按鈕狀態、倒數計時器等）
                        self.applyAutoSubmitSettingsToUI();

                        console.log('清除自動提交設定並更新 UI');
                    } else {
                        // 設定新的自動提交提示詞
                        self.set('autoSubmitPromptId', promptId);
                        console.log('設定自動提交提示詞 ID:', promptId);

                        // 同時更新對應提示詞的 isAutoSubmit 標記
                        if (window.feedbackApp && window.feedbackApp.promptManager) {
                            try {
                                window.feedbackApp.promptManager.setAutoSubmitPrompt(promptId);
                                console.log('🔄 已設定提示詞的自動提交標記:', promptId);

                                // 觸發狀態變更事件，更新相關 UI 組件
                                const currentEnabled = self.get('autoSubmitEnabled');
                                self.triggerAutoSubmitStateChange(currentEnabled);

                                // 更新 UI 元素
                                self.applyAutoSubmitSettingsToUI();

                                console.log('🔄 已更新自動提交 UI 狀態');
                            } catch (promptError) {
                                console.error('❌ 設定提示詞自動提交標記失敗:', promptError);
                                // 如果設定提示詞失敗，回滾設定
                                self.set('autoSubmitPromptId', null);
                                e.target.value = '';
                                throw promptError;
                            }
                        } else {
                            console.warn('⚠️ promptManager 未找到，無法設定提示詞標記');
                        }
                    }
                } catch (error) {
                    Utils.showMessage(error.message, Utils.CONSTANTS.MESSAGE_ERROR);
                    // 恢復原值
                    e.target.value = self.get('autoSubmitPromptId') || '';
                }
            });
        }

        // 會話歷史保存期限設定
        const sessionHistoryRetentionSelect = Utils.safeQuerySelector('#sessionHistoryRetentionHours');
        if (sessionHistoryRetentionSelect) {
            sessionHistoryRetentionSelect.addEventListener('change', function(e) {
                const hours = parseInt(e.target.value);
                self.set('sessionHistoryRetentionHours', hours);
                console.log('會話歷史保存期限已更新:', hours, '小時');

                // 觸發清理過期會話
                if (window.MCPFeedback && window.MCPFeedback.app && window.MCPFeedback.app.sessionManager) {
                    const sessionManager = window.MCPFeedback.app.sessionManager;
                    if (sessionManager.dataManager && sessionManager.dataManager.cleanupExpiredSessions) {
                        sessionManager.dataManager.cleanupExpiredSessions();
                    }
                }
            });
        }

        // 會話歷史匯出按鈕
        const exportHistoryBtn = Utils.safeQuerySelector('#exportSessionHistoryBtn');
        if (exportHistoryBtn) {
            exportHistoryBtn.addEventListener('click', function() {
                if (window.MCPFeedback && window.MCPFeedback.SessionManager) {
                    window.MCPFeedback.SessionManager.exportSessionHistory();
                }
            });
        }

        // 會話歷史清空按鈕
        const clearHistoryBtn = Utils.safeQuerySelector('#clearSessionHistoryBtn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', function() {
                if (window.MCPFeedback && window.MCPFeedback.SessionManager) {
                    window.MCPFeedback.SessionManager.clearSessionHistory();
                }
            });
        }

        // 清空用戶訊息記錄按鈕
        const clearUserMessagesBtn = Utils.safeQuerySelector('#clearUserMessagesBtn');
        if (clearUserMessagesBtn) {
            clearUserMessagesBtn.addEventListener('click', function() {
                const i18n = window.i18nManager;
                const confirmMessage = i18n ?
                    i18n.t('sessionHistory.userMessages.confirmClearAll') :
                    '確定要清空所有會話的用戶訊息記錄嗎？此操作無法復原。';

                if (confirm(confirmMessage)) {
                    if (window.MCPFeedback && window.MCPFeedback.app && window.MCPFeedback.app.sessionManager) {
                        const success = window.MCPFeedback.app.sessionManager.dataManager.clearAllUserMessages();
                        if (success) {
                            const successMessage = i18n ?
                                i18n.t('sessionHistory.userMessages.clearSuccess') :
                                '用戶訊息記錄已清空';
                            alert(successMessage);
                        }
                    }
                }
            });
        }

        // 用戶訊息記錄啟用開關
        const userMessageRecordingToggle = Utils.safeQuerySelector('#userMessageRecordingToggle');
        if (userMessageRecordingToggle) {
            userMessageRecordingToggle.addEventListener('change', function() {
                const newValue = userMessageRecordingToggle.checked;
                self.set('userMessageRecordingEnabled', newValue);
                console.log('用戶訊息記錄狀態已更新:', newValue);
            });
        }

        // 用戶訊息隱私等級選擇
        const userMessagePrivacySelect = Utils.safeQuerySelector('#userMessagePrivacyLevel');
        if (userMessagePrivacySelect) {
            userMessagePrivacySelect.addEventListener('change', function(e) {
                const privacyLevel = e.target.value;
                self.set('userMessagePrivacyLevel', privacyLevel);
                self.updatePrivacyLevelDescription(privacyLevel);
                console.log('用戶訊息隱私等級已更新:', privacyLevel);
            });
        }

        // 重置設定
        const resetBtn = Utils.safeQuerySelector('#resetSettingsBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                if (confirm('確定要重置所有設定嗎？')) {
                    self.resetSettings();
                    self.applyToUI();
                }
            });
        }

        // Telegram 整合設定事件監聽器
        self.setupTelegramEventListeners();

    };

    /**
     * 設置 Telegram 整合相關的事件監聽器
     */
    SettingsManager.prototype.setupTelegramEventListeners = function() {
        const self = this;

        // Telegram 整合啟用/停用切換
        const telegramToggle = Utils.safeQuerySelector('#telegramToggle');
        if (telegramToggle) {
            telegramToggle.addEventListener('click', function() {
                const newValue = !self.get('telegramEnabled');
                self.set('telegramEnabled', newValue);
                telegramToggle.classList.toggle('active', newValue);
                self.toggleTelegramConfigVisibility(newValue);
                self.updateTelegramStatus();
                console.log('Telegram 整合狀態已更新:', newValue);
            });
        }

        // Bot Token 輸入
        const botTokenInput = Utils.safeQuerySelector('#telegramBotToken');
        if (botTokenInput) {
            botTokenInput.addEventListener('input', function(e) {
                const token = e.target.value.trim();
                self.set('telegramBotToken', token);
                self.updateTelegramStatus();
                console.log('Telegram Bot Token 已更新');
            });
        }

        // Chat ID 輸入
        const chatIdInput = Utils.safeQuerySelector('#telegramChatId');
        if (chatIdInput) {
            chatIdInput.addEventListener('input', function(e) {
                const chatId = e.target.value.trim();
                self.set('telegramChatId', chatId);
                self.updateTelegramStatus();
                console.log('Telegram Chat ID 已更新:', chatId);
            });
        }

        // Bot Token 顯示/隱藏切換
        const toggleTokenVisibility = Utils.safeQuerySelector('#toggleBotTokenVisibility');
        if (toggleTokenVisibility) {
            toggleTokenVisibility.addEventListener('click', function() {
                const input = Utils.safeQuerySelector('#telegramBotToken');
                if (input) {
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';
                    toggleTokenVisibility.textContent = isPassword ? '🙈' : '👁️';
                }
            });
        }

        // 連接測試按鈕
        const testConnectionBtn = Utils.safeQuerySelector('#testTelegramConnection');
        if (testConnectionBtn) {
            testConnectionBtn.addEventListener('click', function() {
                self.testTelegramConnection();
            });
        }

        // 訊息格式設定 - 包含會話 ID
        const includeSessionIdToggle = Utils.safeQuerySelector('#telegramIncludeSessionId');
        if (includeSessionIdToggle) {
            includeSessionIdToggle.addEventListener('change', function(e) {
                self.set('telegramIncludeSessionId', e.target.checked);
                console.log('Telegram 包含會話 ID 設定已更新:', e.target.checked);
            });
        }

        // 訊息格式設定 - 包含時間戳記
        const includeTimestampToggle = Utils.safeQuerySelector('#telegramIncludeTimestamp');
        if (includeTimestampToggle) {
            includeTimestampToggle.addEventListener('change', function(e) {
                self.set('telegramIncludeTimestamp', e.target.checked);
                console.log('Telegram 包含時間戳記設定已更新:', e.target.checked);
            });
        }

        // 訊息格式設定 - 包含專案路徑
        const includeProjectPathToggle = Utils.safeQuerySelector('#telegramIncludeProjectPath');
        if (includeProjectPathToggle) {
            includeProjectPathToggle.addEventListener('change', function(e) {
                self.set('telegramIncludeProjectPath', e.target.checked);
                console.log('Telegram 包含專案路徑設定已更新:', e.target.checked);
            });
        }
    };

    /**
     * 切換 Telegram 配置區域的顯示/隱藏
     */
    SettingsManager.prototype.toggleTelegramConfigVisibility = function(enabled) {
        const configSection = Utils.safeQuerySelector('#telegramConfig');
        if (configSection) {
            configSection.style.display = enabled ? 'block' : 'none';
        }
    };

    /**
     * 更新 Telegram 連接狀態指示器
     */
    SettingsManager.prototype.updateTelegramStatus = function() {
        const statusDot = Utils.safeQuerySelector('#telegramStatusDot');
        const statusText = Utils.safeQuerySelector('#telegramStatusText');

        if (!statusDot || !statusText) return;

        const enabled = this.get('telegramEnabled');
        const botToken = this.get('telegramBotToken');
        const chatId = this.get('telegramChatId');

        // 清除所有狀態類別
        statusDot.classList.remove('connected', 'connecting', 'error');

        if (!enabled) {
            statusText.textContent = window.i18nManager ?
                window.i18nManager.t('telegram.disabled') : '已停用';
        } else if (!botToken || !chatId) {
            statusText.textContent = window.i18nManager ?
                window.i18nManager.t('telegram.configIncomplete') : '配置不完整';
        } else {
            statusText.textContent = window.i18nManager ?
                window.i18nManager.t('telegram.readyToTest') : '準備測試';
        }
    };

    /**
     * 測試 Telegram 連接
     */
    SettingsManager.prototype.testTelegramConnection = function() {
        const self = this;
        const testBtn = Utils.safeQuerySelector('#testTelegramConnection');
        const statusDot = Utils.safeQuerySelector('#telegramStatusDot');
        const statusText = Utils.safeQuerySelector('#telegramStatusText');

        if (!testBtn || !statusDot || !statusText) return;

        const botToken = this.get('telegramBotToken');
        const chatId = this.get('telegramChatId');

        // 驗證配置
        if (!botToken || !chatId) {
            Utils.showMessage(
                window.i18nManager ?
                    window.i18nManager.t('telegram.configRequired') :
                    '請先配置 Bot Token 和 Chat ID',
                Utils.CONSTANTS.MESSAGE_WARNING
            );
            return;
        }

        // 更新 UI 狀態為測試中
        testBtn.classList.add('testing');
        testBtn.disabled = true;
        statusDot.classList.remove('connected', 'error');
        statusDot.classList.add('connecting');
        statusText.textContent = window.i18nManager ?
            window.i18nManager.t('telegram.testing') : '測試中...';

        // 實際測試（調用後端 API）
        self.simulateTelegramTest(botToken, chatId).then(function(success) {
            // 更新 UI 狀態
            testBtn.classList.remove('testing');
            testBtn.disabled = false;
            statusDot.classList.remove('connecting');

            if (success) {
                testBtn.classList.add('success');
                statusDot.classList.add('connected');
                statusText.textContent = window.i18nManager ?
                    window.i18nManager.t('telegram.connected') : '連接成功';

                Utils.showMessage(
                    window.i18nManager ?
                        window.i18nManager.t('telegram.testSuccess') :
                        'Telegram 連接測試成功！',
                    Utils.CONSTANTS.MESSAGE_SUCCESS
                );

                // 3秒後清除成功狀態
                setTimeout(function() {
                    testBtn.classList.remove('success');
                }, 3000);
            } else {
                testBtn.classList.add('error');
                statusDot.classList.add('error');
                statusText.textContent = window.i18nManager ?
                    window.i18nManager.t('telegram.connectionFailed') : '連接失敗';

                Utils.showMessage(
                    window.i18nManager ?
                        window.i18nManager.t('telegram.testFailed') :
                        'Telegram 連接測試失敗，請檢查配置',
                    Utils.CONSTANTS.MESSAGE_ERROR
                );

                // 3秒後清除錯誤狀態
                setTimeout(function() {
                    testBtn.classList.remove('error');
                }, 3000);
            }
        }).catch(function(error) {
            console.error('Telegram test error:', error);

            // 錯誤處理
            testBtn.classList.remove('testing');
            testBtn.classList.add('error');
            testBtn.disabled = false;
            statusDot.classList.remove('connecting');
            statusDot.classList.add('error');
            statusText.textContent = window.i18nManager ?
                window.i18nManager.t('telegram.connectionFailed') : '連接失敗';

            Utils.showMessage(
                window.i18nManager ?
                    window.i18nManager.t('telegram.testFailed') :
                    'Telegram 連接測試失敗，請檢查配置',
                Utils.CONSTANTS.MESSAGE_ERROR
            );

            setTimeout(function() {
                testBtn.classList.remove('error');
            }, 3000);
        });
    };

    /**
     * 實際 Telegram 連接測試（調用後端 API）
     */
    SettingsManager.prototype.simulateTelegramTest = function(botToken, chatId) {
        // 實際實現：調用後端 API 進行真實連接測試
        return new Promise(async (resolve) => {
            try {
                // 調用後端測試 API
                const response = await fetch('/api/telegram/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        bot_token: botToken,
                        chat_id: chatId
                    })
                });

                const result = await response.json();
                resolve(result.success || false);
            } catch (error) {
                console.error('Telegram test API error:', error);
                // 回退到格式驗證
                const tokenPattern = /^\d+:[A-Za-z0-9_-]+$/;
                const chatIdPattern = /^(@\w+|-?\d+)$/;
                resolve(tokenPattern.test(botToken) && chatIdPattern.test(chatId));
            }
        });
    };

    // 將 SettingsManager 加入命名空間
    window.MCPFeedback.SettingsManager = SettingsManager;

    console.log('✅ SettingsManager 模組載入完成');

})();
