#!/usr/bin/env python
"""
Simple FastAPI server with embedded HTML UI.
NO Streamlit, NO proxy, NO WebSocket issues.
Everything runs on port 7860.
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


# ============ UI ============

@app.get("/")
def root():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Workplace Failure Simulator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: moveBackground 20s linear infinite;
        }
        
        @keyframes moveBackground {
            0% { transform: translate(0, 0); }
            100% { transform: translate(50px, 50px); }
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            opacity: 0.95;
            font-size: 1.2em;
            position: relative;
            z-index: 1;
        }
        
        .content { 
            padding: 40px; 
        }
        
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-item {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        
        .status-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            border-color: #667eea;
        }
        
        .status-item label {
            display: block;
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .status-item .value {
            font-size: 2em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .message-box {
            background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
            border-left: 5px solid #667eea;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 10px;
            min-height: 120px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        }
        
        .message-box h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .message-box #message {
            color: #333;
            line-height: 1.6;
            font-size: 1.05em;
        }
        
        .controls-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
            font-size: 1.05em;
        }
        
        select, input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s;
            background: white;
        }
        
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .button-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 25px;
        }
        
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.05em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            overflow: hidden;
        }
        
        button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        button:hover::before {
            width: 300px;
            height: 300px;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        
        button:active {
            transform: translateY(-1px);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-success { 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white; 
        }
        
        .btn-warning { 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white; 
        }
        
        .btn-danger { 
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white; 
        }
        
        .log-section h3 {
            margin-bottom: 20px;
            color: #333;
            font-size: 1.4em;
        }
        
        .log-box {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 25px;
            border-radius: 12px;
            max-height: 450px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
        }
        
        .log-box::-webkit-scrollbar {
            width: 10px;
        }
        
        .log-box::-webkit-scrollbar-track {
            background: #2d2d2d;
            border-radius: 5px;
        }
        
        .log-box::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 5px;
        }
        
        .log-entry {
            margin-bottom: 12px;
            padding: 12px;
            border-radius: 6px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .log-start { 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-left: 4px solid #4a90e2;
        }
        
        .log-step { 
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            border-left: 4px solid #38ef7d;
        }
        
        .log-end { 
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            border-left: 4px solid #ffd700;
        }
        
        .log-error { 
            background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
            border-left: 4px solid #ff6b6b;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .content {
                padding: 20px;
            }
            
            .status-bar {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Workplace Failure Simulator</h1>
            <p>Test if an agent survives a real job — not just tasks.</p>
        </div>
        
        <div class="content">
            <div class="status-bar">
                <div class="status-item">
                    <label>⏱️ Time Step</label>
                    <div class="value" id="time">0</div>
                </div>
                <div class="status-item">
                    <label>💰 Reward</label>
                    <div class="value" id="reward">0.00</div>
                </div>
                <div class="status-item">
                    <label>✅ Tasks Completed</label>
                    <div class="value" id="tasks-done">0/3</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress" style="width: 0%"></div>
                    </div>
                </div>
                <div class="status-item">
                    <label>😊 Mood</label>
                    <div class="value" id="mood">-</div>
                </div>
            </div>
            
            <div class="message-box">
                <h3>📋 Current Situation</h3>
                <div id="message">Click "Start Episode" to begin your workplace simulation...</div>
            </div>
            
            <div class="controls-section">
                <div class="form-group">
                    <label>🎯 Choose Your Action:</label>
                    <select id="action-select">
                        <option value="email">📧 Send Email - Meet deadlines and unblock stakeholders</option>
                        <option value="bug">🐛 Fix Bug - Resolve critical issues and restore service</option>
                        <option value="meeting">👥 Attend Meeting - Align with team and stakeholders</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>💭 Reasoning:</label>
                    <input type="text" id="reason-input" placeholder="Explain why you're taking this action...">
                </div>
                
                <div class="button-group">
                    <button class="btn-primary" onclick="startEpisode()">🎮 Start Episode</button>
                    <button class="btn-success" id="step-btn" onclick="takeStep()" disabled>▶ Take Step</button>
                    <button class="btn-warning" onclick="autoPlay()">⚡ Auto Play</button>
                    <button class="btn-danger" onclick="resetAll()">🔄 Reset</button>
                </div>
            </div>
            
            <div class="log-section">
                <h3>📜 Episode Log</h3>
                <div class="log-box" id="log">
                    <div class="log-entry log-start">Welcome! Click "Start Episode" to begin your simulation...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let episodeActive = false;
        
        function addLog(type, text) {
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] ${text}`;
            log.insertBefore(entry, log.firstChild);
        }
        
        async function startEpisode() {
            try {
                addLog('start', '🚀 Initializing new episode...');
                const response = await fetch('/reset', { method: 'POST' });
                const data = await response.json();
                
                document.getElementById('time').textContent = data.time;
                document.getElementById('message').textContent = data.message;
                document.getElementById('mood').textContent = data.mood === 'normal' ? '😊 Normal' : data.mood === 'angry_client' ? '😠 Angry Client' : data.mood;
                document.getElementById('tasks-done').textContent = `0/${data.tasks.length}`;
                document.getElementById('progress').style.width = '0%';
                document.getElementById('reward').textContent = '0.00';
                document.getElementById('step-btn').disabled = false;
                episodeActive = true;
                
                addLog('start', `✅ Episode started successfully!`);
                addLog('start', `📋 Tasks: ${data.tasks.map(t => t.toUpperCase()).join(', ')}`);
                addLog('start', `🔥 Urgency Levels: Email(${data.urgency.email}), Bug(${data.urgency.bug}), Meeting(${data.urgency.meeting})`);
            } catch (error) {
                addLog('error', `❌ Error starting episode: ${error.message}`);
            }
        }
        
        async function takeStep() {
            if (!episodeActive) {
                addLog('error', '⚠️ No active episode. Click "Start Episode" first.');
                return;
            }
            
            const action = document.getElementById('action-select').value;
            const reason = document.getElementById('reason-input').value || `Taking ${action} action based on priority assessment`;
            
            try {
                const response = await fetch('/step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action, reason, confidence: 0.8 })
                });
                
                const data = await response.json();
                
                document.getElementById('time').textContent = data.observation.time;
                document.getElementById('message').textContent = data.observation.message;
                document.getElementById('mood').textContent = data.observation.mood === 'normal' ? '😊 Normal' : data.observation.mood === 'angry_client' ? '😠 Angry Client' : data.observation.mood;
                document.getElementById('reward').textContent = data.reward.toFixed(2);
                
                const completed = data.observation.completed || [];
                const total = data.observation.tasks?.length || 3;
                const progress = (completed.length / total) * 100;
                document.getElementById('tasks-done').textContent = `${completed.length}/${total}`;
                document.getElementById('progress').style.width = `${progress}%`;
                
                const actionEmoji = action === 'email' ? '📧' : action === 'bug' ? '🐛' : '👥';
                addLog('step', `${actionEmoji} Action: ${action.toUpperCase()} | Reward: +${data.reward.toFixed(2)} | Done: ${data.done ? '✅' : '❌'}`);
                
                if (data.info && data.info.reward_breakdown) {
                    const breakdown = data.info.reward_breakdown;
                    addLog('step', `   📊 Reward Breakdown: Task(${breakdown.task_completed}), Urgency(${breakdown.urgency_respected}), Reasoning(${breakdown.reasoning_basic})`);
                }
                
                if (data.done) {
                    episodeActive = false;
                    document.getElementById('step-btn').disabled = true;
                    addLog('end', `🎉 Episode completed! Final Reward: ${data.reward.toFixed(2)}`);
                    addLog('end', `📈 Tasks Completed: ${completed.length}/${total}`);
                }
            } catch (error) {
                addLog('error', `❌ Error taking step: ${error.message}`);
            }
        }
        
        async function autoPlay() {
            if (episodeActive) {
                addLog('error', '⚠️ Episode already in progress.');
                return;
            }
            
            await startEpisode();
            const actions = ['email', 'bug', 'meeting'];
            
            for (let i = 0; i < actions.length; i++) {
                if (!episodeActive) break;
                await new Promise(r => setTimeout(r, 1500));
                document.getElementById('action-select').value = actions[i];
                document.getElementById('reason-input').value = `Auto-playing optimal strategy: ${actions[i]}`;
                await takeStep();
            }
        }
        
        function resetAll() {
            episodeActive = false;
            document.getElementById('time').textContent = '0';
            document.getElementById('reward').textContent = '0.00';
            document.getElementById('tasks-done').textContent = '0/3';
            document.getElementById('progress').style.width = '0%';
            document.getElementById('mood').textContent = '-';
            document.getElementById('message').textContent = 'Click "Start Episode" to begin your workplace simulation...';
            document.getElementById('step-btn').disabled = true;
            document.getElementById('log').innerHTML = '<div class="log-entry log-start">🔄 Reset complete. Ready to start new episode...</div>';
            addLog('start', '✅ System reset. All states cleared.');
        }
    </script>
</body>
</html>
    """)


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    print(f"[STARTUP] Starting server on {host}:{port}...")
    print(f"[STARTUP] UI: http://{host}:{port}")
    print(f"[STARTUP] API: /reset, /step, /state, /health")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
