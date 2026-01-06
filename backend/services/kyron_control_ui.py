"""
KYRON Floating Control UI
Injects floating control button into web pages for automation control
"""

KYRON_CONTROL_UI_SCRIPT = """
(function() {
    // Prevent multiple injections
    if (window.kyronControlInjected) return;
    window.kyronControlInjected = true;
    
    // Create KYRON control panel
    const kyronPanel = document.createElement('div');
    kyronPanel.id = 'kyron-control-panel';
    kyronPanel.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border-radius: 12px;
        overflow: hidden;
        min-width: 280px;
        background: white;
        transition: all 0.3s ease;
    `;
    
    // Status indicator
    const statusBar = document.createElement('div');
    statusBar.id = 'kyron-status-bar';
    statusBar.style.cssText = `
        padding: 12px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
    `;
    
    // Status icon
    const statusIcon = document.createElement('div');
    statusIcon.id = 'kyron-status-icon';
    statusIcon.style.cssText = `
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #10b981;
        animation: pulse 2s infinite;
    `;
    
    // Status text
    const statusText = document.createElement('span');
    statusText.id = 'kyron-status-text';
    statusText.textContent = 'KYRON Running';
    
    statusBar.appendChild(statusIcon);
    statusBar.appendChild(statusText);
    
    // Control buttons container
    const controlsContainer = document.createElement('div');
    controlsContainer.id = 'kyron-controls';
    controlsContainer.style.cssText = `
        padding: 12px;
        display: none;
        flex-direction: column;
        gap: 8px;
    `;
    
    // Pause button
    const pauseBtn = document.createElement('button');
    pauseBtn.id = 'kyron-pause-btn';
    pauseBtn.textContent = '⏸ Pause';
    pauseBtn.style.cssText = `
        padding: 10px 16px;
        background: #f59e0b;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        font-size: 13px;
        transition: all 0.2s;
    `;
    pauseBtn.onmouseover = () => pauseBtn.style.background = '#d97706';
    pauseBtn.onmouseout = () => pauseBtn.style.background = '#f59e0b';
    
    // Resume button
    const resumeBtn = document.createElement('button');
    resumeBtn.id = 'kyron-resume-btn';
    resumeBtn.textContent = '▶ Resume';
    resumeBtn.style.cssText = `
        padding: 10px 16px;
        background: #10b981;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        font-size: 13px;
        transition: all 0.2s;
        display: none;
    `;
    resumeBtn.onmouseover = () => resumeBtn.style.background = '#059669';
    resumeBtn.onmouseout = () => resumeBtn.style.background = '#10b981';
    
    // Stop button
    const stopBtn = document.createElement('button');
    stopBtn.id = 'kyron-stop-btn';
    stopBtn.textContent = '⛔ Stop';
    stopBtn.style.cssText = `
        padding: 10px 16px;
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        font-size: 13px;
        transition: all 0.2s;
    `;
    stopBtn.onmouseover = () => stopBtn.style.background = '#dc2626';
    stopBtn.onmouseout = () => stopBtn.style.background = '#ef4444';
    
    // Progress info
    const progressInfo = document.createElement('div');
    progressInfo.id = 'kyron-progress';
    progressInfo.style.cssText = `
        padding: 8px 12px;
        background: #f3f4f6;
        border-radius: 6px;
        font-size: 12px;
        color: #6b7280;
        text-align: center;
    `;
    progressInfo.textContent = 'KYRON is working...';
    
    // Current step display
    const currentStepDisplay = document.createElement('div');
    currentStepDisplay.id = 'kyron-current-step';
    currentStepDisplay.style.cssText = `
        padding: 8px 12px;
        background: #eff6ff;
        border-radius: 6px;
        font-size: 11px;
        color: #1e40af;
        text-align: center;
        margin-top: 4px;
        font-weight: 500;
    `;
    currentStepDisplay.textContent = 'Initializing...';
    
    controlsContainer.appendChild(pauseBtn);
    controlsContainer.appendChild(resumeBtn);
    controlsContainer.appendChild(stopBtn);
    controlsContainer.appendChild(progressInfo);
    controlsContainer.appendChild(currentStepDisplay);
    
    // Message area
    const messageArea = document.createElement('div');
    messageArea.id = 'kyron-message';
    messageArea.style.cssText = `
        padding: 12px;
        background: #fef3c7;
        border-top: 1px solid #fde68a;
        font-size: 12px;
        color: #92400e;
        display: none;
    `;
    
    kyronPanel.appendChild(statusBar);
    kyronPanel.appendChild(controlsContainer);
    kyronPanel.appendChild(messageArea);
    
    // Toggle controls on status bar click
    statusBar.onclick = () => {
        const isVisible = controlsContainer.style.display === 'flex';
        controlsContainer.style.display = isVisible ? 'none' : 'flex';
    };
    
    // Add to page
    document.body.appendChild(kyronPanel);
    
    // Button event handlers (will be connected via postMessage)
    pauseBtn.onclick = () => {
        window.postMessage({ type: 'KYRON_ACTION', action: 'pause' }, '*');
    };
    
    resumeBtn.onclick = () => {
        window.postMessage({ type: 'KYRON_ACTION', action: 'resume' }, '*');
    };
    
    stopBtn.onclick = () => {
        window.postMessage({ type: 'KYRON_ACTION', action: 'stop' }, '*');
    };
    
    // Listen for status updates
    window.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'KYRON_STATUS_UPDATE') {
            updateKyronStatus(event.data.status, event.data.message, event.data.progress);
        }
    });
    
    // Update status function
    window.updateKyronStatus = function(status, message, progress, currentStep) {
        const icon = document.getElementById('kyron-status-icon');
        const text = document.getElementById('kyron-status-text');
        const messageEl = document.getElementById('kyron-message');
        const progressEl = document.getElementById('kyron-progress');
        const currentStepEl = document.getElementById('kyron-current-step');
        const resumeBtn = document.getElementById('kyron-resume-btn');
        const pauseBtn = document.getElementById('kyron-pause-btn');
        
        // Update icon and status
        if (status === 'running') {
            icon.style.background = '#10b981';
            icon.style.animation = 'pulse 2s infinite';
            text.textContent = 'KYRON Running';
            resumeBtn.style.display = 'none';
            pauseBtn.style.display = 'block';
        } else if (status === 'waiting_for_user') {
            icon.style.background = '#f59e0b';
            icon.style.animation = 'pulse 2s infinite';
            text.textContent = 'KYRON Waiting';
            resumeBtn.style.display = 'block';
            pauseBtn.style.display = 'none';
        } else if (status === 'paused') {
            icon.style.background = '#f59e0b';
            icon.style.animation = 'none';
            text.textContent = 'KYRON Paused';
            resumeBtn.style.display = 'block';
            pauseBtn.style.display = 'none';
        } else if (status === 'stopped') {
            icon.style.background = '#ef4444';
            icon.style.animation = 'none';
            text.textContent = 'KYRON Stopped';
            resumeBtn.style.display = 'none';
            pauseBtn.style.display = 'none';
        } else if (status === 'completed') {
            icon.style.background = '#10b981';
            icon.style.animation = 'none';
            text.textContent = 'KYRON Completed';
            resumeBtn.style.display = 'none';
            pauseBtn.style.display = 'none';
        }
        
        // Update message
        if (message) {
            messageEl.textContent = message;
            messageEl.style.display = 'block';
        } else {
            messageEl.style.display = 'none';
        }
        
        // Update progress
        if (progress) {
            progressEl.textContent = progress;
        }
        
        // Update current step
        if (currentStepEl) {
            if (currentStep) {
                currentStepEl.textContent = currentStep;
                currentStepEl.style.display = 'block';
            } else {
                currentStepEl.style.display = 'none';
            }
        }
    };
    
    // CSS animation for pulse
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    `;
    document.head.appendChild(style);
    
    console.log('[KYRON] Control panel injected successfully');
})();
"""

def get_control_ui_script() -> str:
    """Get the KYRON control UI injection script"""
    return KYRON_CONTROL_UI_SCRIPT

