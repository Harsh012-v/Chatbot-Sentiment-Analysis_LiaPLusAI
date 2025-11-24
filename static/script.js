// Modern JavaScript for Chatbot Web Interface

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');
const endBtn = document.getElementById('endBtn');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('closeSidebar');
const analysisModal = document.getElementById('analysisModal');
const closeModal = document.getElementById('closeModal');
const modalBody = document.getElementById('modalBody');
const sidebarContent = document.getElementById('sidebarContent');

let isConversationEnded = false;
let sessionId = localStorage.getItem('chatbot_session_id') || null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    
    // Initialize session ID if not exists
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('chatbot_session_id', sessionId);
    }
    
    // Remove welcome message after first message
    messageInput.addEventListener('input', () => {
        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg && messageInput.value.trim()) {
            welcomeMsg.style.display = 'none';
        }
    });
});

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Send message
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isConversationEnded) return;
    
    // Disable input
    messageInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    messageInput.value = '';
    
    // Show loading
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        // Remove loading
        removeLoadingMessage(loadingId);
        
        // Update session ID if provided
        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem('chatbot_session_id', sessionId);
        }
        
        if (data.type === 'end_conversation') {
            // End conversation
            addMessageToChat('bot', data.message);
            showAnalysis(data.analysis);
            isConversationEnded = true;
        } else if (data.type === 'message') {
            // Add bot response with sentiment
            addMessageToChat('bot', data.bot_message, data.sentiment);
        } else if (data.error) {
            addMessageToChat('bot', `Error: ${data.error}`, null, true);
        }
    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessageToChat('bot', `Error: ${error.message}`, null, true);
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

function addMessageToChat(sender, text, sentiment = null, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    if (isError) {
        bubble.style.background = 'rgba(248, 113, 113, 0.2)';
        bubble.style.borderColor = 'var(--negative-color)';
    }
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = text;
    
    bubble.appendChild(messageText);
    
    // Add sentiment indicator for user messages
    if (sentiment && sender === 'user') {
        const sentimentDiv = document.createElement('div');
        sentimentDiv.className = `sentiment-indicator ${sentiment.label.toLowerCase()}`;
        
        const sentimentText = document.createElement('span');
        sentimentText.innerHTML = `
            <i class="fas fa-${getSentimentIcon(sentiment.label)}"></i>
            <span>Sentiment: ${sentiment.label}</span>
            <span class="sentiment-score">(${sentiment.score >= 0 ? '+' : ''}${sentiment.score.toFixed(2)})</span>
        `;
        
        if (sentiment.emotion && sentiment.emotion !== 'neutral') {
            sentimentText.innerHTML += `
                <span class="emotion-badge">
                    ${sentiment.emotion_emoji} ${sentiment.emotion.charAt(0).toUpperCase() + sentiment.emotion.slice(1)}
                </span>
            `;
        }
        
        sentimentDiv.appendChild(sentimentText);
        messageDiv.appendChild(sentimentDiv);
    }
    
    // Add timestamp
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString();
    bubble.appendChild(timeDiv);
    
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Remove welcome message if exists
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
}

function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.id = 'loading-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    
    bubble.appendChild(loadingDiv);
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return 'loading-message';
}

