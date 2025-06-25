/**
 * MCP Feedback Enhanced - 音效管理模組
 * ===================================
 * 
 * 處理音效通知的播放、管理和設定功能
 * 使用 HTML5 Audio API 進行音效播放
 * 支援自訂音效上傳和 base64 儲存
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * 音效管理器建構函數
     */
    function AudioManager(options) {
        options = options || {};
        
        // 設定管理器引用
        this.settingsManager = options.settingsManager || null;
        
        // 當前音效設定
        this.currentAudioSettings = {
            enabled: false,
            volume: 50,
            selectedAudioId: 'default-beep',
            customAudios: []
        };
        
        // 預設音效（base64 編碼的簡單提示音）
        this.defaultAudios = {
            'default-beep': {
                id: 'default-beep',
                name: '經典提示音',
                data: this.generateBeepSound(),
                mimeType: 'audio/wav',
                isDefault: true
            },
            'notification-ding': {
                id: 'notification-ding',
                name: '通知鈴聲',
                data: this.generateDingSound(),
                mimeType: 'audio/wav',
                isDefault: true
            },
            'soft-chime': {
                id: 'soft-chime',
                name: '輕柔鐘聲',
                data: this.generateChimeSound(),
                mimeType: 'audio/wav',
                isDefault: true
            }
        };
        
        // 當前播放的 Audio 物件
        this.currentAudio = null;

        // 用戶互動檢測
        this.userHasInteracted = false;
        this.pendingNotifications = [];
        this.autoplayBlocked = false;
        this.interactionListenersAdded = false;

        // 增強的權限管理
        this.audioPermissionRequested = false;
        this.audioPermissionGranted = false;
        this.permissionDialogShown = false;
        this.fallbackNotificationsEnabled = false;

        // 通知方法
        this.notificationPermission = null;
        this.titleBarNotificationActive = false;
        this.originalTitle = document.title;

        // 回調函數
        this.onSettingsChange = options.onSettingsChange || null;

        // 啟動音效播放標記
        this.startupNotificationPlayed = false;
        this.autoplayNotificationShown = false;

        console.log('🔊 AudioManager 初始化完成');
    }

    /**
     * 初始化音效管理器
     */
    AudioManager.prototype.initialize = function() {
        this.loadAudioSettings();
        this.setupUserInteractionDetection();
        this.initializePermissions();
        this.createAudioPermissionIndicator();
        console.log('✅ AudioManager 初始化完成');
    };

    /**
     * 初始化權限系統
     */
    AudioManager.prototype.initializePermissions = function() {
        // 檢查瀏覽器通知權限
        if ('Notification' in window) {
            this.notificationPermission = Notification.permission;
        }

        // 檢查是否已有音效權限
        this.checkAudioPermissionStatus();

        console.log('🔐 權限系統初始化完成');
    };

    /**
     * 檢查音效權限狀態
     */
    AudioManager.prototype.checkAudioPermissionStatus = function() {
        // 從 localStorage 讀取權限狀態
        this.audioPermissionGranted = localStorage.getItem('audioPermissionGranted') === 'true';
        this.audioPermissionRequested = localStorage.getItem('audioPermissionRequested') === 'true';

        if (this.audioPermissionGranted) {
            console.log('🔊 音效權限已授予');
        } else if (this.audioPermissionRequested) {
            console.log('🔇 音效權限已請求但未授予，啟用備用通知');
            this.enableFallbackNotifications();
        }
    };

    /**
     * 載入音效設定
     */
    AudioManager.prototype.loadAudioSettings = function() {
        if (!this.settingsManager) {
            console.warn('⚠️ SettingsManager 未設定，使用預設音效設定');
            return;
        }

        try {
            // 從設定管理器載入音效相關設定
            this.currentAudioSettings.enabled = this.settingsManager.get('audioNotificationEnabled', false);
            this.currentAudioSettings.volume = this.settingsManager.get('audioNotificationVolume', 50);
            this.currentAudioSettings.selectedAudioId = this.settingsManager.get('selectedAudioId', 'default-beep');
            this.currentAudioSettings.customAudios = this.settingsManager.get('customAudios', []);
            
            console.log('📥 音效設定已載入:', this.currentAudioSettings);
        } catch (error) {
            console.error('❌ 載入音效設定失敗:', error);
        }
    };

    /**
     * 儲存音效設定
     */
    AudioManager.prototype.saveAudioSettings = function() {
        if (!this.settingsManager) {
            console.warn('⚠️ SettingsManager 未設定，無法儲存音效設定');
            return;
        }

        try {
            this.settingsManager.set('audioNotificationEnabled', this.currentAudioSettings.enabled);
            this.settingsManager.set('audioNotificationVolume', this.currentAudioSettings.volume);
            this.settingsManager.set('selectedAudioId', this.currentAudioSettings.selectedAudioId);
            this.settingsManager.set('customAudios', this.currentAudioSettings.customAudios);
            
            console.log('💾 音效設定已儲存');
            
            // 觸發回調
            if (this.onSettingsChange) {
                this.onSettingsChange(this.currentAudioSettings);
            }
        } catch (error) {
            console.error('❌ 儲存音效設定失敗:', error);
        }
    };

    /**
     * 播放通知音效（智能播放策略）
     */
    AudioManager.prototype.playNotification = function() {
        if (!this.currentAudioSettings.enabled) {
            console.log('🔇 音效通知已停用');
            return;
        }

        try {
            const audioData = this.getAudioById(this.currentAudioSettings.selectedAudioId);
            if (!audioData) {
                console.warn('⚠️ 找不到指定的音效，使用預設音效');
                this.playAudioSmart(this.defaultAudios['default-beep']);
                return;
            }

            this.playAudioSmart(audioData);
        } catch (error) {
            console.error('❌ 播放通知音效失敗:', error);
        }
    };

    /**
     * 播放啟動音效通知（應用程式就緒時播放）
     */
    AudioManager.prototype.playStartupNotification = function() {
        if (!this.currentAudioSettings.enabled) {
            console.log('🔇 音效通知已停用，跳過啟動音效');
            return;
        }

        // 確保啟動音效只播放一次
        if (this.startupNotificationPlayed) {
            console.log('🔇 啟動音效已播放過，跳過重複播放');
            return;
        }

        this.startupNotificationPlayed = true;
        console.log('🎵 播放應用程式啟動音效');

        try {
            const audioData = this.getAudioById(this.currentAudioSettings.selectedAudioId);
            if (!audioData) {
                console.warn('⚠️ 找不到指定的音效，使用預設啟動音效');
                this.playAudioSmart(this.defaultAudios['default-beep']);
                return;
            }

            this.playAudioSmart(audioData);
        } catch (error) {
            console.error('❌ 播放啟動音效失敗:', error);
        }
    };

    /**
     * 智能音效播放（處理自動播放限制）
     */
    AudioManager.prototype.playAudioSmart = function(audioData) {
        // 檢查音效是否啟用
        if (!this.currentAudioSettings.enabled) {
            console.log('🔇 音效通知已停用');
            return;
        }

        // 如果沒有音效權限，顯示權限請求或使用備用通知
        if (!this.audioPermissionGranted && !this.audioPermissionRequested) {
            this.requestAudioPermission();
            return;
        }

        // 如果權限被拒絕，使用備用通知
        if (this.audioPermissionRequested && !this.audioPermissionGranted) {
            this.triggerFallbackNotification(audioData);
            return;
        }

        // 如果已知自動播放被阻止，直接加入待播放隊列
        if (this.autoplayBlocked && !this.userHasInteracted) {
            this.addToPendingNotifications(audioData);
            this.triggerFallbackNotification(audioData);
            return;
        }

        // 嘗試播放
        this.playAudio(audioData)
            .then(() => {
                // 播放成功，清空待播放隊列
                this.processPendingNotifications();
                this.updateAudioPermissionStatus(true);
            })
            .catch((error) => {
                if (error.name === 'NotAllowedError') {
                    // 自動播放被阻止
                    this.autoplayBlocked = true;
                    this.addToPendingNotifications(audioData);
                    this.showEnhancedAutoplayBlockedNotification();
                    this.triggerFallbackNotification(audioData);
                } else {
                    console.error('❌ 音效播放失敗:', error);
                    this.triggerFallbackNotification(audioData);
                }
            });
    };

    /**
     * 播放指定的音效（返回 Promise）
     */
    AudioManager.prototype.playAudio = function(audioData) {
        return new Promise((resolve, reject) => {
            try {
                // 停止當前播放的音效
                if (this.currentAudio) {
                    this.currentAudio.pause();
                    this.currentAudio = null;
                }

                // 建立新的 Audio 物件
                this.currentAudio = new Audio();
                this.currentAudio.src = 'data:' + audioData.mimeType + ';base64,' + audioData.data;
                this.currentAudio.volume = this.currentAudioSettings.volume / 100;

                // 播放音效
                const playPromise = this.currentAudio.play();

                if (playPromise !== undefined) {
                    playPromise
                        .then(() => {
                            console.log('🔊 音效播放成功:', audioData.name);
                            resolve();
                        })
                        .catch(error => {
                            console.error('❌ 音效播放失敗:', error);
                            reject(error);
                        });
                } else {
                    // 舊版瀏覽器，假設播放成功
                    console.log('🔊 音效播放（舊版瀏覽器）:', audioData.name);
                    resolve();
                }
            } catch (error) {
                console.error('❌ 播放音效時發生錯誤:', error);
                reject(error);
            }
        });
    };

    /**
     * 根據 ID 獲取音效資料
     */
    AudioManager.prototype.getAudioById = function(audioId) {
        // 先檢查預設音效
        if (this.defaultAudios[audioId]) {
            return this.defaultAudios[audioId];
        }

        // 再檢查自訂音效
        return this.currentAudioSettings.customAudios.find(audio => audio.id === audioId) || null;
    };

    /**
     * 獲取所有可用的音效
     */
    AudioManager.prototype.getAllAudios = function() {
        const allAudios = [];
        
        // 新增預設音效
        Object.values(this.defaultAudios).forEach(audio => {
            allAudios.push(audio);
        });
        
        // 新增自訂音效
        this.currentAudioSettings.customAudios.forEach(audio => {
            allAudios.push(audio);
        });
        
        return allAudios;
    };

    /**
     * 新增自訂音效
     */
    AudioManager.prototype.addCustomAudio = function(name, file) {
        return new Promise((resolve, reject) => {
            if (!name || !file) {
                reject(new Error('音效名稱和檔案不能為空'));
                return;
            }

            // 檢查檔案類型
            if (!this.isValidAudioFile(file)) {
                reject(new Error('不支援的音效檔案格式'));
                return;
            }

            // 檢查名稱是否重複
            if (this.isAudioNameExists(name)) {
                reject(new Error('音效名稱已存在'));
                return;
            }

            // 轉換為 base64
            this.fileToBase64(file)
                .then(base64Data => {
                    const audioData = {
                        id: this.generateAudioId(),
                        name: name.trim(),
                        data: base64Data,
                        mimeType: file.type,
                        createdAt: new Date().toISOString(),
                        isDefault: false
                    };

                    this.currentAudioSettings.customAudios.push(audioData);
                    this.saveAudioSettings();

                    console.log('➕ 新增自訂音效:', audioData.name);
                    resolve(audioData);
                })
                .catch(error => {
                    reject(error);
                });
        });
    };

    /**
     * 刪除自訂音效
     */
    AudioManager.prototype.removeCustomAudio = function(audioId) {
        const index = this.currentAudioSettings.customAudios.findIndex(audio => audio.id === audioId);
        if (index === -1) {
            throw new Error('找不到指定的音效');
        }

        const removedAudio = this.currentAudioSettings.customAudios.splice(index, 1)[0];
        
        // 如果刪除的是當前選中的音效，切換到預設音效
        if (this.currentAudioSettings.selectedAudioId === audioId) {
            this.currentAudioSettings.selectedAudioId = 'default-beep';
        }

        this.saveAudioSettings();
        console.log('🗑️ 刪除自訂音效:', removedAudio.name);
        
        return removedAudio;
    };

    /**
     * 設定音量
     */
    AudioManager.prototype.setVolume = function(volume) {
        if (volume < 0 || volume > 100) {
            throw new Error('音量必須在 0-100 之間');
        }

        this.currentAudioSettings.volume = volume;
        this.saveAudioSettings();
        console.log('🔊 音量已設定為:', volume);
    };

    /**
     * 設定是否啟用音效通知
     */
    AudioManager.prototype.setEnabled = function(enabled) {
        this.currentAudioSettings.enabled = !!enabled;
        this.saveAudioSettings();
        console.log('🔊 音效通知已', enabled ? '啟用' : '停用');
    };

    /**
     * 設定選中的音效
     */
    AudioManager.prototype.setSelectedAudio = function(audioId) {
        if (!this.getAudioById(audioId)) {
            throw new Error('找不到指定的音效');
        }

        this.currentAudioSettings.selectedAudioId = audioId;
        this.saveAudioSettings();
        console.log('🎵 已選擇音效:', audioId);
    };

    /**
     * 檢查是否為有效的音效檔案
     */
    AudioManager.prototype.isValidAudioFile = function(file) {
        const validTypes = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/mpeg'];
        return validTypes.includes(file.type);
    };

    /**
     * 檢查音效名稱是否已存在
     */
    AudioManager.prototype.isAudioNameExists = function(name) {
        // 檢查預設音效
        const defaultExists = Object.values(this.defaultAudios).some(audio => audio.name === name);
        if (defaultExists) return true;

        // 檢查自訂音效
        return this.currentAudioSettings.customAudios.some(audio => audio.name === name);
    };

    /**
     * 檔案轉 base64
     */
    AudioManager.prototype.fileToBase64 = function(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function() {
                // 移除 data URL 前綴，只保留 base64 資料
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = function() {
                reject(new Error('檔案讀取失敗'));
            };
            reader.readAsDataURL(file);
        });
    };

    /**
     * 生成音效 ID
     */
    AudioManager.prototype.generateAudioId = function() {
        return 'audio_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    };

    /**
     * 生成經典提示音（440Hz，0.3秒）
     */
    AudioManager.prototype.generateBeepSound = function() {
        return this.generateToneWAV(440, 0.3, 0.5);
    };

    /**
     * 生成通知鈴聲（800Hz + 600Hz 和弦，0.4秒）
     */
    AudioManager.prototype.generateDingSound = function() {
        return this.generateToneWAV(800, 0.4, 0.4);
    };

    /**
     * 生成輕柔鐘聲（523Hz，0.5秒，漸弱）
     */
    AudioManager.prototype.generateChimeSound = function() {
        return this.generateToneWAV(523, 0.5, 0.3);
    };

    /**
     * 生成指定頻率和時長的 WAV 音效
     * @param {number} frequency - 頻率（Hz）
     * @param {number} duration - 持續時間（秒）
     * @param {number} volume - 音量（0-1）
     */
    AudioManager.prototype.generateToneWAV = function(frequency, duration, volume) {
        const sampleRate = 44100;
        const numSamples = Math.floor(sampleRate * duration);
        const buffer = new ArrayBuffer(44 + numSamples * 2);
        const view = new DataView(buffer);

        // WAV 檔案標頭
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, 36 + numSamples * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 1, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, numSamples * 2, true);

        // 生成音效資料
        for (let i = 0; i < numSamples; i++) {
            const t = i / sampleRate;
            const fadeOut = Math.max(0, 1 - (t / duration) * 0.5); // 漸弱效果
            const sample = Math.sin(2 * Math.PI * frequency * t) * volume * fadeOut;
            const intSample = Math.max(-32768, Math.min(32767, Math.floor(sample * 32767)));
            view.setInt16(44 + i * 2, intSample, true);
        }

        // 轉換為 base64
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.length; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    };

    /**
     * 設置用戶互動檢測
     */
    AudioManager.prototype.setupUserInteractionDetection = function() {
        if (this.interactionListenersAdded) return;

        const self = this;
        const interactionEvents = ['click', 'keydown', 'touchstart'];

        const handleUserInteraction = function() {
            if (!self.userHasInteracted) {
                self.userHasInteracted = true;
                console.log('🎯 檢測到用戶互動，音效播放已解鎖');

                // 播放待播放的通知
                self.processPendingNotifications();

                // 移除事件監聽器
                interactionEvents.forEach(event => {
                    document.removeEventListener(event, handleUserInteraction, true);
                });
                self.interactionListenersAdded = false;
            }
        };

        // 添加事件監聽器
        interactionEvents.forEach(event => {
            document.addEventListener(event, handleUserInteraction, true);
        });

        this.interactionListenersAdded = true;
        console.log('🎯 用戶互動檢測已設置');
    };

    /**
     * 添加到待播放通知隊列
     */
    AudioManager.prototype.addToPendingNotifications = function(audioData) {
        // 限制隊列長度，避免積累太多通知
        if (this.pendingNotifications.length >= 3) {
            this.pendingNotifications.shift(); // 移除最舊的通知
        }

        this.pendingNotifications.push({
            audioData: audioData,
            timestamp: Date.now()
        });

        console.log('📋 音效已加入待播放隊列:', audioData.name, '隊列長度:', this.pendingNotifications.length);
    };

    /**
     * 處理待播放的通知
     */
    AudioManager.prototype.processPendingNotifications = function() {
        if (this.pendingNotifications.length === 0) return;

        console.log('🔊 處理待播放通知，數量:', this.pendingNotifications.length);

        // 只播放最新的通知，避免音效重疊
        const latestNotification = this.pendingNotifications[this.pendingNotifications.length - 1];
        this.pendingNotifications = []; // 清空隊列

        this.playAudio(latestNotification.audioData)
            .then(() => {
                console.log('🔊 待播放通知播放成功');
            })
            .catch(error => {
                console.warn('⚠️ 待播放通知播放失敗:', error);
            });
    };

    /**
     * 請求音效權限
     */
    AudioManager.prototype.requestAudioPermission = function() {
        if (this.permissionDialogShown) return;

        this.showPermissionDialog();
    };

    /**
     * 顯示權限請求對話框
     */
    AudioManager.prototype.showPermissionDialog = function() {
        if (this.permissionDialogShown) return;
        this.permissionDialogShown = true;

        const dialog = document.createElement('div');
        dialog.className = 'audio-permission-dialog-overlay';
        dialog.innerHTML = `
            <div class="audio-permission-dialog">
                <div class="dialog-header">
                    <h3>🔊 啟用音效通知</h3>
                </div>
                <div class="dialog-body">
                    <p>為了提供更好的使用體驗，我們希望在有新訊息時播放音效通知。</p>
                    <p>您可以選擇：</p>
                    <ul>
                        <li><strong>啟用音效</strong> - 播放音效通知</li>
                        <li><strong>使用其他通知</strong> - 使用視覺通知和瀏覽器通知</li>
                    </ul>
                </div>
                <div class="dialog-actions">
                    <button class="btn btn-secondary" id="audioPermissionDeny">使用其他通知</button>
                    <button class="btn btn-primary" id="audioPermissionAllow">啟用音效</button>
                </div>
            </div>
        `;

        // 事件處理
        const allowBtn = dialog.querySelector('#audioPermissionAllow');
        const denyBtn = dialog.querySelector('#audioPermissionDeny');

        allowBtn.addEventListener('click', () => {
            this.handleAudioPermissionResponse(true);
            dialog.remove();
        });

        denyBtn.addEventListener('click', () => {
            this.handleAudioPermissionResponse(false);
            dialog.remove();
        });

        // 點擊背景關閉
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
                this.handleAudioPermissionResponse(false);
                dialog.remove();
            }
        });

        document.body.appendChild(dialog);
        setTimeout(() => dialog.classList.add('show'), 10);
    };

    /**
     * 處理音效權限回應
     */
    AudioManager.prototype.handleAudioPermissionResponse = function(granted) {
        this.audioPermissionRequested = true;
        this.audioPermissionGranted = granted;

        // 保存到 localStorage
        localStorage.setItem('audioPermissionRequested', 'true');
        localStorage.setItem('audioPermissionGranted', granted.toString());

        if (granted) {
            console.log('✅ 用戶授予音效權限');
            this.enableAudioWithUserGesture();
        } else {
            console.log('❌ 用戶拒絕音效權限，啟用備用通知');
            this.enableFallbackNotifications();
        }

        this.updateAudioPermissionIndicator();
    };

    /**
     * 通過用戶手勢啟用音效
     */
    AudioManager.prototype.enableAudioWithUserGesture = function() {
        // 播放一個靜音音效來解鎖音效播放
        const silentAudio = new Audio();
        silentAudio.volume = 0;
        silentAudio.play().then(() => {
            console.log('🔊 音效播放已通過用戶手勢解鎖');
            this.userHasInteracted = true;
            this.processPendingNotifications();
        }).catch(error => {
            console.warn('⚠️ 音效解鎖失敗:', error);
            this.enableFallbackNotifications();
        });
    };

    /**
     * 啟用備用通知方法
     */
    AudioManager.prototype.enableFallbackNotifications = function() {
        this.fallbackNotificationsEnabled = true;

        // 請求瀏覽器通知權限
        this.requestBrowserNotificationPermission();

        console.log('🔔 備用通知方法已啟用');
    };

    /**
     * 請求瀏覽器通知權限
     */
    AudioManager.prototype.requestBrowserNotificationPermission = function() {
        if (!('Notification' in window)) {
            console.warn('⚠️ 此瀏覽器不支援通知');
            return;
        }

        if (Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                this.notificationPermission = permission;
                console.log('🔔 瀏覽器通知權限:', permission);
            });
        }
    };

    /**
     * 觸發備用通知
     */
    AudioManager.prototype.triggerFallbackNotification = function(audioData) {
        if (!this.fallbackNotificationsEnabled) return;

        // 瀏覽器通知
        this.showBrowserNotification();

        // 標題欄通知
        this.showTitleBarNotification();

        // 視覺指示器
        this.showVisualNotificationIndicator();
    };

    /**
     * 顯示瀏覽器通知
     */
    AudioManager.prototype.showBrowserNotification = function() {
        if (!('Notification' in window) || Notification.permission !== 'granted') {
            return;
        }

        const notification = new Notification('MCP Feedback Enhanced', {
            body: '有新訊息到達',
            icon: '/favicon.ico',
            tag: 'mcp-feedback-notification'
        });

        // 自動關閉通知
        setTimeout(() => {
            notification.close();
        }, 3000);
    };

    /**
     * 顯示標題欄通知
     */
    AudioManager.prototype.showTitleBarNotification = function() {
        if (this.titleBarNotificationActive) return;

        this.titleBarNotificationActive = true;
        let count = 0;

        const interval = setInterval(() => {
            document.title = count % 2 === 0 ? '🔔 新訊息 - MCP Feedback' : this.originalTitle;
            count++;

            if (count >= 6) { // 閃爍 3 次
                clearInterval(interval);
                document.title = this.originalTitle;
                this.titleBarNotificationActive = false;
            }
        }, 500);
    };

    /**
     * 顯示視覺通知指示器
     */
    AudioManager.prototype.showVisualNotificationIndicator = function() {
        // 創建或更新視覺指示器
        let indicator = document.getElementById('audioFallbackIndicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'audioFallbackIndicator';
            indicator.className = 'audio-fallback-indicator';
            indicator.innerHTML = `
                <div class="indicator-content">
                    <span class="indicator-icon">🔔</span>
                    <span class="indicator-text">新訊息通知</span>
                </div>
            `;
            document.body.appendChild(indicator);
        }

        indicator.classList.add('show');

        // 自動隱藏
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 3000);
    };

    /**
     * 顯示增強的自動播放被阻止通知
     */
    AudioManager.prototype.showEnhancedAutoplayBlockedNotification = function() {
        // 只顯示一次通知
        if (this.autoplayNotificationShown) return;
        this.autoplayNotificationShown = true;

        console.log('🔇 瀏覽器阻止音效自動播放，已啟用備用通知方法');

        // 顯示增強的通知
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            const message = window.i18nManager ?
                window.i18nManager.t('audio.autoplayBlockedEnhanced', '音效被阻止，已啟用視覺和瀏覽器通知') :
                '音效被阻止，已啟用視覺和瀏覽器通知';
            window.MCPFeedback.Utils.showMessage(message, 'info');
        }
    };

    /**
     * 更新音效權限狀態
     */
    AudioManager.prototype.updateAudioPermissionStatus = function(granted) {
        if (granted && !this.audioPermissionGranted) {
            this.audioPermissionGranted = true;
            localStorage.setItem('audioPermissionGranted', 'true');
            this.updateAudioPermissionIndicator();
            console.log('✅ 音效權限狀態已更新為已授予');
        }
    };

    /**
     * 獲取當前設定
     */
    AudioManager.prototype.getSettings = function() {
        return Utils.deepClone(this.currentAudioSettings);
    };

    /**
     * 創建音效權限指示器
     */
    AudioManager.prototype.createAudioPermissionIndicator = function() {
        // 檢查是否已存在
        if (document.getElementById('audioPermissionIndicator')) {
            return;
        }

        const indicator = document.createElement('div');
        indicator.id = 'audioPermissionIndicator';
        indicator.className = 'audio-permission-indicator';
        indicator.innerHTML = `
            <div class="indicator-content">
                <span class="indicator-icon">🔊</span>
                <span class="indicator-status">音效狀態</span>
                <button class="enable-audio-btn" style="display: none;">啟用音效</button>
            </div>
        `;

        // 添加點擊事件
        const enableBtn = indicator.querySelector('.enable-audio-btn');
        enableBtn.addEventListener('click', () => {
            this.requestAudioPermission();
        });

        // 添加到頁面（可以添加到設定區域或狀態欄）
        const targetContainer = document.querySelector('.quick-actions') || document.body;
        targetContainer.appendChild(indicator);

        this.updateAudioPermissionIndicator();
    };

    /**
     * 更新音效權限指示器
     */
    AudioManager.prototype.updateAudioPermissionIndicator = function() {
        const indicator = document.getElementById('audioPermissionIndicator');
        if (!indicator) return;

        const icon = indicator.querySelector('.indicator-icon');
        const status = indicator.querySelector('.indicator-status');
        const enableBtn = indicator.querySelector('.enable-audio-btn');

        if (this.audioPermissionGranted) {
            icon.textContent = '🔊';
            status.textContent = '音效已啟用';
            enableBtn.style.display = 'none';
            indicator.className = 'audio-permission-indicator enabled';
        } else if (this.audioPermissionRequested) {
            icon.textContent = '🔔';
            status.textContent = '使用備用通知';
            enableBtn.style.display = 'none';
            indicator.className = 'audio-permission-indicator fallback';
        } else {
            icon.textContent = '🔇';
            status.textContent = '音效未啟用';
            enableBtn.style.display = 'inline-block';
            indicator.className = 'audio-permission-indicator disabled';
        }
    };

    /**
     * 切換音效權限（用於設定頁面）
     */
    AudioManager.prototype.toggleAudioPermission = function() {
        if (this.audioPermissionGranted) {
            // 禁用音效
            this.audioPermissionGranted = false;
            localStorage.setItem('audioPermissionGranted', 'false');
            this.enableFallbackNotifications();
        } else {
            // 請求音效權限
            this.requestAudioPermission();
        }

        this.updateAudioPermissionIndicator();
    };

    /**
     * 重置音效權限（用於設定重置）
     */
    AudioManager.prototype.resetAudioPermission = function() {
        this.audioPermissionRequested = false;
        this.audioPermissionGranted = false;
        this.permissionDialogShown = false;
        this.fallbackNotificationsEnabled = false;

        localStorage.removeItem('audioPermissionRequested');
        localStorage.removeItem('audioPermissionGranted');

        this.updateAudioPermissionIndicator();
        console.log('🔄 音效權限已重置');
    };

    // 匯出到全域命名空間
    window.MCPFeedback.AudioManager = AudioManager;

})();
