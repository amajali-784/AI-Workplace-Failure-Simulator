#!/usr/bin/env python
"""
Enhanced FastAPI server with ULTRA-modern HTML UI.
Showcases ALL features: Role selection, mood tracking, urgency visualization, reward breakdown, etc.
"""
from __future__ import annotations

import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from env.environment import Action, WorkplaceEnv

app = FastAPI(title="workplace-simulator", version="1.0")

_env = None

def get_env() -> WorkplaceEnv:
    global _env
    if _env is None:
        _env = WorkplaceEnv()
    return _env


# ============ API ENDPOINTS ============

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/reset")
def reset():
    env = get_env()
    obs = env.reset()
    return obs


@app.get("/state")
def state():
    env = get_env()
    return env.state()


@app.post("/step")
def step(action: Action):
    env = get_env()
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }


# ============ ULTRA ENHANCED UI ============

@app.get("/")
def root():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Workplace Failure Simulator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1500px;
            margin: 0 auto;
            background: white;
            border-radius: 24px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.4);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            color: white;
            padding: 50px;
            text-align: center;
            position: relative;
        }
        
        .header h1 {
            font-size: 3em;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.3em;
            opacity: 0.95;
        }
        
        .content { padding: 40px; }
        
        .config-panel {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 25px;
            border-radius: 18px;
            margin-bottom: 30px;
        }
        
        .config-panel h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .config-row {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .config-item {
            flex: 1;
            min-width: 200px;
        }
        
        .config-item label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
        }
        
        .config-item select, .config-item input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            transition: border 0.3s;
        }
        
        .config-item select:focus, .config-item input:focus {
            border-color: #667eea;
            outline: none;
        }
        
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 18px;
            text-align: center;
            transition: all 0.3s;
            border: 3px solid transparent;
        }
        
        .status-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .status-card .icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .status-card .label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
        }
        
        .status-card .value {
            font-size: 2em;
            font-weight: 700;
            color: #333;
        }
        
        .urgency-bar {
            background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
            padding: 25px;
            border-radius: 18px;
            margin-bottom: 30px;
        }
        
        .urgency-bar h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .urgency-item {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            background: white;
            padding: 12px;
            border-radius: 10px;
        }
        
        .urgency-label {
            flex: 0 0 120px;
            font-weight: 600;
        }
        
        .urgency-progress {
            flex: 1;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 0 15px;
        }
        
        .urgency-fill {
            height: 100%;
            background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
            transition: width 0.5s;
        }
        
        .urgency-value {
            flex: 0 0 50px;
            text-align: right;
            font-weight: 700;
            font-size: 1.2em;
        }
        
        .mood-tracker {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 25px;
            border-radius: 18px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .mood-emoji {
            font-size: 4em;
            margin-bottom: 10px;
        }
        
        .mood-label {
            font-size: 1.5em;
            font-weight: 700;
            color: #333;
        }
        
        .action-panel {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 30px;
            border-radius: 18px;
            margin-bottom: 30px;
        }
        
        .action-panel h3 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .action-btn {
            padding: 20px;
            border: 3px solid transparent;
            border-radius: 15px;
            cursor: pointer;
            font-weight: 700;
            font-size: 1.1em;
            transition: all 0.3s;
            text-align: center;
        }
        
        .action-btn.email {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        }
        
        .action-btn.bug {
            background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
        }
        
        .action-btn.meeting {
            background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        }
        
        .action-btn:hover {
            transform: scale(1.05);
            border-color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .action-btn.selected {
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.3);
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #555;
        }
        
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 12px;
            font-size: 15px;
            font-family: inherit;
        }
        
        .input-group input:focus, .input-group textarea:focus {
            border-color: #667eea;
            outline: none;
        }
        
        .control-buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .ctrl-btn {
            flex: 1;
            min-width: 150px;
            padding: 18px;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .ctrl-btn.start { background: #10b981; color: white; }
        .ctrl-btn.step { background: #667eea; color: white; }
        .ctrl-btn.auto { background: #f59e0b; color: white; }
        .ctrl-btn.reset { background: #ef4444; color: white; }
        
        .ctrl-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        
        .ctrl-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .reward-breakdown {
            background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
            padding: 25px;
            border-radius: 18px;
            margin-bottom: 30px;
        }
        
        .reward-breakdown h3 {
            margin-bottom: 15px;
        }
        
        .reward-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: white;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .episode-log {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 18px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .log-entry {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        .log-entry.success { border-left-color: #10b981; }
        .log-entry.warning { border-left-color: #f59e0b; }
        .log-entry.error { border-left-color: #ef4444; }
        
        .log-time {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .log-message {
            font-weight: 600;
            color: #333;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Workplace Failure Simulator</h1>
            <p>Can AI survive a real job? Test task prioritization, crisis management & emotional intelligence!</p>
        </div>
        
        <div class="content">
            <!-- Configuration Panel -->
            <div class="config-panel">
                <h3>⚙️ Environment Configuration</h3>
                <div class="config-row">
                    <div class="config-item">
                        <label>Role</label>
                        <select id="role">
                            <option value="Software Engineer">👨‍💻 Software Engineer</option>
                            <option value="Customer Support">🎧 Customer Support</option>
                            <option value="Product Manager">📊 Product Manager</option>
                        </select>
                    </div>
                    <div class="config-item">
                        <label>Mode</label>
                        <select id="mode">
                            <option value="normal">🌟 Normal</option>
                            <option value="stress">🔥 Stress</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Status Dashboard -->
            <div class="status-bar">
                <div class="status-card">
                    <div class="icon">⏱️</div>
                    <div class="label">Time Step</div>
                    <div class="value" id="time">0</div>
                </div>
                <div class="status-card">
                    <div class="icon">⭐</div>
                    <div class="label">Total Reward</div>
                    <div class="value" id="reward">0.00</div>
                </div>
                <div class="status-card">
                    <div class="icon">✅</div>
                    <div class="label">Tasks Done</div>
                    <div class="value" id="completed">0/3</div>
                </div>
                <div class="status-card">
                    <div class="icon">🎯</div>
                    <div class="label">Progress</div>
                    <div class="value" id="progress">0%</div>
                </div>
                <div class="status-card">
                    <div class="icon">🔄</div>
                    <div class="label">Loop Count</div>
                    <div class="value" id="loops">0</div>
                </div>
                <div class="status-card">
                    <div class="icon">🎭</div>
                    <div class="label">Mood</div>
                    <div class="value" id="mood">😐</div>
                </div>
            </div>
            
            <!-- Urgency Visualization -->
            <div class="urgency-bar">
                <h3>📊 Task Urgency Levels</h3>
                <div id="urgency-display">
                    <div class="urgency-item">
                        <div class="urgency-label">📧 Email</div>
                        <div class="urgency-progress">
                            <div class="urgency-fill" id="urgency-email" style="width: 60%"></div>
                        </div>
                        <div class="urgency-value" id="urgency-email-val">3</div>
                    </div>
                    <div class="urgency-item">
                        <div class="urgency-label">🐛 Bug</div>
                        <div class="urgency-progress">
                            <div class="urgency-fill" id="urgency-bug" style="width: 40%"></div>
                        </div>
                        <div class="urgency-value" id="urgency-bug-val">2</div>
                    </div>
                    <div class="urgency-item">
                        <div class="urgency-label">📅 Meeting</div>
                        <div class="urgency-progress">
                            <div class="urgency-fill" id="urgency-meeting" style="width: 20%"></div>
                        </div>
                        <div class="urgency-value" id="urgency-meeting-val">1</div>
                    </div>
                </div>
            </div>
            
            <!-- Mood Tracker -->
            <div class="mood-tracker">
                <div class="mood-emoji" id="mood-emoji">😐</div>
                <div class="mood-label" id="mood-text">Normal</div>
            </div>
            
            <!-- KPI Dashboard -->
            <div class="kpi-dashboard" id="kpi-section" style="display: none;">
                <h3>📊 KPI Performance Dashboard</h3>
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-icon">✅</div>
                        <div class="kpi-value" id="kpi-tasks">0</div>
                        <div class="kpi-label">Tasks Completed</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">⚡</div>
                        <div class="kpi-value" id="kpi-efficiency">0.00</div>
                        <div class="kpi-label">Efficiency Score</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-icon">🏆</div>
                        <div class="kpi-value" id="kpi-status">-</div>
                        <div class="kpi-label">Performance Status</div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Summary -->
            <div class="performance-summary" id="perf-summary" style="display: none;">
                <h3>📈 Episode Performance Summary</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-label">Total Steps:</span>
                        <span class="summary-value" id="sum-steps">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Total Reward:</span>
                        <span class="summary-value" id="sum-reward">0.00</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Tasks Completed:</span>
                        <span class="summary-value" id="sum-tasks">0/3</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Mood Transitions:</span>
                        <span class="summary-value" id="sum-mood">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Loops Detected:</span>
                        <span class="summary-value" id="sum-loops">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Mistakes Made:</span>
                        <span class="summary-value" id="sum-mistakes">0</span>
                    </div>
                </div>
            </div>
            
            <!-- Action Panel -->
            <div class="action-panel">
                <h3>🎮 Take Action</h3>
                <div class="action-buttons">
                    <button class="action-btn email" onclick="selectAction('email')">
                        📧 Handle Email<br>
                        <small>Client communication</small>
                    </button>
                    <button class="action-btn bug" onclick="selectAction('bug')">
                        🐛 Fix Bug<br>
                        <small>Critical outage</small>
                    </button>
                    <button class="action-btn meeting" onclick="selectAction('meeting')">
                        📅 Attend Meeting<br>
                        <small>Team sync</small>
                    </button>
                </div>
                
                <div class="input-group">
                    <label>Reasoning (required - explain your decision)</label>
                    <textarea id="reason" rows="3" placeholder="Why are you choosing this action? Mention urgency, deadlines, priorities..."></textarea>
                </div>
                
                <div class="input-group">
                    <label>Confidence (0.0 - 1.0, optional)</label>
                    <input type="number" id="confidence" min="0" max="1" step="0.05" placeholder="0.85">
                </div>
                
                <div class="control-buttons">
                    <button class="ctrl-btn start" onclick="startEpisode()">🚀 Start Episode</button>
                    <button class="ctrl-btn step" onclick="takeStep()" id="stepBtn" disabled>▶️ Take Step</button>
                    <button class="ctrl-btn auto" onclick="autoPlay()" id="autoBtn" disabled>⚡ Auto Play</button>
                    <button class="ctrl-btn reset" onclick="resetEnv()">🔄 Reset</button>
                </div>
            </div>
            
            <!-- Reward Breakdown -->
            <div class="reward-breakdown" id="reward-breakdown" style="display: none;">
                <h3>💰 Reward Breakdown</h3>
                <div id="reward-items"></div>
            </div>
            
            <!-- Episode Log -->
            <div class="episode-log">
                <h3>📜 Episode Log</h3>
                <div id="log"></div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedAction = null;
        let totalReward = 0;
        let episodeActive = false;
        
        function selectAction(action) {
            selectedAction = action;
            document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('selected'));
            event.target.closest('.action-btn').classList.add('selected');
            document.getElementById('stepBtn').disabled = false;
        }
        
        async function startEpisode() {
            const role = document.getElementById('role').value;
            const mode = document.getElementById('mode').value;
            
            const response = await fetch('/reset', { method: 'POST' });
            const data = await response.json();
            
            episodeActive = true;
            totalReward = 0;
            updateState(data);
            addLog('🚀 Episode started!', 'success');
            document.getElementById('stepBtn').disabled = false;
            document.getElementById('autoBtn').disabled = false;
        }
        
        async function takeStep() {
            if (!selectedAction) {
                alert('Please select an action first!');
                return;
            }
            
            const reason = document.getElementById('reason').value;
            const confidence = document.getElementById('confidence').value;
            
            const payload = {
                action: selectedAction,
                reason: reason || "No reason provided"
            };
            
            if (confidence) {
                payload.confidence = parseFloat(confidence);
            }
            
            const response = await fetch('/step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            totalReward += data.reward;
            
            updateState(data.observation);
            showRewardBreakdown(data.info);
            
            const emoji = data.reward > 0 ? '✅' : '❌';
            addLog(`${emoji} Action: ${selectedAction} | Reward: ${data.reward.toFixed(2)} | Total: ${totalReward.toFixed(2)}`, 
                   data.reward > 0 ? 'success' : 'error');
            
            if (data.info.reward_breakdown) {
                console.log('Reward breakdown:', data.info.reward_breakdown);
            }
            
            if (data.done) {
                episodeActive = false;
                addLog('🏁 Episode completed!', 'success');
                document.getElementById('stepBtn').disabled = true;
                document.getElementById('autoBtn').disabled = true;
            }
        }
        
        function updateState(state) {
            document.getElementById('time').textContent = state.time;
            document.getElementById('reward').textContent = totalReward.toFixed(2);
            document.getElementById('completed').textContent = `${state.completed?.length || 0}/3`;
            document.getElementById('progress').textContent = `${Math.round((state.completed?.length || 0) / 3 * 100)}%`;
            document.getElementById('loops').textContent = state.loop_count || 0;
            
            // Update urgency
            if (state.urgency) {
                document.getElementById('urgency-email').style.width = `${(state.urgency.email || 0) * 20}%`;
                document.getElementById('urgency-email-val').textContent = state.urgency.email || 0;
                document.getElementById('urgency-bug').style.width = `${(state.urgency.bug || 0) * 20}%`;
                document.getElementById('urgency-bug-val').textContent = state.urgency.bug || 0;
                document.getElementById('urgency-meeting').style.width = `${(state.urgency.meeting || 0) * 20}%`;
                document.getElementById('urgency-meeting-val').textContent = state.urgency.meeting || 0;
            }
            
            // Update mood
            const moodEmojis = {
                'normal': '😐',
                'angry_client': '😡',
                'recovered': '😊'
            };
            const mood = state.mood || 'normal';
            document.getElementById('mood').textContent = moodEmojis[mood] || '😐';
            document.getElementById('mood-emoji').textContent = moodEmojis[mood] || '😐';
            document.getElementById('mood-text').textContent = mood.replace('_', ' ').toUpperCase();
        }
        
        function showRewardBreakdown(info) {
            const breakdown = info.reward_breakdown;
            if (!breakdown || Object.keys(breakdown).length === 0) return;
            
            const container = document.getElementById('reward-breakdown');
            const items = document.getElementById('reward-items');
            items.innerHTML = '';
            
            for (const [key, value] of Object.entries(breakdown)) {
                const div = document.createElement('div');
                div.className = 'reward-item';
                div.innerHTML = `
                    <span>${key.replace(/_/g, ' ').toUpperCase()}</span>
                    <span style="font-weight: 700; color: ${value > 0 ? '#10b981' : '#ef4444'}">
                        ${value > 0 ? '+' : ''}${value.toFixed(2)}
                    </span>
                `;
                items.appendChild(div);
            }
            
            container.style.display = 'block';
        }
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            
            const time = new Date().toLocaleTimeString();
            entry.innerHTML = `
                <div class="log-time">${time}</div>
                <div class="log-message">${message}</div>
            `;
            
            log.insertBefore(entry, log.firstChild);
        }
        
        async function autoPlay() {
            const actions = ['email', 'bug', 'meeting'];
            const reasons = [
                'Highest urgency task with approaching deadline',
                'Critical system outage affecting all users',
                'Important stakeholder alignment meeting'
            ];
            
            for (let i = 0; i < 3; i++) {
                if (!episodeActive) break;
                
                selectedAction = actions[i];
                document.getElementById('reason').value = reasons[i];
                document.getElementById('confidence').value = '0.85';
                
                await takeStep();
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        
        async function resetEnv() {
            episodeActive = false;
            totalReward = 0;
            selectedAction = null;
            
            document.getElementById('time').textContent = '0';
            document.getElementById('reward').textContent = '0.00';
            document.getElementById('completed').textContent = '0/3';
            document.getElementById('progress').textContent = '0%';
            document.getElementById('loops').textContent = '0';
            document.getElementById('mood').textContent = '😐';
            document.getElementById('mood-emoji').textContent = '😐';
            document.getElementById('mood-text').textContent = 'NORMAL';
            
            document.getElementById('urgency-email').style.width = '60%';
            document.getElementById('urgency-email-val').textContent = '3';
            document.getElementById('urgency-bug').style.width = '40%';
            document.getElementById('urgency-bug-val').textContent = '2';
            document.getElementById('urgency-meeting').style.width = '20%';
            document.getElementById('urgency-meeting-val').textContent = '1';
            
            document.getElementById('reward-breakdown').style.display = 'none';
            document.getElementById('log').innerHTML = '';
            document.getElementById('stepBtn').disabled = true;
            document.getElementById('autoBtn').disabled = true;
            
            document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('selected'));
            
            addLog('🔄 Environment reset', 'warning');
        }
    </script>
</body>
</html>
""")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
