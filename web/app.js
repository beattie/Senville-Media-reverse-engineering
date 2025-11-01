// Senville AC Control - Web Interface JavaScript

const API_BASE = '/api';
let statusRefreshInterval = null;
let currentStatus = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    refreshStatus();
    startAutoRefresh();
});

// Setup all event listeners
function setupEventListeners() {
    // Power buttons
    document.getElementById('btn-power-on').addEventListener('click', () => setPower(true));
    document.getElementById('btn-power-off').addEventListener('click', () => setPower(false));

    // Mode buttons
    document.querySelectorAll('.btn-mode').forEach(btn => {
        btn.addEventListener('click', () => setMode(btn.dataset.mode));
    });

    // Temperature controls
    document.getElementById('btn-temp-up').addEventListener('click', () => adjustTemp(1));
    document.getElementById('btn-temp-down').addEventListener('click', () => adjustTemp(-1));
    document.getElementById('btn-set-temp').addEventListener('click', setTemperature);
    document.getElementById('temp-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') setTemperature();
    });

    // Fan speed buttons
    document.querySelectorAll('.btn-fan').forEach(btn => {
        btn.addEventListener('click', () => setFanSpeed(parseInt(btn.dataset.speed)));
    });

    // Swing toggles
    document.getElementById('vswing-toggle').addEventListener('change', (e) => {
        setSwing('vertical', e.target.checked);
    });
    document.getElementById('hswing-toggle').addEventListener('change', (e) => {
        setSwing('horizontal', e.target.checked);
    });

    // Refresh button
    document.getElementById('btn-refresh').addEventListener('click', refreshStatus);
}

// API Functions

async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Unknown error');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

async function refreshStatus() {
    try {
        const result = await apiCall('/status');
        currentStatus = result.data;
        updateStatusDisplay(currentStatus);
        updateConnectionStatus(true);
        updateLastUpdateTime();
    } catch (error) {
        updateConnectionStatus(false);
    }
}

async function setPower(on) {
    try {
        await apiCall('/power', 'POST', { on });
        showToast(`AC turned ${on ? 'on' : 'off'}`, 'success');
        setTimeout(refreshStatus, 500);
    } catch (error) {
        // Error already shown by apiCall
    }
}

async function setMode(mode) {
    try {
        await apiCall('/mode', 'POST', { mode });
        showToast(`Mode set to ${mode}`, 'success');
        setTimeout(refreshStatus, 500);
    } catch (error) {
        // Error already shown by apiCall
    }
}

async function setTemperature() {
    const temp = parseInt(document.getElementById('temp-input').value);
    const fahrenheit = currentStatus ? currentStatus.fahrenheit : true;

    try {
        await apiCall('/temperature', 'POST', { temperature: temp, fahrenheit });
        showToast(`Temperature set to ${temp}°${fahrenheit ? 'F' : 'C'}`, 'success');
        setTimeout(refreshStatus, 500);
    } catch (error) {
        // Error already shown by apiCall
    }
}

async function setFanSpeed(speed) {
    try {
        await apiCall('/fan', 'POST', { speed });
        const speedNames = { 20: 'Low', 40: 'Med-Low', 60: 'Medium', 80: 'Med-High', 102: 'Auto' };
        showToast(`Fan speed set to ${speedNames[speed]}`, 'success');
        setTimeout(refreshStatus, 500);
    } catch (error) {
        // Error already shown by apiCall
    }
}

async function setSwing(type, enabled) {
    try {
        const data = type === 'vertical'
            ? { vertical: enabled }
            : { horizontal: enabled };

        await apiCall('/swing', 'POST', data);
        showToast(`${type} swing ${enabled ? 'enabled' : 'disabled'}`, 'success');
        setTimeout(refreshStatus, 500);
    } catch (error) {
        // Error already shown by apiCall
        // Revert toggle on error
        if (type === 'vertical') {
            document.getElementById('vswing-toggle').checked = !enabled;
        } else {
            document.getElementById('hswing-toggle').checked = !enabled;
        }
    }
}

// UI Update Functions

function updateStatusDisplay(status) {
    // Power
    const powerText = status.running ? 'ON' : 'OFF';
    document.getElementById('status-power').textContent = powerText;
    document.getElementById('status-power').style.color = status.running ? '#4CAF50' : '#f44336';

    // Mode
    document.getElementById('status-mode').textContent = status.mode.toUpperCase();

    // Temperatures
    const unit = status.fahrenheit ? '°F' : '°C';
    document.getElementById('status-target-temp').textContent = `${status.target_temperature}${unit}`;
    document.getElementById('status-indoor-temp').textContent = `${status.indoor_temperature}${unit}`;
    document.getElementById('status-outdoor-temp').textContent = `${status.outdoor_temperature}${unit}`;

    // Fan
    const fanNames = { 20: 'Low', 40: 'Med-Low', 60: 'Medium', 80: 'Med-High', 102: 'Auto' };
    document.getElementById('status-fan').textContent = fanNames[status.fan_speed] || status.fan_speed;

    // Update temperature input
    document.getElementById('temp-input').value = Math.round(status.target_temperature);
    document.getElementById('temp-unit').textContent = unit;

    // Update temperature input range based on unit
    if (status.fahrenheit) {
        document.getElementById('temp-input').min = 60;
        document.getElementById('temp-input').max = 87;
    } else {
        document.getElementById('temp-input').min = 16;
        document.getElementById('temp-input').max = 31;
    }

    // Update swing toggles
    document.getElementById('vswing-toggle').checked = status.vertical_swing;
    document.getElementById('hswing-toggle').checked = status.horizontal_swing;

    // Highlight active mode button
    document.querySelectorAll('.btn-mode').forEach(btn => {
        if (btn.dataset.mode === status.mode.toLowerCase()) {
            btn.style.opacity = '1';
            btn.style.fontWeight = '600';
        } else {
            btn.style.opacity = '0.6';
            btn.style.fontWeight = '500';
        }
    });

    // Highlight active fan button
    document.querySelectorAll('.btn-fan').forEach(btn => {
        if (parseInt(btn.dataset.speed) === status.fan_speed) {
            btn.style.opacity = '1';
            btn.style.fontWeight = '600';
        } else {
            btn.style.opacity = '0.6';
            btn.style.fontWeight = '500';
        }
    });
}

function updateConnectionStatus(connected) {
    const badge = document.getElementById('connection-status');
    if (connected) {
        badge.textContent = 'Connected';
        badge.className = 'status-badge connected';
    } else {
        badge.textContent = 'Disconnected';
        badge.className = 'status-badge disconnected';
    }
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById('last-update').textContent = timeStr;
}

function adjustTemp(delta) {
    const input = document.getElementById('temp-input');
    const newValue = parseInt(input.value) + delta;
    const min = parseInt(input.min);
    const max = parseInt(input.max);

    if (newValue >= min && newValue <= max) {
        input.value = newValue;
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

function startAutoRefresh() {
    // Refresh status every 5 seconds
    statusRefreshInterval = setInterval(refreshStatus, 5000);
}

function stopAutoRefresh() {
    if (statusRefreshInterval) {
        clearInterval(statusRefreshInterval);
        statusRefreshInterval = null;
    }
}

// Stop auto-refresh when page is hidden (save resources)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        refreshStatus();
        startAutoRefresh();
    }
});