function removeLoadingMessage(id) {
    const loadingMsg = document.getElementById(id);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

function getSentimentIcon(label) {
    switch(label.toLowerCase()) {
        case 'positive':
            return 'smile';
        case 'negative':
            return 'frown';
        default:
            return 'meh';
    }
}

// Reset conversation
resetBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to reset the conversation?')) {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update session ID
                if (data.session_id) {
                    sessionId = data.session_id;
                    localStorage.setItem('chatbot_session_id', sessionId);
                }
                
                // Clear chat
                chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <h2>Conversation Reset!</h2>
                        <p>Start a new conversation.</p>
                    </div>
                `;
                
                sidebarContent.innerHTML = `
                    <div class="analysis-placeholder">
                        <i class="fas fa-chart-bar"></i>
                        <p>Conversation analysis will appear here after you end the conversation.</p>
                    </div>
                `;
                
                isConversationEnded = false;
                messageInput.focus();
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
});

// End conversation
endBtn.addEventListener('click', async () => {
    if (confirm('End conversation and view analysis?')) {
        try {
            const response = await fetch('/api/end_conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAnalysis(data.analysis);
                isConversationEnded = true;
                messageInput.disabled = true;
                sendBtn.disabled = true;
            } else if (data.error) {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
});

function showAnalysis(analysis) {
    // Show in modal
    modalBody.innerHTML = generateAnalysisHTML(analysis);
    analysisModal.classList.add('active');
    
    // Also update sidebar
    sidebarContent.innerHTML = generateAnalysisHTML(analysis, true);
}

function generateAnalysisHTML(analysis, isSidebar = false) {
    const overallSentiment = analysis.overall_sentiment || 'Neutral';
    const sentimentClass = overallSentiment.toLowerCase();
    
    let html = `
        <div class="analysis-card">
            <h4><i class="fas fa-chart-pie"></i> Overall Sentiment</h4>
            <div class="stat-item">
                <span class="stat-label">Sentiment</span>
                <span class="stat-value ${sentimentClass}">${overallSentiment}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Average Score</span>
                <span class="stat-value">${(analysis.average_score || 0).toFixed(3)}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Messages</span>
                <span class="stat-value">${analysis.total_messages || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Duration</span>
                <span class="stat-value">${formatDuration(analysis.duration || 0)}</span>
            </div>
        </div>
        
        <div class="analysis-card">
            <h4><i class="fas fa-info-circle"></i> Reasoning</h4>
            <p style="color: var(--text-secondary); line-height: 1.6;">${analysis.reasoning || 'No reasoning available'}</p>
        </div>
    `;
    
    if (analysis.label_distribution) {
        html += `
            <div class="analysis-card">
                <h4><i class="fas fa-chart-bar"></i> Sentiment Distribution</h4>
                <div class="stat-item">
                    <span class="stat-label">Positive</span>
                    <span class="stat-value positive">${analysis.label_distribution.Positive || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Negative</span>
                    <span class="stat-value negative">${analysis.label_distribution.Negative || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Neutral</span>
                    <span class="stat-value neutral">${analysis.label_distribution.Neutral || 0}</span>
                </div>
            </div>
        `;
    }
    
    if (analysis.trend_analysis) {
        html += `
            <div class="analysis-card">
                <h4><i class="fas fa-chart-line"></i> Trend Analysis</h4>
                <div class="stat-item">
                    <span class="stat-label">Trend</span>
                    <span class="stat-value">${analysis.trend_analysis.trend || 'N/A'}</span>
                </div>
                <p style="color: var(--text-secondary); margin-top: 1rem; line-height: 1.6;">
                    ${analysis.trend_analysis.description || 'No trend data available'}
                </p>
                ${analysis.trend_analysis.insights ? `
                    <div style="margin-top: 1rem;">
                        <h5 style="color: var(--text-secondary); margin-bottom: 0.5rem;">Key Insights:</h5>
                        <ul style="color: var(--text-secondary); padding-left: 1.5rem; line-height: 1.8;">
                            ${analysis.trend_analysis.insights.map(insight => `<li>${insight}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    if (analysis.emotion_analysis) {
        html += `
            <div class="analysis-card">
                <h4><i class="fas fa-smile"></i> Emotion Analysis</h4>
                <div class="stat-item">
                    <span class="stat-label">Dominant Emotion</span>
                    <span class="stat-value">${analysis.emotion_analysis.dominant_emotion || 'N/A'}</span>
                </div>
                ${analysis.emotion_analysis.emotion_distribution ? `
                    <div style="margin-top: 1rem;">
                        <h5 style="color: var(--text-secondary); margin-bottom: 0.5rem;">Distribution:</h5>
                        ${Object.entries(analysis.emotion_analysis.emotion_distribution)
                            .filter(([_, count]) => count > 0)
                            .map(([emotion, count]) => `
                                <div class="stat-item">
                                    <span class="stat-label">${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</span>
                                    <span class="stat-value">${count}</span>
                                </div>
                            `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Add sentiment chart if we have scores
    if (analysis.sentiment_scores && analysis.sentiment_scores.length > 0) {
        html += `
            <div class="analysis-card">
                <h4><i class="fas fa-chart-area"></i> Sentiment Progression</h4>
                <canvas id="sentimentChart" width="400" height="200"></canvas>
            </div>
        `;
    }
    
    return html;
}

function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(1)} seconds`;
    } else if (seconds < 3600) {
        return `${(seconds / 60).toFixed(1)} minutes`;
    } else {
        return `${(seconds / 3600).toFixed(1)} hours`;
    }
}

// Close sidebar
closeSidebar.addEventListener('click', () => {
    sidebar.style.display = 'none';
});

// Close modal
closeModal.addEventListener('click', () => {
    analysisModal.classList.remove('active');
});

// Close modal on outside click
analysisModal.addEventListener('click', (e) => {
    if (e.target === analysisModal) {
        analysisModal.classList.remove('active');
    }
});

// Draw sentiment chart if Chart.js is available
function drawSentimentChart(scores) {
    // This would require Chart.js library
    // For now, we'll skip this or add it later
    console.log('Sentiment scores for chart:', scores);
}

