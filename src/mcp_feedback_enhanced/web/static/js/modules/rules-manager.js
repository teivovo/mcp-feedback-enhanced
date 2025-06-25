/**
 * MCP Feedback Enhanced - 規則管理模組
 * =====================================
 * 
 * 提供訊息類型規則的管理介面，包括規則創建、編輯、刪除和測試功能
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};

    /**
     * 規則管理器
     */
    function RulesManager() {
        this.currentRules = [];
        this.selectedRule = null;
        this.isEditing = false;
        this.projectGroups = ['all', 'specific', 'exclude', 'regex'];
        
        // UI 元素
        this.container = null;
        this.rulesAccordion = null;
        this.ruleEditor = null;
        this.testPanel = null;
        
        // 回調函數
        this.onRuleChange = null;
        this.onRuleTest = null;
    }

    /**
     * 初始化規則管理器
     */
    RulesManager.prototype.initialize = function(containerId, options) {
        options = options || {};
        
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('❌ 找不到規則管理器容器:', containerId);
            return false;
        }

        this.onRuleChange = options.onRuleChange || null;
        this.onRuleTest = options.onRuleTest || null;

        this.createUI();
        this.loadRules();
        
        console.log('🔧 規則管理器初始化完成');
        return true;
    };

    /**
     * 創建 UI 介面
     */
    RulesManager.prototype.createUI = function() {
        this.container.innerHTML = `
            <div class="rules-manager">
                <div class="rules-header">
                    <h3>📋 訊息類型規則管理</h3>
                    <div class="rules-actions">
                        <button class="btn btn-primary" id="addRuleBtn">
                            <span class="btn-icon">➕</span>
                            新增規則
                        </button>
                        <button class="btn btn-secondary" id="importRulesBtn">
                            <span class="btn-icon">📥</span>
                            匯入規則
                        </button>
                        <button class="btn btn-secondary" id="exportRulesBtn">
                            <span class="btn-icon">📤</span>
                            匯出規則
                        </button>
                    </div>
                </div>
                
                <div class="rules-content">
                    <div class="rules-sidebar">
                        <div class="rules-accordion" id="rulesAccordion">
                            <!-- 規則手風琴將在這裡生成 -->
                        </div>
                    </div>
                    
                    <div class="rules-main">
                        <div class="rule-editor" id="ruleEditor">
                            <div class="editor-placeholder">
                                <div class="placeholder-icon">📝</div>
                                <div class="placeholder-text">選擇一個規則進行編輯，或點擊「新增規則」創建新規則</div>
                            </div>
                        </div>
                        
                        <div class="rule-test-panel" id="ruleTestPanel">
                            <h4>🧪 規則測試</h4>
                            <div class="test-inputs">
                                <div class="input-group">
                                    <label for="testMessageType">訊息類型:</label>
                                    <select id="testMessageType">
                                        <option value="general">General</option>
                                        <option value="code_review">Code Review</option>
                                        <option value="error_report">Error Report</option>
                                        <option value="feature_request">Feature Request</option>
                                        <option value="documentation">Documentation</option>
                                        <option value="testing">Testing</option>
                                        <option value="deployment">Deployment</option>
                                        <option value="security">Security</option>
                                    </select>
                                </div>
                                <div class="input-group">
                                    <label for="testProjectPath">專案路徑:</label>
                                    <input type="text" id="testProjectPath" value="/test/project" placeholder="輸入專案路徑">
                                </div>
                                <button class="btn btn-test" id="testRulesBtn">🎯 測試規則</button>
                            </div>
                            <div class="test-results" id="testResults">
                                <!-- 測試結果將在這裡顯示 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.setupEventListeners();
    };

    /**
     * 設置事件監聽器
     */
    RulesManager.prototype.setupEventListeners = function() {
        // 新增規則按鈕
        const addRuleBtn = document.getElementById('addRuleBtn');
        if (addRuleBtn) {
            addRuleBtn.addEventListener('click', () => {
                this.createNewRule();
            });
        }

        // 匯入規則按鈕
        const importRulesBtn = document.getElementById('importRulesBtn');
        if (importRulesBtn) {
            importRulesBtn.addEventListener('click', () => {
                this.importRules();
            });
        }

        // 匯出規則按鈕
        const exportRulesBtn = document.getElementById('exportRulesBtn');
        if (exportRulesBtn) {
            exportRulesBtn.addEventListener('click', () => {
                this.exportRules();
            });
        }

        // 測試規則按鈕
        const testRulesBtn = document.getElementById('testRulesBtn');
        if (testRulesBtn) {
            testRulesBtn.addEventListener('click', () => {
                this.testRules();
            });
        }
    };

    /**
     * 載入規則
     */
    RulesManager.prototype.loadRules = function() {
        // 模擬載入規則（實際應該從後端 API 載入）
        this.currentRules = [
            {
                id: "error_report_auto_submit",
                name: "Error Report Auto Submit",
                description: "Automatically submit error reports after 5 minutes",
                message_type: "error_report",
                rule_type: "auto_submit_override",
                value: true,
                timeout_override: 300,
                project_filter: { type: "all" },
                priority: 100,
                enabled: true
            },
            {
                id: "code_review_header",
                name: "Code Review Header",
                description: "Add standard header for code review responses",
                message_type: "code_review",
                rule_type: "response_header",
                value: "## Code Review Feedback\n\nThank you for the code review. Here are my responses:\n\n",
                project_filter: { type: "all" },
                priority: 50,
                enabled: true
            }
        ];

        this.renderRulesAccordion();
    };

    /**
     * 渲染規則手風琴
     */
    RulesManager.prototype.renderRulesAccordion = function() {
        const accordion = document.getElementById('rulesAccordion');
        if (!accordion) return;

        // 按專案分組規則
        const groupedRules = this.groupRulesByProject();
        
        accordion.innerHTML = '';
        
        Object.keys(groupedRules).forEach(groupKey => {
            const group = groupedRules[groupKey];
            const groupElement = this.createAccordionGroup(groupKey, group);
            accordion.appendChild(groupElement);
        });
    };

    /**
     * 按專案分組規則
     */
    RulesManager.prototype.groupRulesByProject = function() {
        const groups = {
            'all': { name: '所有專案', rules: [] },
            'specific': { name: '特定專案', rules: [] },
            'exclude': { name: '排除專案', rules: [] },
            'regex': { name: '正則表達式', rules: [] }
        };

        this.currentRules.forEach(rule => {
            const filterType = rule.project_filter?.type || 'all';
            if (groups[filterType]) {
                groups[filterType].rules.push(rule);
            } else {
                groups['all'].rules.push(rule);
            }
        });

        return groups;
    };

    /**
     * 創建手風琴分組
     */
    RulesManager.prototype.createAccordionGroup = function(groupKey, group) {
        const groupElement = document.createElement('div');
        groupElement.className = 'accordion-group';
        groupElement.innerHTML = `
            <div class="accordion-header" data-group="${groupKey}">
                <span class="group-icon">${this.getGroupIcon(groupKey)}</span>
                <span class="group-name">${group.name}</span>
                <span class="group-count">(${group.rules.length})</span>
                <span class="accordion-toggle">▼</span>
            </div>
            <div class="accordion-content">
                ${group.rules.map(rule => this.createRuleItem(rule)).join('')}
            </div>
        `;

        // 添加點擊事件
        const header = groupElement.querySelector('.accordion-header');
        header.addEventListener('click', () => {
            this.toggleAccordionGroup(groupElement);
        });

        return groupElement;
    };

    /**
     * 創建規則項目
     */
    RulesManager.prototype.createRuleItem = function(rule) {
        const statusIcon = rule.enabled ? '✅' : '❌';
        const typeIcon = this.getRuleTypeIcon(rule.rule_type);
        
        return `
            <div class="rule-item" data-rule-id="${rule.id}">
                <div class="rule-info">
                    <div class="rule-header">
                        <span class="rule-status">${statusIcon}</span>
                        <span class="rule-type-icon">${typeIcon}</span>
                        <span class="rule-name">${rule.name}</span>
                    </div>
                    <div class="rule-details">
                        <span class="rule-message-type">${rule.message_type}</span>
                        <span class="rule-priority">優先級: ${rule.priority}</span>
                    </div>
                </div>
                <div class="rule-actions">
                    <button class="btn-icon edit-rule" title="編輯規則">✏️</button>
                    <button class="btn-icon delete-rule" title="刪除規則">🗑️</button>
                </div>
            </div>
        `;
    };

    /**
     * 獲取分組圖標
     */
    RulesManager.prototype.getGroupIcon = function(groupKey) {
        const icons = {
            'all': '🌐',
            'specific': '📁',
            'exclude': '🚫',
            'regex': '🔍'
        };
        return icons[groupKey] || '📋';
    };

    /**
     * 獲取規則類型圖標
     */
    RulesManager.prototype.getRuleTypeIcon = function(ruleType) {
        const icons = {
            'auto_submit_override': '⏰',
            'timeout_override': '⏱️',
            'response_header': '📄',
            'response_footer': '📝',
            'template_override': '📋',
            'custom_config': '⚙️'
        };
        return icons[ruleType] || '🔧';
    };

    /**
     * 切換手風琴分組
     */
    RulesManager.prototype.toggleAccordionGroup = function(groupElement) {
        const content = groupElement.querySelector('.accordion-content');
        const toggle = groupElement.querySelector('.accordion-toggle');
        
        if (content.style.display === 'none' || !content.style.display) {
            content.style.display = 'block';
            toggle.textContent = '▲';
            groupElement.classList.add('expanded');
        } else {
            content.style.display = 'none';
            toggle.textContent = '▼';
            groupElement.classList.remove('expanded');
        }
    };

    /**
     * 創建新規則
     */
    RulesManager.prototype.createNewRule = function() {
        console.log('📝 創建新規則');
        this.selectedRule = null;
        this.isEditing = true;
        this.showRuleEditor();
    };

    /**
     * 顯示規則編輯器
     */
    RulesManager.prototype.showRuleEditor = function() {
        const editor = document.getElementById('ruleEditor');
        if (!editor) return;

        const rule = this.selectedRule || this.getDefaultRule();
        
        editor.innerHTML = `
            <div class="editor-content">
                <div class="editor-header">
                    <h4>${this.isEditing ? (this.selectedRule ? '編輯規則' : '新增規則') : '查看規則'}</h4>
                    <div class="editor-actions">
                        <button class="btn btn-primary" id="saveRuleBtn">💾 儲存</button>
                        <button class="btn btn-secondary" id="cancelEditBtn">❌ 取消</button>
                    </div>
                </div>
                
                <form class="rule-form" id="ruleForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="ruleName">規則名稱:</label>
                            <input type="text" id="ruleName" value="${rule.name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label for="ruleEnabled">啟用狀態:</label>
                            <select id="ruleEnabled">
                                <option value="true" ${rule.enabled ? 'selected' : ''}>啟用</option>
                                <option value="false" ${!rule.enabled ? 'selected' : ''}>停用</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="ruleMessageType">訊息類型:</label>
                            <select id="ruleMessageType" required>
                                <option value="general" ${rule.message_type === 'general' ? 'selected' : ''}>General</option>
                                <option value="code_review" ${rule.message_type === 'code_review' ? 'selected' : ''}>Code Review</option>
                                <option value="error_report" ${rule.message_type === 'error_report' ? 'selected' : ''}>Error Report</option>
                                <option value="feature_request" ${rule.message_type === 'feature_request' ? 'selected' : ''}>Feature Request</option>
                                <option value="documentation" ${rule.message_type === 'documentation' ? 'selected' : ''}>Documentation</option>
                                <option value="testing" ${rule.message_type === 'testing' ? 'selected' : ''}>Testing</option>
                                <option value="deployment" ${rule.message_type === 'deployment' ? 'selected' : ''}>Deployment</option>
                                <option value="security" ${rule.message_type === 'security' ? 'selected' : ''}>Security</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="ruleType">規則類型:</label>
                            <select id="ruleType" required>
                                <option value="auto_submit_override" ${rule.rule_type === 'auto_submit_override' ? 'selected' : ''}>自動提交覆蓋</option>
                                <option value="timeout_override" ${rule.rule_type === 'timeout_override' ? 'selected' : ''}>超時覆蓋</option>
                                <option value="response_header" ${rule.rule_type === 'response_header' ? 'selected' : ''}>回應標頭</option>
                                <option value="response_footer" ${rule.rule_type === 'response_footer' ? 'selected' : ''}>回應頁尾</option>
                                <option value="template_override" ${rule.rule_type === 'template_override' ? 'selected' : ''}>模板覆蓋</option>
                                <option value="custom_config" ${rule.rule_type === 'custom_config' ? 'selected' : ''}>自訂配置</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="ruleDescription">描述:</label>
                        <textarea id="ruleDescription" rows="2">${rule.description || ''}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="ruleValue">規則值:</label>
                        <textarea id="ruleValue" rows="3" placeholder="輸入規則值（JSON 格式或文字）">${this.formatRuleValue(rule.value)}</textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="rulePriority">優先級:</label>
                            <input type="number" id="rulePriority" value="${rule.priority || 50}" min="0" max="1000">
                        </div>
                        <div class="form-group">
                            <label for="timeoutOverride">超時覆蓋 (秒):</label>
                            <input type="number" id="timeoutOverride" value="${rule.timeout_override || ''}" min="0">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>專案篩選:</label>
                        <div class="project-filter-section">
                            <div class="filter-type-selector">
                                <label><input type="radio" name="filterType" value="all" ${(rule.project_filter?.type || 'all') === 'all' ? 'checked' : ''}> 所有專案</label>
                                <label><input type="radio" name="filterType" value="specific" ${rule.project_filter?.type === 'specific' ? 'checked' : ''}> 特定專案</label>
                                <label><input type="radio" name="filterType" value="exclude" ${rule.project_filter?.type === 'exclude' ? 'checked' : ''}> 排除專案</label>
                                <label><input type="radio" name="filterType" value="regex" ${rule.project_filter?.type === 'regex' ? 'checked' : ''}> 正則表達式</label>
                            </div>
                            <div class="filter-patterns" id="filterPatterns">
                                <textarea placeholder="輸入專案路徑模式，每行一個">${this.formatProjectPatterns(rule.project_filter)}</textarea>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        `;

        this.setupEditorEventListeners();
    };

    /**
     * 設置編輯器事件監聽器
     */
    RulesManager.prototype.setupEditorEventListeners = function() {
        // 儲存按鈕
        const saveBtn = document.getElementById('saveRuleBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveRule();
            });
        }

        // 取消按鈕
        const cancelBtn = document.getElementById('cancelEditBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelEdit();
            });
        }

        // 專案篩選類型變更
        const filterTypeInputs = document.querySelectorAll('input[name="filterType"]');
        filterTypeInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.updateFilterPatternsVisibility();
            });
        });

        this.updateFilterPatternsVisibility();
    };

    /**
     * 更新篩選模式可見性
     */
    RulesManager.prototype.updateFilterPatternsVisibility = function() {
        const selectedType = document.querySelector('input[name="filterType"]:checked')?.value;
        const patternsContainer = document.getElementById('filterPatterns');
        
        if (patternsContainer) {
            if (selectedType === 'all') {
                patternsContainer.style.display = 'none';
            } else {
                patternsContainer.style.display = 'block';
            }
        }
    };

    /**
     * 格式化規則值
     */
    RulesManager.prototype.formatRuleValue = function(value) {
        if (typeof value === 'object') {
            return JSON.stringify(value, null, 2);
        }
        return value || '';
    };

    /**
     * 格式化專案模式
     */
    RulesManager.prototype.formatProjectPatterns = function(projectFilter) {
        if (!projectFilter) return '';
        
        if (projectFilter.patterns && Array.isArray(projectFilter.patterns)) {
            return projectFilter.patterns.join('\n');
        }
        
        if (projectFilter.pattern) {
            return projectFilter.pattern;
        }
        
        return '';
    };

    /**
     * 獲取預設規則
     */
    RulesManager.prototype.getDefaultRule = function() {
        return {
            id: '',
            name: '',
            description: '',
            message_type: 'general',
            rule_type: 'auto_submit_override',
            value: false,
            priority: 50,
            enabled: true,
            project_filter: { type: 'all' }
        };
    };

    /**
     * 儲存規則
     */
    RulesManager.prototype.saveRule = function() {
        console.log('💾 儲存規則');
        // 實際實現應該調用後端 API
        this.isEditing = false;
        this.loadRules(); // 重新載入規則
    };

    /**
     * 取消編輯
     */
    RulesManager.prototype.cancelEdit = function() {
        console.log('❌ 取消編輯');
        this.isEditing = false;
        this.selectedRule = null;
        
        const editor = document.getElementById('ruleEditor');
        if (editor) {
            editor.innerHTML = `
                <div class="editor-placeholder">
                    <div class="placeholder-icon">📝</div>
                    <div class="placeholder-text">選擇一個規則進行編輯，或點擊「新增規則」創建新規則</div>
                </div>
            `;
        }
    };

    /**
     * 匯入規則
     */
    RulesManager.prototype.importRules = function() {
        console.log('📥 匯入規則');
        // 實際實現應該提供文件選擇對話框
    };

    /**
     * 匯出規則
     */
    RulesManager.prototype.exportRules = function() {
        console.log('📤 匯出規則');
        // 實際實現應該生成並下載 JSON 文件
    };

    /**
     * 測試規則
     */
    RulesManager.prototype.testRules = function() {
        const messageType = document.getElementById('testMessageType')?.value;
        const projectPath = document.getElementById('testProjectPath')?.value;
        
        console.log('🧪 測試規則:', messageType, projectPath);
        
        // 實際實現應該調用後端 API 進行測試
        const testResults = document.getElementById('testResults');
        if (testResults) {
            testResults.innerHTML = `
                <div class="test-result">
                    <h5>測試結果:</h5>
                    <p>訊息類型: ${messageType}</p>
                    <p>專案路徑: ${projectPath}</p>
                    <p>匹配規則: 2 條</p>
                </div>
            `;
        }
    };

    // 將 RulesManager 加入命名空間
    window.MCPFeedback.RulesManager = RulesManager;

})();
