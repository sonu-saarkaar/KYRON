/**
 * KYRON Automation Overlay UI
 * Floating control panel that shows status and provides user controls
 */

(function() {
    'use strict';
    
    // Prevent multiple injections
    if (window.KYRON_OVERLAY_INJECTED) {
        console.log('[KYRON] Overlay already injected');
        return;
    }
    window.KYRON_OVERLAY_INJECTED = true;
    
    // Create overlay container
    const overlay = document.createElement('div');
    overlay.id = 'kyron-overlay';
    overlay.innerHTML = `
        <style>
            #kyron-overlay {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            }
            
            #kyron-control-panel {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                padding: 16px 20px;
                min-width: 280px;
                color: white;
                cursor: move;
                user-select: none;
                transition: all 0.3s ease;
            }
            
            #kyron-control-panel.minimized {
                padding: 12px 16px;
                min-width: auto;
            }
            
            #kyron-control-panel:hover {
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
            }
            
            .kyron-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
            }
            
            .kyron-header.minimized {
                margin-bottom: 0;
            }
            
            .kyron-logo {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                font-size: 16px;
            }
            
            .kyron-status-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #4ade80;
                box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
                animation: pulse 2s ease-in-out infinite;
            }
            
            .kyron-status-dot.running {
                background: #4ade80;
                animation: pulse 1s ease-in-out infinite;
            }
            
            .kyron-status-dot.paused {
                background: #fbbf24;
                animation: none;
            }
            
            .kyron-status-dot.stopped {
                background: #ef4444;
                animation: none;
            }
            
            .kyron-status-dot.waiting {
                background: #3b82f6;
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% {
                    opacity: 1;
                    transform: scale(1);
                }
                50% {
                    opacity: 0.6;
                    transform: scale(1.1);
                }
            }
            
            .kyron-minimize-btn {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                width: 24px;
                height: 24px;
                border-radius: 6px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }
            
            .kyron-minimize-btn:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            .kyron-content {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .kyron-content.hidden {
                display: none;
            }
            
            .kyron-status-text {
                font-size: 13px;
                opacity: 0.9;
                line-height: 1.4;
                margin: 0;
            }
            
            .kyron-progress-bar {
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
                overflow: hidden;
                margin: 8px 0;
            }
            
            .kyron-progress-fill {
                height: 100%;
                background: white;
                border-radius: 2px;
                transition: width 0.3s ease;
            }
            
            .kyron-controls {
                display: flex;
                gap: 8px;
                margin-top: 4px;
            }
            
            .kyron-btn {
                flex: 1;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .kyron-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
            }
            
            .kyron-btn:active {
                transform: translateY(0);
            }
            
            .kyron-btn.primary {
                background: rgba(255, 255, 255, 0.9);
                color: #667eea;
            }
            
            .kyron-btn.primary:hover {
                background: white;
            }
            
            .kyron-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .kyron-btn:disabled:hover {
                transform: none;
            }
            
            .kyron-current-step {
                font-size: 12px;
                opacity: 0.8;
                margin-top: 4px;
                font-style: italic;
            }
        </style>
        
        <div id="kyron-control-panel">
            <div class="kyron-header">
                <div class="kyron-logo">
                    <div class="kyron-status-dot running"></div>
                    <span>KYRON AI</span>
                </div>
                <button class="kyron-minimize-btn" id="kyron-minimize">─</button>
            </div>
            
            <div class="kyron-content">
                <p class="kyron-status-text" id="kyron-status">Initializing automation...</p>
                
                <div class="kyron-progress-bar">
                    <div class="kyron-progress-fill" id="kyron-progress" style="width: 0%"></div>
                </div>
                
                <div class="kyron-current-step" id="kyron-current-step">Starting...</div>
                
                <div class="kyron-controls">
                    <button class="kyron-btn" id="kyron-pause">⏸ Pause</button>
                    <button class="kyron-btn" id="kyron-resume" style="display:none;">▶ Resume</button>
                    <button class="kyron-btn" id="kyron-stop">⏹ Stop</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Draggable functionality
    const panel = document.getElementById('kyron-control-panel');
    const header = panel.querySelector('.kyron-header');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;
    
    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);
    
    function dragStart(e) {
        if (e.target.id === 'kyron-minimize') return;
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        isDragging = true;
    }
    
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            setTranslate(currentX, currentY, panel);
        }
    }
    
    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }
    
    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }
    
    // Minimize/Maximize
    const minimizeBtn = document.getElementById('kyron-minimize');
    const content = panel.querySelector('.kyron-content');
    const headerDiv = panel.querySelector('.kyron-header');
    let isMinimized = false;
    
    minimizeBtn.addEventListener('click', () => {
        isMinimized = !isMinimized;
        if (isMinimized) {
            content.classList.add('hidden');
            panel.classList.add('minimized');
            headerDiv.classList.add('minimized');
            minimizeBtn.textContent = '+';
        } else {
            content.classList.remove('hidden');
            panel.classList.remove('minimized');
            headerDiv.classList.remove('minimized');
            minimizeBtn.textContent = '─';
        }
    });
    
    // Control buttons
    const pauseBtn = document.getElementById('kyron-pause');
    const resumeBtn = document.getElementById('kyron-resume');
    const stopBtn = document.getElementById('kyron-stop');
    const statusDot = panel.querySelector('.kyron-status-dot');
    
    let isPaused = false;
    
    pauseBtn.addEventListener('click', () => {
        isPaused = true;
        pauseBtn.style.display = 'none';
        resumeBtn.style.display = 'block';
        statusDot.classList.remove('running');
        statusDot.classList.add('paused');
        window.KYRON_PAUSED = true;
        console.log('[KYRON] Automation paused by user');
    });
    
    resumeBtn.addEventListener('click', () => {
        isPaused = false;
        resumeBtn.style.display = 'none';
        pauseBtn.style.display = 'block';
        statusDot.classList.remove('paused');
        statusDot.classList.add('running');
        window.KYRON_PAUSED = false;
        console.log('[KYRON] Automation resumed by user');
    });
    
    stopBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to stop KYRON automation?')) {
            statusDot.classList.remove('running', 'paused');
            statusDot.classList.add('stopped');
            window.KYRON_STOPPED = true;
            pauseBtn.disabled = true;
            resumeBtn.disabled = true;
            stopBtn.disabled = true;
            document.getElementById('kyron-status').textContent = 'Automation stopped by user';
            console.log('[KYRON] Automation stopped by user');
        }
    });
    
    // Public API for status updates
    window.KYRON = {
        updateStatus: function(status, step, progress) {
            document.getElementById('kyron-status').textContent = status;
            if (step) {
                document.getElementById('kyron-current-step').textContent = step;
            }
            if (progress !== undefined) {
                document.getElementById('kyron-progress').style.width = progress + '%';
            }
        },
        
        setWaiting: function() {
            statusDot.classList.remove('running', 'paused', 'stopped');
            statusDot.classList.add('waiting');
        },
        
        setRunning: function() {
            if (!isPaused) {
                statusDot.classList.remove('waiting', 'paused', 'stopped');
                statusDot.classList.add('running');
            }
        },
        
        setCompleted: function() {
            statusDot.classList.remove('running', 'waiting', 'paused');
            pauseBtn.disabled = true;
            resumeBtn.disabled = true;
            stopBtn.disabled = true;
            document.getElementById('kyron-status').textContent = 'Automation completed successfully!';
            document.getElementById('kyron-current-step').textContent = 'All done ✅';
            document.getElementById('kyron-progress').style.width = '100%';
        },
        
        setError: function(message) {
            statusDot.classList.remove('running', 'waiting', 'paused');
            statusDot.classList.add('stopped');
            pauseBtn.disabled = true;
            resumeBtn.disabled = true;
            document.getElementById('kyron-status').textContent = 'Error: ' + message;
        }
    };
    
    console.log('[KYRON] Overlay UI initialized');
})();

