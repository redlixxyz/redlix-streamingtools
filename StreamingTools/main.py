from flask import Flask, jsonify, request, render_template_string, send_from_directory
from threading import Lock
import time
from tts import speak
import os

app = Flask(__name__)
lock = Lock()

# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DP3MEDIA
## Streaming Tools Alpha v.1.0
# This main.py Controls the Web Interface and all the Effects for StreamingTools
# As of 30.10.2025

# Global state with default values
state = {
    "timer": {
        "value": 0.0,
        "running": False,
        "visible": True,
        "last_update": time.time()
    },
    "countdown": {
        "value": 0.0,
        "initial": 0.0,
        "running": False,
        "visible": True,
        "last_update": time.time()
    },
    "message": {
        "text": "",
        "color": "#b71c1c",
        "expires_at": 0.0
    },
    "event": {
        "type": "",
        "expires_at": 0.0
    }
}

CONTROL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>DP3MEDIA | Streaming Tools Beta v.2.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-red: rgb(128, 26, 48);
            --dark-gray: rgb(38, 38, 38);
            --burgundy: rgb(49, 18, 26);
            --white: #ffffff;
            --light-gray: #f5f5f5;
            --border: #d0d0d0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--white);
            color: var(--dark-gray);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 0;
            line-height: 1.5;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: var(--primary-red);
            padding: 1rem 2rem;
            border: 3px solid var(--dark-gray);
            border-left: none;
            border-right: none;
            border-top: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .header-logo {
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .header-logo img {
            height: 100%;
            width: auto;
            object-fit: contain;
        }

        .header-title {
            display: none;
        }

        .version-badge {
            background: var(--white);
            color: var(--primary-red);
            padding: 0.4rem 0.8rem;
            border: 2px solid var(--dark-gray);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            padding: 1.5rem;
        }

        .panel {
            background: var(--light-gray);
            border: 3px solid var(--dark-gray);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--dark-gray);
        }

        h2 {
            font-size: 1rem;
            font-weight: 700;
            color: var(--dark-gray);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        h2::before {
            content: '';
            display: block;
            width: 6px;
            height: 6px;
            background: var(--primary-red);
            border: 2px solid var(--dark-gray);
        }

        .status {
            font-family: 'Inter', monospace;
            color: var(--dark-gray);
            font-size: 2rem;
            font-weight: 700;
            background: var(--white);
            padding: 1rem;
            text-align: center;
            border: 3px solid var(--dark-gray);
            letter-spacing: 2px;
        }

        .controls {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            align-items: center;
        }

        button {
            background: var(--white);
            border: 3px solid var(--dark-gray);
            color: var(--dark-gray);
            padding: 0.5rem 1rem;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.15s;
            min-width: 80px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        button:hover {
            background: var(--primary-red);
            color: var(--white);
        }

        button:active {
            transform: scale(0.95);
        }

        .toggle {
            background: var(--burgundy);
            color: var(--white);
            min-width: 70px;
        }

        .toggle.active {
            background: var(--primary-red);
            color: var(--white);
        }

        .start {
            background: var(--primary-red);
            color: var(--white);
            font-weight: 700;
        }

        .start:hover {
            background: var(--burgundy);
            color: var(--white);
        }

        input, select {
            background: var(--white);
            border: 3px solid var(--dark-gray);
            color: var(--dark-gray);
            padding: 0.5rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--primary-red);
        }

        .time-input-group {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            background: var(--white);
            padding: 0.5rem;
            border: 3px solid var(--dark-gray);
        }

        .time-input-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.25rem;
        }

        .time-input-wrapper input {
            width: 60px;
            text-align: center;
            padding: 0.4rem;
            border-width: 2px;
        }

        .time-input-wrapper label {
            font-size: 0.65rem;
            color: var(--dark-gray);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .time-separator {
            color: var(--dark-gray);
            font-weight: 700;
            font-size: 1.25rem;
            padding-top: 0.5rem;
        }

        .message-controls {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .message-controls input[type="text"] {
            flex: 1;
            min-width: 200px;
        }

        input[type="color"] {
            padding: 0.25rem;
            width: 60px;
            height: 40px;
            cursor: pointer;
            border-width: 2px;
        }

        .event-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
        }

        .event-btn {
            padding: 1rem;
            font-size: 0.9rem;
            min-width: 0;
            font-weight: 700;
        }

        .panel-full {
            grid-column: 1 / -1;
        }

        .footer {
            background: var(--dark-gray);
            padding: 1rem 2rem;
            border: 3px solid var(--dark-gray);
            border-left: none;
            border-right: none;
            border-bottom: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .footer-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .footer-logo {
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .footer-logo img {
            height: 100%;
            width: auto;
            object-fit: contain;
        }

        .footer-info {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .footer-title {
            font-size: 0.875rem;
            font-weight: 700;
            color: var(--white);
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .footer-subtitle {
            font-size: 0.7rem;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 500;
        }

        .footer-right {
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .footer-links {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }

        .footer-link {
            color: var(--white);
            text-decoration: none;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.4rem 0.6rem;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border: 2px solid transparent;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .footer-link:hover {
            color: var(--white);
            background: var(--burgundy);
            border: 2px solid var(--dark-gray);
        }

        .footer-link svg {
            width: 14px;
            height: 14px;
        }

        .footer-version {
            background: var(--white);
            color: var(--primary-red);
            padding: 0.4rem 0.6rem;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 1px;
            border: 2px solid var(--dark-gray);
            text-transform: uppercase;
        }

        @media (max-width: 1024px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .dashboard {
                padding: 1rem;
                gap: 1rem;
            }
            
            .footer {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .footer-right {
                width: 100%;
                justify-content: space-between;
            }
        }

        button svg {
            width: 14px;
            height: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <div class="header-logo">
                    <img src="media/headerlogo.png" alt="DP3MEDIA Streaming Tools Logo">
                </div>
                <h1 class="header-title">STREAMING TOOLS</h1>
            </div>
            <div class="version-badge">Alpha v.1.0</div>
        </div>

        <div class="dashboard">
            <!-- Timer Panel -->
            <div class="panel">
                <div class="panel-header">
                    <h2>Timer</h2>
                    <button class="toggle" id="timerVisibility" onclick="toggleVisibility('timer')">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    </button>
                </div>
                <div class="status" id="timerStatus">00:00:00</div>
                <div class="controls">
                    <button onclick="timerControl('start')" class="start">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/></svg>
                        Start
                    </button>
                    <button onclick="timerControl('stop')">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/></svg>
                        Stop
                    </button>
                    <button onclick="timerControl('reset')">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        Reset
                    </button>
                </div>
            </div>

            <!-- Countdown Panel -->
            <div class="panel">
                <div class="panel-header">
                    <h2>Countdown</h2>
                    <button class="toggle" id="countdownVisibility" onclick="toggleVisibility('countdown')">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    </button>
                </div>
                <div class="status" id="countdownStatus">00:00:00</div>
                <div class="time-input-group">
                    <div class="time-input-wrapper">
                        <input type="number" id="countdownHours" placeholder="00" min="0" max="23" value="0">
                        <label>HRS</label>
                    </div>
                    <span class="time-separator">:</span>
                    <div class="time-input-wrapper">
                        <input type="number" id="countdownMinutes" placeholder="00" min="0" max="59" value="5">
                        <label>MIN</label>
                    </div>
                    <span class="time-separator">:</span>
                    <div class="time-input-wrapper">
                        <input type="number" id="countdownSeconds" placeholder="00" min="0" max="59" value="0">
                        <label>SEC</label>
                    </div>
                </div>
                <div class="controls">
                    <button onclick="startCountdown()" class="start">Start</button>
                    <button onclick="countdownControl('stop')">Stop</button>
                    <button onclick="countdownControl('reset')">Reset</button>
                </div>
            </div>

            <!-- Message Panel -->
            <div class="panel panel-full">
                <div class="panel-header">
                    <h2>Message</h2>
                </div>
                <div class="message-controls">
                    <select id="messageEmoji">
                        <option value="">No Emoji</option>
                        <option value="⚠️">⚠️ Warning</option>
                        <option value="🔴">🔴 Alert</option>
                        <option value="📢">📢 Announce</option>
                        <option value="💡">💡 Info</option>
                        <option value="🎮">🎮 Goofy</option>
                        <option value="⭐">⭐ Star</option>
                    </select>
                    <input type="text" id="messageText" placeholder="Enter message...">
                    <select id="messageDuration">
                        <option value="3">3s</option>
                        <option value="5" selected>5s</option>
                        <option value="10">10s</option>
                        <option value="15">15s</option>
                        <option value="30">30s</option>
                        <option value="60">60s</option>
                    </select>
                    <input type="color" id="messageColor" value="#b71c1c">
                    <button onclick="sendMessage()" class="start">Show</button>
                    <button onclick="clearMessage()">Clear</button>
                </div>
            </div>

            <!-- Events Panel -->
            <div class="panel panel-full">
                <div class="panel-header">
                    <h2>Events</h2>
                    <select id="eventDuration">
                        <option value="3">3s</option>
                        <option value="5" selected>5s</option>
                        <option value="10">10s</option>
                        <option value="15">15s</option>
                    </select>
                </div>
                <div class="event-grid">
                    <button onclick="triggerEvent('confetti')" class="event-btn start">🎉 Confetti</button>
                    <button onclick="triggerEvent('glitch')" class="event-btn start">⚡ Glitch</button>
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="footer-left">
                <div class="footer-logo">
                    <img src="media/DP3MEDIAlogo.svg" alt="DP3MEDIA Logo">
                </div>
                <div class="footer-info">
                    <div class="footer-title">DP3MEDIA STREAMING TOOLS</div>
                    <div class="footer-subtitle">Professional streaming overlay system</div>
                </div>
            </div>
            <div class="footer-right">
                <div class="footer-links">
                    <a href="https://DP3MEDIA.xyz/" target="_blank" class="footer-link">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                        </svg>
                        Home
                    </a>
                    <a href="https://DP3MEDIA.xyz/streaming-tools" target="_blank" class="footer-link">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        Docs
                    </a>
                </div>
                <div class="footer-version">Alpha v.1.0</div>
            </div>
        </div>
    </div>

    <script>
        function formatTime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        }

        async function updateState() {
            try {
                const response = await fetch('/api/state');
                const data = await response.json();
                
                document.getElementById('timerStatus').textContent = formatTime(data.timer.value);
                document.getElementById('countdownStatus').textContent = formatTime(data.countdown.value);
                
                document.getElementById('timerVisibility').classList.toggle('active', data.timer.visible);
                document.getElementById('countdownVisibility').classList.toggle('active', data.countdown.visible);
            } catch (err) {
                console.error('Failed to update state:', err);
            }
            setTimeout(updateState, 100);
        }

        async function apiCall(endpoint, method='POST', data={}) {
            try {
                const response = await fetch(`/api/${endpoint}`, {
                    method,
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (err) {
                console.error('API call failed:', err);
                return null;
            }
        }

        function timerControl(action) {
            apiCall(`timer/${action}`);
        }

        function countdownControl(action) {
            apiCall(`countdown/${action}`);
        }

        function startCountdown() {
            const hours = parseInt(document.getElementById('countdownHours').value) || 0;
            const minutes = parseInt(document.getElementById('countdownMinutes').value) || 0;
            const seconds = parseInt(document.getElementById('countdownSeconds').value) || 0;
            const totalMinutes = (hours * 60) + minutes + (seconds / 60);
            apiCall('countdown/start', 'POST', {minutes: totalMinutes});
        }

        function toggleVisibility(element) {
            apiCall(`visibility/${element}`);
        }

        function sendMessage() {
            const text = document.getElementById('messageText').value;
            const emoji = document.getElementById('messageEmoji').value;
            const color = document.getElementById('messageColor').value;
            const duration = document.getElementById('messageDuration').value;
            const fullText = emoji ? `${emoji} ${text} ${emoji}` : text;
            apiCall('message', 'POST', {text: fullText, color, duration});
        }

        function clearMessage() {
            apiCall('message/clear');
        }

        function triggerEvent(type) {
            const duration = document.getElementById('eventDuration').value;
            apiCall('event', 'POST', {type, duration});
        }

        window.onload = updateState;
    </script>
</body>
</html>
"""

DISPLAY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Stream Display for OBS v.1.0 / PART OF STREAMING TOOLS DP3MEDIA</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            padding: 30px;
            background: #00FF00;
            color: white;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            height: 100vh;
        }
        .display-container {
            position: fixed;
            top: 30px;
            left: 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .display-box {
            background: linear-gradient(110deg, rgba(0,0,0,0.95), rgba(0,0,0,0.85));
            padding: 15px 25px 20px 25px;
            border-radius: 16px;
            display: none;
            position: relative;
            overflow: hidden;
            min-width: 280px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .display-box::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: translateX(-100%);
            animation: shimmer 10s infinite;
        }
        @keyframes shimmer {
            100% { transform: translateX(100%); }
        }
        .display-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.5;
            margin-bottom: 8px;
            font-weight: 600;
            position: relative;
            padding-left: 12px;
        }
        .display-label::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 6px;
            height: 6px;
            background: currentColor;
            border-radius: 50%;
            transform: translateY(-50%);
        }
        .time-display {
            font-family: 'JetBrains Mono', monospace;
            font-size: 42px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            margin-bottom: 12px;
        }
        .time-group {
            background: rgba(0,0,0,0.5);
            padding: 8px 12px;
            border-radius: 8px;
            position: relative;
            min-width: 60px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            color: #fff;
        }
        .time-group::after {
            content: attr(data-label);
            position: absolute;
            bottom: -16px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 10px;
            color: rgba(255,255,255,0.4);
            font-family: 'Inter', sans-serif;
            letter-spacing: 1px;
        }
        .time-separator {
            color: rgba(255,255,255,0.5);
            margin: 0 2px;
            animation: blink 10s infinite;
        }
        @keyframes blink {
            0%, 98% { opacity: 0.5; }
            99% { opacity: 0.2; }
        }
        .message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, rgba(0,0,0,0.95), rgba(0,0,0,0.85));
            padding: 40px 60px;
            border-radius: 24px;
            font-family: 'Inter', sans-serif;
            font-size: 48px;
            font-weight: 700;
            text-align: center;
            display: none;
            max-width: 85vw;
            box-shadow: 
                0 0 60px var(--msg-glow, rgba(183, 28, 28, 0.8)),
                0 0 120px var(--msg-glow, rgba(183, 28, 28, 0.5)),
                0 20px 60px rgba(0,0,0,0.5),
                inset 0 1px 0 rgba(255,255,255,0.2),
                inset 0 -1px 0 rgba(0,0,0,0.5);
            backdrop-filter: blur(15px);
            animation: messageIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            border: 2px solid var(--msg-color, #b71c1c);
            text-shadow: 
                0 0 20px var(--msg-glow, rgba(183, 28, 28, 0.8)),
                0 0 40px var(--msg-glow, rgba(183, 28, 28, 0.5)),
                0 2px 10px rgba(0,0,0,0.8);
            letter-spacing: 0.5px;
        }
        .message::before {
            content: '';
            position: absolute;
            inset: -3px;
            background: var(--msg-color, #b71c1c);
            border-radius: 24px;
            z-index: -1;
            opacity: 0.15;
            filter: blur(20px);
        }
        .message::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.1), 
                transparent);
            transform: translateX(-100%);
            animation: messageShimmer 2s infinite;
            border-radius: 24px;
        }
        @keyframes messageIn {
            0% {
                transform: translate(-50%, -50%) scale(0.8);
                opacity: 0;
            }
            100% {
                transform: translate(-50%, -50%) scale(1);
                opacity: 1;
            }
        }
        @keyframes messageShimmer {
            100% { transform: translateX(100%); }
        }
        .message-progress {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background: rgba(0,0,0,0.5);
            border-radius: 0 0 24px 24px;
            overflow: hidden;
        }
        .message-progress-bar {
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, 
                var(--msg-color, #b71c1c), 
                color-mix(in srgb, var(--msg-color, #b71c1c) 70%, white));
            box-shadow: 0 0 20px var(--msg-glow, rgba(183, 28, 28, 0.8));
            transform-origin: left;
            animation: progress var(--duration, 5s) linear forwards;
        }
        @keyframes progress {
            to { transform: scaleX(0); }
        }
        .progress-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 0 0 16px 16px;
            overflow: hidden;
            opacity: 0;  /* Hidden by default */
            transition: opacity 0.3s ease;  /* Smooth transition */
        }
        .progress-bar.active {
            opacity: 1;  /* Show when active */
        }
        .progress-bar-fill {
            height: 100%;
            width: 100%;
            background: rgba(255,255,255,0.2);
            transition: width 0.3s linear;
        }
        #timer .progress-bar-fill {
            background: #4CAF50;
            width: 100% !important;  # Ensure full width
        }
        #timer .progress-bar-fill.blink-fast {
            animation: blinkFast 0.5s infinite;
        }
        #timer .progress-bar-fill.blink-slow {
            animation: blinkSlow 3s infinite;
        }
        @keyframes blinkFast {
            50% { opacity: 0.3; }
        }
        @keyframes blinkSlow {
            50% { opacity: 0.3; }
        }
        #countdown .progress-bar-fill {
            background: linear-gradient(90deg, #FF5722, #FF8A65);
        }
        
        /* Confetti styles */
        .confetti {
            position: fixed;
            width: 10px;
            height: 10px;
            background: #f0f;
            position: absolute;
            animation: confetti-fall linear forwards;
        }
        @keyframes confetti-fall {
            to {
                transform: translateY(100vh) rotate(360deg);
            }
        }
        
        /* Explosion styles */
        .tile {
            position: fixed;
            transition: transform 0.3s ease-out;
            filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));
        }
        .tile.exploded {
            animation: tile-explode 0.5s ease-out forwards;
        }
        @keyframes tile-explode {
            0% {
                transform: translate(0, 0) rotate(0deg) skew(0deg);
                opacity: 1;
            }
            100% {
                transform: translate(var(--tx), var(--ty)) rotate(var(--rot)) skew(var(--skew-x), var(--skew-y));
                opacity: 0.6;
            }
        }
        .tile.green-piece {
            clip-path: polygon(
                var(--p1x) var(--p1y),
                var(--p2x) var(--p2y),
                var(--p3x) var(--p3y),
                var(--p4x) var(--p4y)
            );
            filter: drop-shadow(0 0 15px rgba(0,255,0,0.5));
        }
        
        /* Glitch styles - Advanced CRT TV malfunction */
        .glitch-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
            display: none;
            background: #000;
        }
        .glitch-overlay.active {
            display: block;
        }
        
        /* CRT scanlines */
        .glitch-overlay::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15) 0px,
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 2px
            );
            z-index: 10;
            animation: scanlineMove 8s linear infinite;
        }
        
        @keyframes scanlineMove {
            0% { transform: translateY(0); }
            100% { transform: translateY(4px); }
        }
        
        /* CRT curvature vignette */
        .glitch-overlay::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(
                ellipse at center,
                transparent 0%,
                transparent 60%,
                rgba(0, 0, 0, 0.4) 100%
            );
            z-index: 11;
        }
        
        /* TV color bars */
        .tv-bars {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg,
                    #ffffff 0%, #ffffff 12.5%,
                    #ffff00 12.5%, #ffff00 25%,
                    #00ffff 25%, #00ffff 37.5%,
                    #00ff00 37.5%, #00ff00 50%,
                    #ff00ff 50%, #ff00ff 62.5%,
                    #ff0000 62.5%, #ff0000 75%,
                    #0000ff 75%, #0000ff 87.5%,
                    #000000 87.5%, #000000 100%
                );
            z-index: 1;
            animation: barsGlitch 0.3s infinite;
        }
        
        @keyframes barsGlitch {
            0%, 100% { 
                opacity: 1;
                transform: translateX(0) scaleY(1);
            }
            10% { 
                opacity: 0.8;
                transform: translateX(-5px) scaleY(0.98);
            }
            20% { 
                opacity: 1;
                transform: translateX(3px) scaleY(1.02);
            }
            30% { 
                opacity: 0.9;
                transform: translateX(-2px) scaleY(0.99);
            }
            40% { 
                opacity: 1;
                transform: translateX(0) scaleY(1);
            }
        }
        
        /* RGB separation effect */
        .rgb-shift {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 3;
            mix-blend-mode: screen;
        }
        
        .rgb-shift::before,
        .rgb-shift::after {
            content: '';
            position: absolute;
            top: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg,
                    #ffffff 0%, #ffffff 12.5%,
                    #ffff00 12.5%, #ffff00 25%,
                    #00ffff 25%, #00ffff 37.5%,
                    #00ff00 37.5%, #00ff00 50%,
                    #ff00ff 50%, #ff00ff 62.5%,
                    #ff0000 62.5%, #ff0000 75%,
                    #0000ff 75%, #0000ff 87.5%,
                    #000000 87.5%, #000000 100%
                );
            animation: rgbShiftAnim 0.4s infinite;
        }
        
        .rgb-shift::before {
            left: -3px;
            filter: brightness(1.5);
            opacity: 0.5;
        }
        
        .rgb-shift::after {
            left: 3px;
            filter: brightness(1.2);
            opacity: 0.5;
        }
        
        @keyframes rgbShiftAnim {
            0%, 100% { 
                transform: translate(0, 0);
            }
            25% { 
                transform: translate(2px, 1px);
            }
            50% { 
                transform: translate(-2px, -1px);
            }
            75% { 
                transform: translate(1px, -2px);
            }
        }
        
        /* Static noise */
        .tv-static {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 4;
            opacity: 0.15;
            animation: staticAnim 0.2s infinite;
        }
        
        @keyframes staticAnim {
            0% { 
                background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><filter id="n"><feTurbulence baseFrequency="0.9" numOctaves="4"/></filter><rect width="200" height="200" filter="url(%23n)" opacity="1"/></svg>');
            }
            10% { 
                background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><filter id="n"><feTurbulence baseFrequency="0.95" numOctaves="5"/></filter><rect width="200" height="200" filter="url(%23n)" opacity="1"/></svg>');
            }
            20% { 
                background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><filter id="n"><feTurbulence baseFrequency="0.85" numOctaves="3"/></filter><rect width="200" height="200" filter="url(%23n)" opacity="1"/></svg>');
            }
        }
        
        /* Horizontal distortion bars */
        .distortion-bars {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 5;
        }
        
        .distortion-bar {
            position: absolute;
            left: 0;
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.1);
            animation: distortionMove 1.5s infinite;
        }
        
        .distortion-bar:nth-child(1) {
            top: 20%;
            animation-delay: 0s;
        }
        
        .distortion-bar:nth-child(2) {
            top: 50%;
            animation-delay: 0.3s;
            height: 30px;
        }
        
        .distortion-bar:nth-child(3) {
            top: 75%;
            animation-delay: 0.6s;
            height: 15px;
        }
        
        @keyframes distortionMove {
            0%, 100% {
                transform: translateX(0) scaleX(1);
                opacity: 0;
            }
            10% {
                opacity: 0.8;
            }
            50% {
                transform: translateX(-100px) scaleX(1.5);
                opacity: 0.5;
            }
            90% {
                opacity: 0.3;
            }
        }
        
        /* Vertical roll */
        .vertical-roll {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            background: linear-gradient(
                180deg,
                transparent 0%,
                transparent 40%,
                rgba(255, 255, 255, 0.1) 50%,
                transparent 60%,
                transparent 100%
            );
            animation: verticalRoll 3s linear infinite;
        }
        
        @keyframes verticalRoll {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }
        
        /* Color bleeding effect */
        .color-bleed {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 6;
            background: 
                radial-gradient(circle at 30% 20%, rgba(255, 0, 0, 0.3) 0%, transparent 40%),
                radial-gradient(circle at 70% 50%, rgba(0, 255, 0, 0.3) 0%, transparent 40%),
                radial-gradient(circle at 40% 80%, rgba(0, 0, 255, 0.3) 0%, transparent 40%);
            mix-blend-mode: overlay;
            animation: colorBleedPulse 2s ease-in-out infinite;
        }
        
        @keyframes colorBleedPulse {
            0%, 100% {
                opacity: 0.4;
                filter: blur(10px);
            }
            50% {
                opacity: 0.7;
                filter: blur(20px);
            }
        }
        
        /* Signal loss flicker */
        .signal-loss {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 7;
            background: #000;
            animation: signalLoss 0.8s infinite;
        }
        
        @keyframes signalLoss {
            0%, 90% { opacity: 0; }
            91%, 93% { opacity: 0.9; }
            94%, 96% { opacity: 0; }
            97%, 100% { opacity: 0.95; }
        }
        
        /* Bad tracking lines */
        .tracking-lines {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 8;
            background: repeating-linear-gradient(
                0deg,
                transparent 0px,
                transparent 10px,
                rgba(255, 255, 255, 0.03) 10px,
                rgba(255, 255, 255, 0.03) 11px
            );
            animation: trackingShake 0.5s infinite;
        }
        
        @keyframes trackingShake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-2px); }
            50% { transform: translateX(2px); }
            75% { transform: translateX(-1px); }
        }
    </style>
</head>
<body>
    <div class="display-container">
        <div id="timer" class="display-box">
            <div class="display-label">Timer</div>
            <div class="time-display">
                <span class="time-group" data-label="HRS">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="MIN">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="SEC">00</span>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill"></div>
            </div>
        </div>
        <div id="countdown" class="display-box">
            <div class="display-label">Countdown</div>
            <div class="time-display">
                <span class="time-group" data-label="HRS">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="MIN">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="SEC">00</span>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill"></div>
            </div>
        </div>
    </div>
    <div id="message" class="message"></div>
    <div id="glitchOverlay" class="glitch-overlay">
        <div class="tv-bars"></div>
        <div class="vertical-roll"></div>
        <div class="rgb-shift"></div>
        <div class="tv-static"></div>
        <div class="distortion-bars">
            <div class="distortion-bar"></div>
            <div class="distortion-bar"></div>
            <div class="distortion-bar"></div>
        </div>
        <div class="color-bleed"></div>
        <div class="signal-loss"></div>
        <div class="tracking-lines"></div>
    </div>

    <script>
        function updateTimeDisplay(element, timeStr) {
            const [h, m, s] = timeStr.split(':');
            const groups = element.querySelectorAll('.time-group');
            groups[0].textContent = h;
            groups[1].textContent = m;
            groups[2].textContent = s;
        }

        let currentEvent = null;
        let eventEndTime = 0;
        
        function createConfetti() {
            const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ffa500', '#ff1493'];
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * window.innerWidth + 'px';
            confetti.style.top = '-10px';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.width = (Math.random() * 10 + 5) + 'px';
            confetti.style.height = confetti.style.width;
            confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
            confetti.style.opacity = Math.random() * 0.5 + 0.5;
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 5000);
        }
        
        function startConfetti() {
            const interval = setInterval(() => {
                if (Date.now() / 1000 > eventEndTime) {
                    clearInterval(interval);
                    return;
                }
                for (let i = 0; i < 3; i++) {
                    createConfetti();
                }
            }, 100);
        }
        
        function createExplosion() {
            // Create explosion container
            const container = document.createElement('div');
            container.className = 'explosion-container';
            document.body.appendChild(container);
            
            // Random explosion center point
            const centerX = window.innerWidth * (0.3 + Math.random() * 0.4);
            const centerY = window.innerHeight * (0.3 + Math.random() * 0.4);
            
            // Screen shake
            document.body.classList.add('shake');
            
            // Create screen distortion
            const distortion = document.createElement('div');
            distortion.className = 'explosion-distortion';
            distortion.style.setProperty('--explosion-x', `${centerX}px`);
            distortion.style.setProperty('--explosion-y', `${centerY}px`);
            document.body.appendChild(distortion);
            
            // Create core flash
            const flash = document.createElement('div');
            flash.className = 'explosion-flash';
            flash.style.left = `${centerX}px`;
            flash.style.top = `${centerY}px`;
            flash.style.transform = 'translate(-50%, -50%)';
            container.appendChild(flash);
            
            // Create shockwaves (multiple rings)
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    const shockwave = document.createElement('div');
                    shockwave.className = 'shockwave';
                    shockwave.style.left = `${centerX}px`;
                    shockwave.style.top = `${centerY}px`;
                    shockwave.style.transform = 'translate(-50%, -50%)';
                    shockwave.style.animationDelay = `${i * 0.1}s`;
                    container.appendChild(shockwave);
                }, i * 150);
            }
            
            // Create energy rings
            for (let i = 0; i < 4; i++) {
                setTimeout(() => {
                    const ring = document.createElement('div');
                    ring.className = 'energy-ring';
                    ring.style.left = `${centerX}px`;
                    ring.style.top = `${centerY}px`;
                    ring.style.transform = 'translate(-50%, -50%)';
                    ring.style.animationDelay = `${i * 0.08}s`;
                    container.appendChild(ring);
                }, i * 80);
            }
            
            // Create light rays
            for (let i = 0; i < 12; i++) {
                const ray = document.createElement('div');
                ray.className = 'light-ray';
                const angle = (360 / 12) * i;
                ray.style.left = `${centerX}px`;
                ray.style.top = `${centerY}px`;
                ray.style.transform = `translate(-50%, 0) rotate(${angle}deg)`;
                ray.style.animationDelay = `${i * 0.02}s`;
                container.appendChild(ray);
            }
            
            // Create fire particles (100+)
            const fireColors = ['#FF2400', '#FF6B00', '#FFD700', '#FFF8E7'];
            for (let i = 0; i < 150; i++) {
                const particle = document.createElement('div');
                particle.className = 'fire-particle';
                const size = Math.random() * 40 + 20;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${centerX}px`;
                particle.style.top = `${centerY}px`;
                particle.style.background = `radial-gradient(circle, ${fireColors[Math.floor(Math.random() * fireColors.length)]}, transparent)`;
                
                const angle = Math.random() * Math.PI * 2;
                const distance = Math.random() * 500 + 200;
                const tx = Math.cos(angle) * distance;
                const ty = Math.sin(angle) * distance;
                const duration = Math.random() * 1 + 0.8;
                
                particle.style.setProperty('--tx', `${tx}px`);
                particle.style.setProperty('--ty', `${ty}px`);
                particle.style.setProperty('--duration', `${duration}s`);
                particle.style.animationDelay = `${Math.random() * 0.2}s`;
                
                container.appendChild(particle);
            }
            
            // Create debris particles
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'debris-particle';
                const width = Math.random() * 20 + 5;
                const height = Math.random() * 20 + 5;
                particle.style.width = `${width}px`;
                particle.style.height = `${height}px`;
                particle.style.left = `${centerX}px`;
                particle.style.top = `${centerY}px`;
                
                const angle = Math.random() * Math.PI * 2;
                const distance = Math.random() * 400 + 150;
                const tx = Math.cos(angle) * distance;
                const ty = Math.sin(angle) * distance + Math.random() * 100;
                const rot = Math.random() * 720 - 360;
                const duration = Math.random() * 1.5 + 1;
                
                particle.style.setProperty('--tx', `${tx}px`);
                particle.style.setProperty('--ty', `${ty}px`);
                particle.style.setProperty('--rot', `${rot}deg`);
                particle.style.setProperty('--duration', `${duration}s`);
                particle.style.animationDelay = `${Math.random() * 0.15}s`;
                
                container.appendChild(particle);
            }
            
            // Create smoke particles
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'smoke-particle';
                const size = Math.random() * 150 + 100;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${centerX}px`;
                particle.style.top = `${centerY}px`;
                
                const angle = Math.random() * Math.PI * 2;
                const distance = Math.random() * 300 + 100;
                const tx = Math.cos(angle) * distance;
                const ty = Math.sin(angle) * distance - Math.random() * 100;
                const duration = Math.random() * 2 + 2;
                
                particle.style.setProperty('--tx', `${tx}px`);
                particle.style.setProperty('--ty', `${ty}px`);
                particle.style.setProperty('--duration', `${duration}s`);
                particle.style.animationDelay = `${Math.random() * 0.3 + 0.2}s`;
                
                container.appendChild(particle);
            }
            
            // Create spark particles
            for (let i = 0; i < 200; i++) {
                const particle = document.createElement('div');
                particle.className = 'spark-particle';
                particle.style.left = `${centerX}px`;
                particle.style.top = `${centerY}px`;
                
                const angle = Math.random() * Math.PI * 2;
                const distance = Math.random() * 600 + 200;
                const tx = Math.cos(angle) * distance;
                const ty = Math.sin(angle) * distance;
                const duration = Math.random() * 0.8 + 0.4;
                
                particle.style.setProperty('--tx', `${tx}px`);
                particle.style.setProperty('--ty', `${ty}px`);
                particle.style.setProperty('--duration', `${duration}s`);
                particle.style.animationDelay = `${Math.random() * 0.1}s`;
                
                container.appendChild(particle);
            }
            
            // Cleanup after explosion
            const cleanupTime = (eventEndTime - Date.now() / 1000) * 1000;
            setTimeout(() => {
                container.remove();
                distortion.remove();
                document.body.classList.remove('shake');
            }, cleanupTime);
        }
        
        function startGlitch() {
            const glitchOverlay = document.getElementById('glitchOverlay');
            glitchOverlay.classList.add('active');
            
            setTimeout(() => {
                glitchOverlay.classList.remove('active');
            }, (eventEndTime - Date.now() / 1000) * 1000);
        }

        async function updateDisplay() {
            try {
                const response = await fetch('/api/state');
                const data = await response.json();
                
                // Update timer
                const timerElement = document.getElementById('timer');
                timerElement.style.display = data.timer.visible ? 'block' : 'none';
                updateTimeDisplay(timerElement, formatTime(data.timer.value));
                
                // Update timer progress bar
                const timerProgressBar = timerElement.querySelector('.progress-bar');
                timerProgressBar.classList.toggle('active', data.timer.running);
                timerProgressBar.querySelector('.progress-bar-fill').style.width = '100%';

                // Update countdown
                const countdownElement = document.getElementById('countdown');
                countdownElement.style.display = data.countdown.visible ? 'block' : 'none';
                updateTimeDisplay(countdownElement, formatTime(data.countdown.value));

                // Update countdown progress and ensure progress bar is visible when running
                const countdownProgressBar = countdownElement.querySelector('.progress-bar');
                countdownProgressBar.classList.toggle('active', data.countdown.running);
                if (data.countdown.running && data.countdown.initial > 0) {
                    const progress = (data.countdown.value / data.countdown.initial) * 100;
                    countdownProgressBar.querySelector('.progress-bar-fill').style.width = `${progress}%`;
                } else {
                    countdownProgressBar.querySelector('.progress-bar-fill').style.width = '0%';
                }
                
                // Update message
                const messageElement = document.getElementById('message');
                if (data.message.text && Date.now() / 1000 < data.message.expires_at) {
                    if (messageElement.style.display !== 'block') {
                        messageElement.style.display = 'block';
                        messageElement.style.setProperty('--msg-color', data.message.color);
                        messageElement.innerHTML = `
                            ${data.message.text}
                            <div class="message-progress">
                                <div class="message-progress-bar"></div>
                            </div>
                        `;
                        const duration = Math.max(0, data.message.expires_at - Date.now() / 1000);
                        messageElement.style.setProperty('--duration', `${duration}s`);
                    }
                } else {
                    messageElement.style.display = 'none';
                }

                // Handle events
                if (data.event.type && Date.now() / 1000 < data.event.expires_at) {
                    if (currentEvent !== data.event.type) {
                        currentEvent = data.event.type;
                        eventEndTime = data.event.expires_at;
                        
                        if (currentEvent === 'confetti') {
                            startConfetti();
                        } else if (currentEvent === 'explosion') {
                            createExplosion();
                        } else if (currentEvent === 'glitch') {
                            startGlitch();
                        }
                    }
                } else if (currentEvent && Date.now() / 1000 >= eventEndTime) {
                    currentEvent = null;
                }
            } catch (err) {
                console.error('Failed to update display:', err);
            }
            setTimeout(updateDisplay, 100);
        }

        function formatTime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        }

        window.onload = updateDisplay;
    </script>
</body>
</html>
"""

# Add route to serve media files
@app.route('/media/<path:filename>')
def serve_media(filename):
    media_dir = os.path.join(BASE_DIR, 'media')
    return send_from_directory(media_dir, filename)

# Routes
@app.route('/')
def control_panel():
    return render_template_string(CONTROL_HTML)

@app.route('/display')
def display():
    return render_template_string(DISPLAY_HTML)

@app.route('/api/state')
def get_state():
    with lock:
        current_time = time.time()
        
        # Update timer if running
        if state['timer']['running']:
            elapsed = current_time - state['timer']['last_update']
            state['timer']['value'] += elapsed
            state['timer']['last_update'] = current_time
        
        # Update countdown if running
        if state['countdown']['running']:
            elapsed = current_time - state['countdown']['last_update']
            state['countdown']['value'] = max(0, state['countdown']['value'] - elapsed)
            state['countdown']['last_update'] = current_time
            if state['countdown']['value'] <= 0:
                state['countdown']['running'] = False
        
        return jsonify(state)

# Timer endpoints
@app.route('/api/timer/<action>', methods=['POST'])
def timer_control(action):
    with lock:
        if action == 'start':
            state['timer']['running'] = True
            state['timer']['last_update'] = time.time()
        elif action == 'stop':
            state['timer']['running'] = False
        elif action == 'reset':
            state['timer']['value'] = 0
            state['timer']['running'] = False
    return jsonify({'success': True})

# Countdown endpoints
@app.route('/api/countdown/<action>', methods=['POST'])
def countdown_control(action):
    with lock:
        if action == 'start':
            data = request.get_json()
            minutes = float(data.get('minutes', 0))
            total_seconds = minutes * 60
            state['countdown']['value'] = total_seconds
            state['countdown']['initial'] = total_seconds  # Store initial value
            state['countdown']['running'] = True
            state['countdown']['last_update'] = time.time()
        elif action == 'stop':
            state['countdown']['running'] = False
        elif action == 'reset':
            state['countdown']['value'] = 0
            state['countdown']['initial'] = 0
            state['countdown']['running'] = False
    return jsonify({'success': True})

# Visibility toggle endpoints
@app.route('/api/visibility/<element>', methods=['POST'])
def toggle_visibility(element):
    with lock:
        if element in ['timer', 'countdown']:
            state[element]['visible'] = not state[element]['visible']
    return jsonify({'success': True})

# Message endpoints
@app.route('/api/message', methods=['POST'])
def set_message():
    with lock:
        data = request.get_json()
        message_text = data.get('text', '')
        state['message']['text'] = message_text
        state['message']['color'] = data.get('color', '#b71c1c')
        duration = float(data.get('duration', 5))
        state['message']['expires_at'] = time.time() + duration
        
        # Trigger TTS for the message
        if message_text:
            speak(message_text)
    
    return jsonify({'success': True})

@app.route('/api/message/clear', methods=['POST'])
def clear_message():
    with lock:
        state['message']['text'] = ''
        state['message']['expires_at'] = 0
    return jsonify({'success': True})

# Event endpoint
@app.route('/api/event', methods=['POST'])
def trigger_event():
    with lock:
        data = request.get_json()
        event_type = data.get('type', '')
        duration = float(data.get('duration', 5))
        state['event']['type'] = event_type
        state['event']['expires_at'] = time.time() + duration
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8765, debug=True)