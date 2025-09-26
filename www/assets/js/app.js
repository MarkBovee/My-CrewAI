// CrewAI Flow Control Center JavaScript
class FlowControlCenter {
    constructor() {
        this.currentFlow = null;
        this.isExecuting = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateFlowStats();
        this.bindKnowledgeEvents();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(item.dataset.section);
            });
        });

        // Modal events
        this.bindModalEvents();

        // Flow execution
        document.getElementById('execute-flow')?.addEventListener('click', () => {
            this.executeFlow();
        });

        // Cancel flow
        document.getElementById('cancel-flow')?.addEventListener('click', () => {
            this.closeModal('flow-modal');
        });

        // Experience flow execution
        document.getElementById('execute-experience-flow')?.addEventListener('click', () => {
            this.executeExperienceFlow();
        });

        // Cancel experience flow
        document.getElementById('cancel-experience-flow')?.addEventListener('click', () => {
            this.closeModal('experience-flow-modal');
        });
    }

    bindKnowledgeEvents() {
        // Knowledge management events
        document.getElementById('reset-topics')?.addEventListener('click', () => {
            this.resetKnowledge('topics');
        });

        document.getElementById('reset-web')?.addEventListener('click', () => {
            this.resetKnowledge('web');
        });

        document.getElementById('reset-all')?.addEventListener('click', () => {
            this.resetKnowledge('all');
        });

        document.getElementById('check-topic-btn')?.addEventListener('click', () => {
            this.checkTopic();
        });

        document.getElementById('refresh-knowledge-stats')?.addEventListener('click', () => {
            this.loadKnowledgeStats();
        });

        // Load stats when settings section is activated
        const settingsNav = document.querySelector('[data-section="settings"]');
        if (settingsNav) {
            settingsNav.addEventListener('click', () => {
                setTimeout(() => this.loadKnowledgeStats(), 100);
            });
        }
    }

    bindModalEvents() {
        // Close modals
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal.id);
            });
        });

        // Close modal on background click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal[style*="block"]');
                if (openModal) {
                    this.closeModal(openModal.id);
                }
            }
        });
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        const targetSection = document.getElementById(`${section}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update page title
        const titles = {
            flows: 'Flow Management',
            agents: 'Agent Configuration',
            tasks: 'Task Management',
            outputs: 'Output History',
            settings: 'Settings'
        };
        
        const titleElement = document.querySelector('.page-title');
        if (titleElement && titles[section]) {
            titleElement.textContent = titles[section];
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            
            // Reset modal content
            if (modalId === 'flow-modal') {
                this.resetFlowModal();
            }
        }
    }

    resetFlowModal() {
        const executionLog = document.getElementById('execution-log');
        if (executionLog) {
            executionLog.style.display = 'none';
            executionLog.querySelector('.log-content').innerHTML = '';
        }
        
        const executeBtn = document.getElementById('execute-flow');
        if (executeBtn) {
            executeBtn.disabled = false;
            executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute';
        }
        
        this.isExecuting = false;
    }

    async executeFlow() {
        if (this.isExecuting) return;

        const topic = document.getElementById('flow-topic').value.trim();
        
        if (!topic) {
            this.showNotification('Please enter a topic for the flow', 'error');
            return;
        }

        this.isExecuting = true;
        const executeBtn = document.getElementById('execute-flow');
        const executionLog = document.getElementById('execution-log');
        const logContent = executionLog.querySelector('.log-content');

        // Update UI
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<div class="loading"></div> Executing...';
        executionLog.style.display = 'block';
        logContent.innerHTML = 'Initializing flow execution...\n';

        try {
            // Start flow execution
            this.appendLog('🚀 Starting Create New Post Flow');
            this.appendLog(`📋 Topic: ${topic}`);
            this.appendLog('='.repeat(60));
            
            const response = await fetch('/api/execute-flow', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flow_name: this.currentFlow,
                    topic: topic
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.handleFlowEvent(data);
                        } catch (e) {
                            // Ignore parsing errors for incomplete chunks
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Flow execution error:', error);
            this.appendLog(`❌ Error: ${error.message}`, 'error');
            this.showNotification('Flow execution failed', 'error');
        } finally {
            this.isExecuting = false;
            executeBtn.disabled = false;
            executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute';
        }
    }

    handleFlowEvent(data) {
        switch (data.type) {
            case 'log':
                this.appendLog(data.message, data.level);
                break;
            case 'progress':
                this.appendLog(`⏳ ${data.step}: ${data.message}`);
                break;
            case 'success':
                this.appendLog('✅ Flow completed successfully!', 'success');
                this.appendLog(`📁 Output saved to: ${data.output_file}`);
                this.showNotification('Flow executed successfully!', 'success');
                this.updateFlowStats();
                break;
            case 'error':
                this.appendLog(`❌ Error: ${data.message}`, 'error');
                this.showNotification('Flow execution failed', 'error');
                break;
        }
    }

    appendLog(message, level = 'info') {
        const logContent = document.querySelector('#execution-log .log-content');
        if (!logContent) return;

        const timestamp = new Date().toLocaleTimeString();
        const levelIcon = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️'
        }[level] || 'ℹ️';

        const logLine = `[${timestamp}] ${levelIcon} ${message}\n`;
        logContent.innerHTML += logLine;
        logContent.scrollTop = logContent.scrollHeight;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    updateFlowStats() {
        // This would typically fetch real stats from the server
        // For now, we'll simulate some updates
        const stats = {
            executions: Math.floor(Math.random() * 20) + 10,
            successRate: Math.floor(Math.random() * 10) + 90,
            avgRuntime: (Math.random() * 2 + 1).toFixed(1)
        };

        // Update stat cards
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length >= 2) {
            statCards[1].querySelector('h3').textContent = stats.executions;
            statCards[2].querySelector('h3').textContent = `${stats.successRate}%`;
            statCards[3].querySelector('h3').textContent = `${stats.avgRuntime}s`;
        }
    }

    async loadFlowPlots() {
        try {
            const response = await fetch('/api/flow-plots');
            const plots = await response.json();
            
            // Update flow cards with plot availability
            plots.forEach(plot => {
                const flowCard = document.querySelector(`[data-flow="${plot.flow_name}"]`);
                if (flowCard) {
                    const plotBtn = flowCard.querySelector('.btn-outline');
                    if (plotBtn) {
                        plotBtn.disabled = false;
                        plotBtn.onclick = () => this.viewFlowPlot(plot.flow_name);
                    }
                }
            });
        } catch (error) {
            console.error('Failed to load flow plots:', error);
        }
    }

    // Knowledge Management Methods
    async loadKnowledgeStats() {
        try {
            const response = await fetch('/api/knowledge/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateKnowledgeStatsDisplay(data.data);
            } else {
                console.error('Failed to load knowledge stats:', data.error);
            }
        } catch (error) {
            console.error('Error loading knowledge stats:', error);
        }
    }

    updateKnowledgeStatsDisplay(stats) {
        const statsContainer = document.getElementById('knowledge-stats');
        if (!statsContainer) return;

        statsContainer.innerHTML = `
            <div class="knowledge-stat-grid">
                <div class="knowledge-stat-item">
                    <h4>Total Articles</h4>
                    <span class="stat-value">${stats.total_articles}</span>
                </div>
                <div class="knowledge-stat-item">
                    <h4>Web Results</h4>
                    <span class="stat-value">${stats.total_web_results}</span>
                </div>
                <div class="knowledge-stat-item">
                    <h4>Topic Memory</h4>
                    <span class="stat-value">${stats.topics_in_memory}</span>
                </div>
                <div class="knowledge-stat-item">
                    <h4>Last Updated</h4>
                    <span class="stat-value">${stats.last_updated || 'Never'}</span>
                </div>
            </div>
        `;
    }

    async resetKnowledge(type) {
        if (!confirm(`Are you sure you want to reset ${type} knowledge data? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch('/api/knowledge/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: type })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                this.loadKnowledgeStats(); // Refresh stats
            } else {
                this.showNotification(`Reset failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error resetting knowledge:', error);
            this.showNotification('Reset failed: Network error', 'error');
        }
    }

    async checkTopic() {
        const topicInput = document.getElementById('topic-check-input');
        const resultsDiv = document.getElementById('topic-check-results');
        
        if (!topicInput || !topicInput.value.trim()) {
            this.showNotification('Please enter a topic to check', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/knowledge/check-topic', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic: topicInput.value.trim() })
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayTopicCheckResults(data.data, resultsDiv);
            } else {
                this.showNotification(`Topic check failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error checking topic:', error);
            this.showNotification('Topic check failed: Network error', 'error');
        }
    }

    displayTopicCheckResults(results, container) {
        if (!container) return;

        const { is_covered, similarity_score, similar_topics } = results;
        
        container.innerHTML = `
            <div class="topic-check-result ${is_covered ? 'covered' : 'new'}">
                <h4>${is_covered ? '⚠️ Topic Already Covered' : '✅ New Topic'}</h4>
                <p><strong>Similarity Score:</strong> ${(similarity_score * 100).toFixed(1)}%</p>
                ${similar_topics.length > 0 ? `
                    <div class="similar-topics">
                        <h5>Similar Topics Found:</h5>
                        <ul>
                            ${similar_topics.map(topic => `<li>${topic}</li>`).join('')}
                        </ul>
                    </div>
                ` : '<p>No similar topics found in memory.</p>'}
            </div>
        `;
    }

    async executeExperienceFlow() {
        if (this.isExecuting) return;

        const experienceText = document.getElementById('experience-text').value.trim();
        
        if (!experienceText) {
            this.showNotification('Please enter your personal experience text', 'error');
            return;
        }

        if (experienceText.length < 50) {
            this.showNotification('Please provide a more detailed experience (at least 50 characters)', 'warning');
            return;
        }

        this.isExecuting = true;
        const executeBtn = document.getElementById('execute-experience-flow');
        const executionLog = document.getElementById('experience-execution-log');
        const logContent = executionLog.querySelector('.log-content');

        // Update UI
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<div class="loading"></div> Transforming...';
        executionLog.style.display = 'block';
        logContent.innerHTML = 'Initializing experience blog flow...\n';

        try {
            // Start experience flow execution
            this.appendExperienceLog('🚀 Starting Create Blog From Experience Flow');
            this.appendExperienceLog(`📝 Experience Text Length: ${experienceText.length} characters`);
            this.appendExperienceLog('='.repeat(60));
            
            const response = await fetch('/api/execute-flow', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flow_name: 'create_blog_from_experience_flow',
                    experience_text: experienceText
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.handleExperienceFlowEvent(data);
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Flow execution error:', error);
            this.appendExperienceLog(`❌ Error: ${error.message}`, 'error');
            this.showNotification('Experience flow execution failed', 'error');
        } finally {
            this.isExecuting = false;
            executeBtn.disabled = false;
            executeBtn.innerHTML = '<i class="fas fa-magic"></i> Transform Experience';
        }
    }

    handleExperienceFlowEvent(data) {
        switch (data.type) {
            case 'log':
                this.appendExperienceLog(data.message, data.level);
                break;
            case 'progress':
                this.appendExperienceLog(`⏳ ${data.step}: ${data.message}`);
                break;
            case 'success':
                this.appendExperienceLog('✅ Experience blog flow completed successfully!', 'success');
                this.appendExperienceLog(`📁 Output saved to: ${data.output_file}`);
                this.showNotification('Experience blog created successfully!', 'success');
                this.updateFlowStats();
                break;
            case 'error':
                this.appendExperienceLog(`❌ Error: ${data.message}`, 'error');
                this.showNotification('Experience blog flow failed', 'error');
                break;
        }
    }

    appendExperienceLog(message, level = 'info') {
        const logContent = document.querySelector('#experience-execution-log .log-content');
        if (!logContent) return;

        const timestamp = new Date().toLocaleTimeString();
        const levelIcon = {
            'info': 'ℹ️',
            'debug': '🔍',
            'error': '❌',
            'warning': '⚠️',
            'success': '✅'
        }[level] || 'ℹ️';

        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${level}`;
        logEntry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${levelIcon} ${message}`;
        
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    }
}

// Global functions for HTML onclick handlers
function runFlow(flowName) {
    const flowModal = document.getElementById('flow-modal');
    const modalFlowName = document.getElementById('modal-flow-name');
    
    if (modalFlowName) {
        modalFlowName.textContent = flowName;
    }
    
    window.flowControl.currentFlow = flowName;
    window.flowControl.showModal('flow-modal');
}

function viewFlowPlot(flowName) {
    const plotModal = document.getElementById('plot-modal');
    const plotFlowName = document.getElementById('plot-flow-name');
    const plotIframe = document.getElementById('plot-iframe');
    
    if (plotFlowName) {
        plotFlowName.textContent = flowName;
    }
    
    if (plotIframe) {
        plotIframe.src = `plots/${flowName}_plot.html`;
    }
    
    window.flowControl.showModal('plot-modal');
}

// Function for experience blog flow
function runExperienceFlow() {
    window.flowControl.showModal('experience-flow-modal');
}

// CSS for notifications
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 300px;
    z-index: 3000;
    animation: slideInRight 0.3s ease;
    box-shadow: var(--shadow);
}

.notification-success {
    border-left: 4px solid var(--success-color);
    color: var(--success-color);
}

.notification-error {
    border-left: 4px solid var(--error-color);
    color: var(--error-color);
}

.notification-info {
    border-left: 4px solid var(--primary-color);
    color: var(--primary-color);
}

.notification-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 18px;
    margin-left: auto;
    padding: 0;
}

.notification-close:hover {
    color: var(--primary-color);
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

// Add notification styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.flowControl = new FlowControlCenter();
    
    // Load flow plots on startup
    window.flowControl.loadFlowPlots();
    
    console.log('CrewAI Flow Control Center initialized');
});