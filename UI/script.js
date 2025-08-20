// AI Control Tower - Frontend JavaScript
// Handles API integration, dynamic content, and user interactions

class AIControlTowerUI {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.currentResults = null;
        this.init();
    }

    init() {
        this.attachEventListeners();
        this.loadInitialState();
    }

    attachEventListeners() {
        // Form submission
        document.getElementById('baseline-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateBaselines();
        });

        // Clear button
        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearForm();
        });

        // Sample queries
        window.loadSample = (type) => {
            this.loadSampleData(type);
        };

        // Export functions
        window.exportResults = (format) => {
            this.exportResults(format);
        };

        window.copyToClipboard = () => {
            this.copyResultsToClipboard();
        };

        window.retryAnalysis = () => {
            this.generateBaselines();
        };

        // Category modal functions
        window.showCategoryDetails = (category) => {
            this.showCategoryModal(category);
        };

        window.closeModal = () => {
            this.closeModal();
        };

        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.id === 'category-modal') {
                this.closeModal();
            }
        });

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    loadInitialState() {
        this.showWelcomeState();
    }

    showWelcomeState() {
        document.getElementById('welcome-state').style.display = 'block';
        document.getElementById('results-display').style.display = 'none';
        document.getElementById('error-display').style.display = 'none';
    }

    showLoadingState() {
        document.getElementById('welcome-state').style.display = 'none';
        document.getElementById('results-display').style.display = 'none';
        document.getElementById('error-display').style.display = 'none';
        document.getElementById('loading-state').style.display = 'block';
        
        // Animate progress steps
        this.animateProgressSteps();
    }

    animateProgressSteps() {
        const steps = document.querySelectorAll('.step');
        let currentStep = 0;
        
        const activateStep = () => {
            if (currentStep < steps.length) {
                steps.forEach((step, index) => {
                    step.classList.toggle('active', index <= currentStep);
                });
                currentStep++;
                setTimeout(activateStep, 1500);
            }
        };
        
        // Reset all steps first
        steps.forEach(step => step.classList.remove('active'));
        setTimeout(activateStep, 500);
    }

    showResultsState() {
        document.getElementById('welcome-state').style.display = 'none';
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('error-display').style.display = 'none';
        document.getElementById('results-display').style.display = 'block';
    }

    showErrorState(error) {
        document.getElementById('welcome-state').style.display = 'none';
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('results-display').style.display = 'none';
        document.getElementById('error-display').style.display = 'block';
        
        document.getElementById('error-message').textContent = error;
    }

    async generateBaselines() {
        const formData = new FormData(document.getElementById('baseline-form'));
        const data = {
            user_query: formData.get('user_query'),
            document_content: formData.get('document_content')
        };

        // Validate inputs
        if (!data.user_query.trim()) {
            this.showErrorState('Please enter a user query.');
            return;
        }

        if (!data.document_content.trim()) {
            this.showErrorState('Please enter agent documentation.');
            return;
        }

        this.showLoadingState();

        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze/baseline`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'API request failed');
            }

            if (!result.success) {
                throw new Error(result.error || 'Analysis failed');
            }

            this.currentResults = result;
            this.displayResults(result);
            
        } catch (error) {
            console.error('Error generating baselines:', error);
            this.showErrorState(error.message || 'Failed to generate baselines. Please try again.');
        }
    }

    displayResults(results) {
        this.showResultsState();
        
        // Display execution summary
        this.displayExecutionSummary(results);
        
        // Display calculated baselines
        this.displayBaselines(results.calculated_baselines);
        
        // Display insights
        this.displayInsights(results.insights);
        
        // Display readiness assessment
        this.displayReadinessAssessment(results.readiness_assessment);
    }

    displayExecutionSummary(results) {
        const summaryContainer = document.getElementById('execution-summary');
        const executionTime = results.execution_time || 0;
        const metricsCount = Object.keys(results.calculated_baselines || {}).length;
        
        summaryContainer.innerHTML = `
            <div class="summary-card">
                <h5>Execution Time</h5>
                <div class="value">${executionTime.toFixed(2)}s</div>
            </div>
            <div class="summary-card">
                <h5>Metrics Generated</h5>
                <div class="value">${metricsCount}</div>
            </div>
            <div class="summary-card">
                <h5>Analysis Status</h5>
                <div class="value">Complete</div>
            </div>
            <div class="summary-card">
                <h5>Timestamp</h5>
                <div class="value">${new Date(results.timestamp).toLocaleString()}</div>
            </div>
        `;
    }

    displayBaselines(baselines) {
        const baselinesContainer = document.getElementById('baselines-display');
        
        if (!baselines || Object.keys(baselines).length === 0) {
            baselinesContainer.innerHTML = '<p>No baselines generated.</p>';
            return;
        }

        const baselineItems = Object.entries(baselines).map(([key, baseline]) => {
            const progress = this.calculateProgress(baseline.recommended, baseline.min, baseline.max);
            const displayName = this.formatMetricName(key);
            const unit = this.getMetricUnit(key);
            
            return `
                <div class="baseline-item">
                    <div class="baseline-header">
                        <div class="baseline-name">${displayName}</div>
                        <div class="baseline-value">${baseline.recommended}${unit}</div>
                    </div>
                    <div class="baseline-range">Range: ${baseline.min} - ${baseline.max}${unit}</div>
                    <div class="baseline-progress">
                        <div class="baseline-progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <div class="baseline-rationale">${baseline.rationale}</div>
                </div>
            `;
        }).join('');

        baselinesContainer.innerHTML = baselineItems;
    }

    displayInsights(insights) {
        const insightsContainer = document.getElementById('insights-display');
        
        if (!insights || Object.keys(insights).length === 0) {
            insightsContainer.innerHTML = '<p>No insights generated.</p>';
            return;
        }

        const categoryIcons = {
            technical_insights: 'fas fa-microchip',
            operational_insights: 'fas fa-tasks',
            business_insights: 'fas fa-chart-pie',
            recommendations: 'fas fa-lightbulb'
        };

        const insightCategories = Object.entries(insights).map(([category, items]) => {
            if (!items || items.length === 0) return '';
            
            const icon = categoryIcons[category] || 'fas fa-info-circle';
            const title = this.formatCategoryName(category);
            
            const listItems = items.map(item => `<li>${item}</li>`).join('');
            
            return `
                <div class="insight-category">
                    <h5><i class="${icon}"></i> ${title}</h5>
                    <ul>${listItems}</ul>
                </div>
            `;
        }).filter(Boolean).join('');

        insightsContainer.innerHTML = insightCategories;
    }

    displayReadinessAssessment(readiness) {
        const readinessContainer = document.getElementById('readiness-display');
        
        if (!readiness || Object.keys(readiness).length === 0) {
            readinessContainer.innerHTML = '<p>No readiness assessment available.</p>';
            return;
        }

        const readinessItems = Object.entries(readiness).map(([key, level]) => {
            const displayName = this.formatMetricName(key);
            const levelClass = level.toLowerCase();
            
            return `
                <div class="readiness-item ${levelClass}">
                    <div class="readiness-label">${displayName}</div>
                    <div class="readiness-value">${level}</div>
                </div>
            `;
        }).join('');

        readinessContainer.innerHTML = readinessItems;
    }

    calculateProgress(value, min, max) {
        if (min === max) return 100;
        return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
    }

    formatMetricName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatCategoryName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getMetricUnit(metricName) {
        const percentageMetrics = [
            'tool_utilization',
            'task_escalation_rate',
            'first_contact_resolution',
            'improvement_velocity',
            'customer_satisfaction_improvement'
        ];
        
        if (percentageMetrics.includes(metricName)) {
            return '%';
        }
        
        if (metricName === 'cost_savings_roi') {
            return 'x';
        }
        
        return '';
    }

    loadSampleData(type) {
        const samples = {
            'customer-service': {
                query: 'Create baseline metrics for a customer service agent handling technical support',
                document: `Customer Service Agent Specification:
- Handles technical support for cloud services
- Uses knowledge base, ticketing system, and escalation tools  
- Expected to resolve 75% of issues on first contact
- Domain: Mature cloud service support with well-established processes
- Task complexity: Mix of simple account issues and complex technical problems
- Performance targets: <15% escalation rate, >70% CSAT`
            },
            'research-agent': {
                query: 'Generate baselines for an AI research assistant in emerging technology domains',
                document: `Research Assistant Agent Specification:
- Conducts complex research in emerging AI and ML domains
- Uses experimental search tools, academic databases, and analysis frameworks
- Expected to provide comprehensive insights for novel research questions
- Domain: New and rapidly evolving technology landscape
- Task complexity: Highly specialized research with novel methodologies
- Performance targets: >80% accuracy in research synthesis, <20% false positive rate`
            },
            'sales-agent': {
                query: 'Establish performance baselines for a sales automation agent',
                document: `Sales Automation Agent Specification:
- Manages lead qualification and initial customer outreach
- Uses CRM integration, email automation, and lead scoring tools
- Expected to qualify 60% of leads without human intervention
- Domain: Established B2B sales processes with proven methodologies  
- Task complexity: Mix of simple lead scoring and complex qualification conversations
- Performance targets: >60% lead qualification rate, <10% escalation to human sales reps`
            }
        };

        const sample = samples[type];
        if (sample) {
            document.getElementById('user-query').value = sample.query;
            document.getElementById('document-content').value = sample.document;
        }
    }

    clearForm() {
        document.getElementById('baseline-form').reset();
        this.showWelcomeState();
    }

    exportResults(format) {
        if (!this.currentResults) {
            alert('No results to export. Please run an analysis first.');
            return;
        }

        switch (format) {
            case 'json':
                this.exportAsJSON();
                break;
            case 'pdf':
                this.exportAsPDF();
                break;
            default:
                console.error('Unsupported export format:', format);
        }
    }

    exportAsJSON() {
        const dataStr = JSON.stringify(this.currentResults, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `ai-control-tower-baseline-${Date.now()}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    exportAsPDF() {
        // For PDF export, we'll create a printable version
        const printWindow = window.open('', '_blank');
        const printContent = this.generatePrintableReport();
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Control Tower - Baseline Analysis Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 2cm; line-height: 1.6; }
                    h1, h2, h3 { color: #2c3e50; }
                    .header { text-align: center; border-bottom: 2px solid #667eea; padding-bottom: 1rem; margin-bottom: 2rem; }
                    .section { margin-bottom: 2rem; page-break-inside: avoid; }
                    .baseline-item { margin-bottom: 1rem; padding: 1rem; border: 1px solid #e9ecef; border-radius: 8px; }
                    .baseline-name { font-weight: bold; color: #2c3e50; }
                    .baseline-value { color: #667eea; font-weight: bold; }
                    .insights ul { list-style-type: disc; margin-left: 2rem; }
                    .readiness-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
                    @media print { body { margin: 1cm; } }
                </style>
            </head>
            <body>
                ${printContent}
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => {
            printWindow.print();
        }, 250);
    }

    generatePrintableReport() {
        const results = this.currentResults;
        const date = new Date(results.timestamp).toLocaleString();
        
        let html = `
            <div class="header">
                <h1>AI Control Tower - Baseline Analysis Report</h1>
                <p>Generated on: ${date}</p>
                <p>Query: ${results.user_query}</p>
            </div>
        `;

        // Calculated Baselines
        html += '<div class="section"><h2>Calculated Baselines</h2>';
        Object.entries(results.calculated_baselines || {}).forEach(([key, baseline]) => {
            const displayName = this.formatMetricName(key);
            const unit = this.getMetricUnit(key);
            html += `
                <div class="baseline-item">
                    <div class="baseline-name">${displayName}</div>
                    <div class="baseline-value">Recommended: ${baseline.recommended}${unit}</div>
                    <div>Range: ${baseline.min} - ${baseline.max}${unit}</div>
                    <div><em>${baseline.rationale}</em></div>
                </div>
            `;
        });
        html += '</div>';

        // Insights
        if (results.insights) {
            html += '<div class="section"><h2>Key Insights</h2>';
            Object.entries(results.insights).forEach(([category, items]) => {
                if (items && items.length > 0) {
                    const title = this.formatCategoryName(category);
                    html += `<h3>${title}</h3><ul>`;
                    items.forEach(item => {
                        html += `<li>${item}</li>`;
                    });
                    html += '</ul>';
                }
            });
            html += '</div>';
        }

        // Readiness Assessment
        if (results.readiness_assessment) {
            html += '<div class="section"><h2>Readiness Assessment</h2><div class="readiness-grid">';
            Object.entries(results.readiness_assessment).forEach(([key, level]) => {
                const displayName = this.formatMetricName(key);
                html += `<div><strong>${displayName}:</strong> ${level.toUpperCase()}</div>`;
            });
            html += '</div></div>';
        }

        return html;
    }

    copyResultsToClipboard() {
        if (!this.currentResults) {
            alert('No results to copy. Please run an analysis first.');
            return;
        }

        const textContent = this.generateTextReport();
        
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textContent).then(() => {
                this.showCopySuccess();
            }).catch(err => {
                console.error('Failed to copy to clipboard:', err);
                this.fallbackCopy(textContent);
            });
        } else {
            this.fallbackCopy(textContent);
        }
    }

    fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showCopySuccess();
        } catch (err) {
            console.error('Fallback copy failed:', err);
            alert('Failed to copy to clipboard. Please copy manually.');
        }
        
        document.body.removeChild(textArea);
    }

    showCopySuccess() {
        const button = document.querySelector('button[onclick="copyToClipboard()"]');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        button.style.background = '#28a745';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.background = '';
        }, 2000);
    }

    generateTextReport() {
        const results = this.currentResults;
        const date = new Date(results.timestamp).toLocaleString();
        
        let report = `AI CONTROL TOWER - BASELINE ANALYSIS REPORT\n`;
        report += `Generated on: ${date}\n`;
        report += `Query: ${results.user_query}\n\n`;

        report += `CALCULATED BASELINES:\n`;
        report += `${'='.repeat(50)}\n`;
        Object.entries(results.calculated_baselines || {}).forEach(([key, baseline]) => {
            const displayName = this.formatMetricName(key);
            const unit = this.getMetricUnit(key);
            report += `${displayName}: ${baseline.recommended}${unit}\n`;
            report += `  Range: ${baseline.min} - ${baseline.max}${unit}\n`;
            report += `  Rationale: ${baseline.rationale}\n\n`;
        });

        if (results.insights) {
            report += `KEY INSIGHTS:\n`;
            report += `${'='.repeat(50)}\n`;
            Object.entries(results.insights).forEach(([category, items]) => {
                if (items && items.length > 0) {
                    const title = this.formatCategoryName(category);
                    report += `\n${title}:\n`;
                    items.forEach(item => {
                        report += `• ${item}\n`;
                    });
                }
            });
        }

        if (results.readiness_assessment) {
            report += `\nREADINESS ASSESSMENT:\n`;
            report += `${'='.repeat(50)}\n`;
            Object.entries(results.readiness_assessment).forEach(([key, level]) => {
                const displayName = this.formatMetricName(key);
                report += `${displayName}: ${level.toUpperCase()}\n`;
            });
        }

        return report;
    }

    showCategoryModal(category) {
        const modal = document.getElementById('category-modal');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');
        
        const categoryData = this.getCategoryData(category);
        
        title.innerHTML = `<i class="${categoryData.icon}"></i> ${categoryData.title}`;
        body.innerHTML = categoryData.content;
        
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        const modal = document.getElementById('category-modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    getCategoryData(category) {
        const categories = {
            technical: {
                icon: 'fas fa-microchip',
                title: 'Technical Metrics',
                content: `
                    <h4>Overview</h4>
                    <p>Technical metrics measure the core performance characteristics of the agent's processing capabilities and tool utilization efficiency.</p>
                    
                    <h4>Key Metrics</h4>
                    <ul>
                        <li><strong>Trajectory Complexity:</strong> Number of reasoning steps required to complete tasks</li>
                        <li><strong>Tool Utilization:</strong> Percentage of effective tool usage during task execution</li>
                    </ul>
                    
                    <h4>Baseline Ranges</h4>
                    <ul>
                        <li><strong>Simple Queries:</strong> 20-30 trajectory complexity</li>
                        <li><strong>Complex Multi-step:</strong> 40-60 trajectory complexity</li>
                        <li><strong>Highly Specialized:</strong> 60-80 trajectory complexity</li>
                    </ul>
                    
                    <p>These metrics help evaluate the agent's computational efficiency and reasoning depth.</p>
                `
            },
            operational: {
                icon: 'fas fa-tasks',
                title: 'Operational KPIs',
                content: `
                    <h4>Overview</h4>
                    <p>Operational KPIs measure day-to-day performance and effectiveness in handling user requests and task completion.</p>
                    
                    <h4>Key Metrics</h4>
                    <ul>
                        <li><strong>Task Escalation Rate:</strong> Percentage of tasks requiring human intervention</li>
                        <li><strong>First Contact Resolution:</strong> Percentage of issues resolved on first interaction</li>
                    </ul>
                    
                    <h4>Baseline Ranges</h4>
                    <ul>
                        <li><strong>Simple Tasks:</strong> 5-10% escalation rate</li>
                        <li><strong>Complex Tasks:</strong> 15-25% escalation rate</li>
                        <li><strong>Novel Tasks:</strong> 25-40% escalation rate</li>
                    </ul>
                    
                    <p>These KPIs directly impact user satisfaction and operational efficiency.</p>
                `
            },
            learning: {
                icon: 'fas fa-graduation-cap',
                title: 'Learning & Safety Metrics',
                content: `
                    <h4>Overview</h4>
                    <p>Learning and safety metrics track the agent's ability to improve over time while maintaining compliance with safety guidelines.</p>
                    
                    <h4>Key Metrics</h4>
                    <ul>
                        <li><strong>Improvement Velocity:</strong> Rate of performance improvement over time</li>
                        <li><strong>Guardrail Violations:</strong> Frequency of safety or compliance breaches</li>
                    </ul>
                    
                    <h4>Baseline Ranges</h4>
                    <ul>
                        <li><strong>Stable Domain:</strong> 3-5% improvement velocity</li>
                        <li><strong>Evolving Domain:</strong> 5-10% improvement velocity</li>
                        <li><strong>New Domain:</strong> 10-20% improvement velocity</li>
                    </ul>
                    
                    <p>These metrics ensure continuous improvement while maintaining safety standards.</p>
                `
            },
            business: {
                icon: 'fas fa-chart-pie',
                title: 'Business Metrics',
                content: `
                    <h4>Overview</h4>
                    <p>Business metrics measure the tangible value and ROI delivered by the agent implementation.</p>
                    
                    <h4>Key Metrics</h4>
                    <ul>
                        <li><strong>Cost Savings ROI:</strong> Return on investment multiplier</li>
                        <li><strong>Customer Satisfaction Improvement:</strong> Increase in customer satisfaction scores</li>
                    </ul>
                    
                    <h4>Baseline Ranges</h4>
                    <ul>
                        <li><strong>High Automation Potential:</strong> 5-10x ROI</li>
                        <li><strong>Medium Automation:</strong> 2-5x ROI</li>
                        <li><strong>Low Automation:</strong> 1-2x ROI</li>
                    </ul>
                    
                    <p>These metrics demonstrate business value and justify continued investment.</p>
                `
            }
        };
        
        return categories[category] || {
            icon: 'fas fa-info-circle',
            title: 'Category Information',
            content: '<p>Category information not available.</p>'
        };
    }
}

// Initialize the UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.aiControlTowerUI = new AIControlTowerUI();
});

// Global utility functions
window.smoothScrollTo = (targetId) => {
    const target = document.getElementById(targetId);
    if (target) {
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape key to close modal
    if (e.key === 'Escape') {
        const modal = document.getElementById('category-modal');
        if (modal.style.display === 'flex') {
            window.closeModal();
        }
    }
    
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('baseline-form');
        if (form && !document.getElementById('loading-state').style.display) {
            form.dispatchEvent(new Event('submit'));
        }
    }
});