#!/usr/bin/env python
"""
Professional FastAPI server with enterprise-grade HTML UI.
Modern, polished, production-ready interface.
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


# ============ PROFESSIONAL UI ============

@app.get("/")
def root():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Workplace Failure Simulator | OpenEnv</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--gray-50);
            color: var(--gray-800);
            line-height: 1.6;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 2rem 0;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 1;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }
        
        .header h1 {
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: -0.025em;
        }
        
        .header-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Main Layout */
        .main {
            padding: 2rem 0;
        }
        
        .grid {
            display: grid;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .grid-2 { grid-template-columns: repeat(2, 1fr); }
        .grid-3 { grid-template-columns: repeat(3, 1fr); }
        .grid-4 { grid-template-columns: repeat(4, 1fr); }
        .grid-6 { grid-template-columns: repeat(6, 1fr); }
        
        @media (max-width: 1024px) {
            .grid-4, .grid-6 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3 { grid-template-columns: 1fr; }
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            padding: 1.5rem;
            border: 1px solid var(--gray-200);
            transition: all 0.2s;
        }
        
        .card:hover {
            box-shadow: var(--shadow-lg);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--gray-100);
        }
        
        .card-title {
            font-size: 1.125rem;
            font-weight: 700;
            color: var(--gray-800);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Stat Cards */
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--gray-200);
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .stat-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            color: var(--gray-900);
            line-height: 1;
        }
        
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        /* Configuration Panel */
        .config-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .form-label {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--gray-700);
        }
        
        .form-select, .form-input, .form-textarea {
            padding: 0.75rem 1rem;
            border: 1px solid var(--gray-300);
            border-radius: 8px;
            font-size: 0.875rem;
            font-family: inherit;
            transition: all 0.2s;
            background: white;
        }
        
        .form-select:focus, .form-input:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        
        .form-textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        /* Action Buttons */
        .action-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .action-btn {
            padding: 1.25rem;
            border: 2px solid var(--gray-200);
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }
        
        .action-btn:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .action-btn.selected {
            border-color: var(--primary);
            background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }
        
        .action-btn-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .action-btn-label {
            font-weight: 700;
            font-size: 1rem;
            color: var(--gray-800);
            margin-bottom: 0.25rem;
        }
        
        .action-btn-desc {
            font-size: 0.75rem;
            color: var(--gray-600);
        }
        
        /* Control Buttons */
        .control-group {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover:not(:disabled) {
            background: var(--primary-dark);
            box-shadow: var(--shadow-md);
        }
        
        .btn-success {
            background: var(--success);
            color: white;
        }
        
        .btn-warning {
            background: var(--warning);
            color: white;
        }
        
        .btn-danger {
            background: var(--danger);
            color: white;
        }
        
        /* Progress Bars */
        .progress-item {
            margin-bottom: 1rem;
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }
        
        .progress-label {
            font-weight: 600;
            color: var(--gray-700);
        }
        
        .progress-value {
            font-weight: 700;
            color: var(--gray-900);
        }
        
        .progress-bar {
            height: 12px;
            background: var(--gray-200);
            border-radius: 9999px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
            transition: width 0.5s ease;
            border-radius: 9999px;
        }
        
        /* Mood Display */
        .mood-display {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 12px;
            border: 2px solid #fbbf24;
        }
        
        .mood-emoji {
            font-size: 4rem;
            margin-bottom: 0.5rem;
        }
        
        .mood-text {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gray-800);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Reward Breakdown */
        .reward-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .reward-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background: var(--gray-50);
            border-radius: 8px;
            border-left: 3px solid var(--gray-300);
        }
        
        .reward-item.positive {
            border-left-color: var(--success);
            background: #ecfdf5;
        }
        
        .reward-item.negative {
            border-left-color: var(--danger);
            background: #fef2f2;
        }
        
        .reward-name {
            font-weight: 600;
            font-size: 0.875rem;
            color: var(--gray-700);
        }
        
        .reward-value {
            font-weight: 700;
            font-size: 1rem;
        }
        
        .reward-value.positive { color: var(--success); }
        .reward-value.negative { color: var(--danger); }
        
        /* Episode Log */
        .log-container {
            max-height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .log-entry {
            padding: 0.75rem 1rem;
            background: var(--gray-50);
            border-radius: 8px;
            border-left: 3px solid var(--gray-300);
            font-size: 0.875rem;
        }
        
        .log-entry.success { border-left-color: var(--success); background: #ecfdf5; }
        .log-entry.warning { border-left-color: var(--warning); background: #fffbeb; }
        .log-entry.error { border-left-color: var(--danger); background: #fef2f2; }
        .log-entry.info { border-left-color: var(--info); background: #eff6ff; }
        
        .log-time {
            font-size: 0.75rem;
            color: var(--gray-600);
            margin-bottom: 0.25rem;
        }
        
        .log-message {
            color: var(--gray-800);
            font-weight: 500;
        }
        
        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }
        
        .kpi-card {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            border: 2px solid #bae6fd;
        }
        
        .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            color: var(--gray-900);
            margin-bottom: 0.25rem;
        }
        
        .kpi-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Badge */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
        .badge-info { background: #dbeafe; color: #1e40af; }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: var(--gray-600);
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        .empty-state-text {
            font-size: 1.125rem;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div>
                    <h1>🤖 AI Workplace Failure Simulator</h1>
                    <p style="opacity: 0.9; margin-top: 0.5rem;">OpenEnv Environment • Test AI Agent Capabilities</p>
                </div>
                <div class="header-badge">
                    <span>🟢</span>
                    <span>System Online</span>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main">
        <div class="container">
            <!-- Configuration -->
            <div class="grid grid-2">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">⚙️ Configuration</div>
                    </div>
                    <div class="config-form">
                        <div class="form-group">
                            <label class="form-label">Role</label>
                            <select class="form-select" id="role">
                                <option value="Software Engineer">👨‍💻 Software Engineer</option>
                                <option value="Customer Support">🎧 Customer Support</option>
                                <option value="Product Manager">📊 Product Manager</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Mode</label>
                            <select class="form-select" id="mode">
                                <option value="normal">🌟 Normal Mode</option>
                                <option value="stress">🔥 Stress Mode</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Mood Display -->
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🎭 Emotional State</div>
                    </div>
                    <div class="mood-display">
                        <div class="mood-emoji" id="mood-emoji">😐</div>
                        <div class="mood-text" id="mood-text">Normal</div>
                    </div>
                </div>
            </div>
            
            <!-- Stats Grid -->
            <div class="grid grid-6">
                <div class="stat-card">
                    <div class="stat-icon">⏱️</div>
                    <div class="stat-label">Time Step</div>
                    <div class="stat-value" id="stat-time">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-label">Total Reward</div>
                    <div class="stat-value" id="stat-reward">0.00</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-label">Completed</div>
                    <div class="stat-value" id="stat-completed">0/3</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-label">Progress</div>
                    <div class="stat-value" id="stat-progress">0%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🔄</div>
                    <div class="stat-label">Loops</div>
                    <div class="stat-value" id="stat-loops">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-label">Efficiency</div>
                    <div class="stat-value" id="stat-efficiency">0.00</div>
                </div>
            </div>
            
            <!-- Task Urgency -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📊 Task Priority Levels</div>
                    <span class="badge badge-info">Real-time</span>
                </div>
                <div class="progress-item">
                    <div class="progress-header">
                        <span class="progress-label">📧 Email Management</span>
                        <span class="progress-value" id="urgency-email-val">3/5</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="urgency-email" style="width: 60%"></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-header">
                        <span class="progress-label">🐛 Bug Resolution</span>
                        <span class="progress-value" id="urgency-bug-val">2/5</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="urgency-bug" style="width: 40%"></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-header">
                        <span class="progress-label">📅 Meeting Attendance</span>
                        <span class="progress-value" id="urgency-meeting-val">1/5</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="urgency-meeting" style="width: 20%"></div>
                    </div>
                </div>
            </div>
            
            <!-- Actions -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🎮 Take Action</div>
                </div>
                
                <div class="action-grid">
                    <button class="action-btn" onclick="selectAction('email')">
                        <div class="action-btn-icon">📧</div>
                        <div class="action-btn-label">Handle Email</div>
                        <div class="action-btn-desc">Client communication & triage</div>
                    </button>
                    <button class="action-btn" onclick="selectAction('bug')">
                        <div class="action-btn-icon">🐛</div>
                        <div class="action-btn-label">Fix Bug</div>
                        <div class="action-btn-desc">Critical outage resolution</div>
                    </button>
                    <button class="action-btn" onclick="selectAction('meeting')">
                        <div class="action-btn-icon">📅</div>
                        <div class="action-btn-label">Attend Meeting</div>
                        <div class="action-btn-desc">Team sync & alignment</div>
                    </button>
                </div>
                
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label class="form-label">Reasoning (required)</label>
                    <textarea class="form-textarea" id="reason" placeholder="Explain your decision. Consider urgency, deadlines, priorities, and stakeholder impact..."></textarea>
                </div>
                
                <div class="form-group" style="margin-bottom: 1.5rem;">
                    <label class="form-label">Confidence Level (optional)</label>
                    <input type="number" class="form-input" id="confidence" min="0" max="1" step="0.05" placeholder="0.85">
                </div>
                
                <div class="control-group">
                    <button class="btn btn-success" onclick="startEpisode()">🚀 Start Episode</button>
                    <button class="btn btn-primary" onclick="takeStep()" id="stepBtn" disabled>▶️ Execute Step</button>
                    <button class="btn btn-warning" onclick="autoPlay()" id="autoBtn" disabled>⚡ Auto Play</button>
                    <button class="btn btn-danger" onclick="resetEnv()">🔄 Reset</button>
                </div>
            </div>
            
            <!-- KPI & Rewards -->
            <div class="grid grid-2">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📈 KPI Dashboard</div>
                    </div>
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-value" id="kpi-tasks">0</div>
                            <div class="kpi-label">Tasks Done</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value" id="kpi-efficiency">0.00</div>
                            <div class="kpi-label">Efficiency</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value" id="kpi-status">-</div>
                            <div class="kpi-label">Status</div>
                        </div>
                    </div>
                </div>
                
                <div class="card" id="reward-card" style="display: none;">
                    <div class="card-header">
                        <div class="card-title">💰 Reward Breakdown</div>
                    </div>
                    <div class="reward-list" id="reward-list"></div>
                </div>
            </div>
            
            <!-- Episode Log -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📜 Episode Timeline</div>
                    <span class="badge badge-info" id="log-count">0 entries</span>
                </div>
                <div class="log-container" id="log">
                    <div class="empty-state">
                        <div class="empty-state-icon">📝</div>
                        <div class="empty-state-text">No activity yet. Start an episode to begin!</div>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <script>
        let selectedAction = null;
        let totalReward = 0;
        let episodeActive = false;
        let logCount = 0;
        
        function selectAction(action) {
            selectedAction = action;
            document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('selected'));
            event.target.closest('.action-btn').classList.add('selected');
            document.getElementById('stepBtn').disabled = false;
        }
        
        async function startEpisode() {
            const response = await fetch('/reset', { method: 'POST' });
            const data = await response.json();
            
            episodeActive = true;
            totalReward = 0;
            logCount = 0;
            updateState(data);
            addLog('Episode initialized successfully', 'success');
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
                reason: reason || "No reasoning provided"
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
            const logType = data.reward > 0 ? 'success' : 'error';
            addLog(`${emoji} ${selectedAction.toUpperCase()} | Reward: ${data.reward.toFixed(2)} | Total: ${totalReward.toFixed(2)}`, logType);
            
            if (data.done) {
                episodeActive = false;
                addLog('🏁 Episode completed!', 'success');
                document.getElementById('stepBtn').disabled = true;
                document.getElementById('autoBtn').disabled = true;
            }
        }
        
        function updateState(state) {
            document.getElementById('stat-time').textContent = state.time;
            document.getElementById('stat-reward').textContent = totalReward.toFixed(2);
            document.getElementById('stat-completed').textContent = `${state.completed?.length || 0}/3`;
            document.getElementById('stat-progress').textContent = `${Math.round((state.completed?.length || 0) / 3 * 100)}%`;
            document.getElementById('stat-loops').textContent = state.loop_count || 0;
            document.getElementById('stat-efficiency').textContent = ((state.completed?.length || 0) / 3).toFixed(2);
            
            if (state.urgency) {
                document.getElementById('urgency-email').style.width = `${(state.urgency.email || 0) * 20}%`;
                document.getElementById('urgency-email-val').textContent = `${state.urgency.email || 0}/5`;
                document.getElementById('urgency-bug').style.width = `${(state.urgency.bug || 0) * 20}%`;
                document.getElementById('urgency-bug-val').textContent = `${state.urgency.bug || 0}/5`;
                document.getElementById('urgency-meeting').style.width = `${(state.urgency.meeting || 0) * 20}%`;
                document.getElementById('urgency-meeting-val').textContent = `${state.urgency.meeting || 0}/5`;
            }
            
            const moodEmojis = { 'normal': '😐', 'angry_client': '😡', 'recovered': '😊' };
            const mood = state.mood || 'normal';
            document.getElementById('mood-emoji').textContent = moodEmojis[mood] || '😐';
            document.getElementById('mood-text').textContent = mood.replace('_', ' ').toUpperCase();
            
            if (state.kpi) {
                document.getElementById('kpi-tasks').textContent = state.kpi.tasks_completed;
                document.getElementById('kpi-efficiency').textContent = state.kpi.efficiency;
                document.getElementById('kpi-status').textContent = state.kpi.status;
            }
        }
        
        function showRewardBreakdown(info) {
            const breakdown = info.reward_breakdown;
            if (!breakdown || Object.keys(breakdown).length === 0) return;
            
            const card = document.getElementById('reward-card');
            const list = document.getElementById('reward-list');
            list.innerHTML = '';
            
            for (const [key, value] of Object.entries(breakdown)) {
                const div = document.createElement('div');
                const isPositive = value > 0;
                div.className = `reward-item ${isPositive ? 'positive' : 'negative'}`;
                div.innerHTML = `
                    <span class="reward-name">${key.replace(/_/g, ' ').toUpperCase()}</span>
                    <span class="reward-value ${isPositive ? 'positive' : 'negative'}">
                        ${isPositive ? '+' : ''}${value.toFixed(2)}
                    </span>
                `;
                list.appendChild(div);
            }
            
            card.style.display = 'block';
        }
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            
            if (logCount === 0) {
                log.innerHTML = '';
            }
            
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            
            const time = new Date().toLocaleTimeString();
            entry.innerHTML = `
                <div class="log-time">${time}</div>
                <div class="log-message">${message}</div>
            `;
            
            log.insertBefore(entry, log.firstChild);
            logCount++;
            document.getElementById('log-count').textContent = `${logCount} entries`;
        }
        
        async function autoPlay() {
            const actions = ['email', 'bug', 'meeting'];
            const reasons = [
                'Highest urgency task with approaching deadline requiring immediate attention',
                'Critical system outage affecting all users and business operations',
                'Important stakeholder alignment meeting for project success'
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
        
        function resetEnv() {
            episodeActive = false;
            totalReward = 0;
            selectedAction = null;
            logCount = 0;
            
            document.getElementById('stat-time').textContent = '0';
            document.getElementById('stat-reward').textContent = '0.00';
            document.getElementById('stat-completed').textContent = '0/3';
            document.getElementById('stat-progress').textContent = '0%';
            document.getElementById('stat-loops').textContent = '0';
            document.getElementById('stat-efficiency').textContent = '0.00';
            
            document.getElementById('urgency-email').style.width = '60%';
            document.getElementById('urgency-email-val').textContent = '3/5';
            document.getElementById('urgency-bug').style.width = '40%';
            document.getElementById('urgency-bug-val').textContent = '2/5';
            document.getElementById('urgency-meeting').style.width = '20%';
            document.getElementById('urgency-meeting-val').textContent = '1/5';
            
            document.getElementById('mood-emoji').textContent = '😐';
            document.getElementById('mood-text').textContent = 'NORMAL';
            
            document.getElementById('kpi-tasks').textContent = '0';
            document.getElementById('kpi-efficiency').textContent = '0.00';
            document.getElementById('kpi-status').textContent = '-';
            
            document.getElementById('reward-card').style.display = 'none';
            document.getElementById('log').innerHTML = '<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-text">No activity yet. Start an episode to begin!</div></div>';
            document.getElementById('log-count').textContent = '0 entries';
            
            document.getElementById('stepBtn').disabled = true;
            document.getElementById('autoBtn').disabled = true;
            
            document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('selected'));
            
            addLog('Environment reset successfully', 'warning');
        }
    </script>
</body>
</html>
""")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
