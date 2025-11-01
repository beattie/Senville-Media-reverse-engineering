// Senville AC Schedules - JavaScript

const API_BASE = '/api';
let currentEditingId = null;
let schedules = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadSchedulerStatus();
    loadSchedules();
    setInterval(loadSchedulerStatus, 10000); // Update status every 10 seconds
});

// Setup event listeners
function setupEventListeners() {
    // Scheduler control
    document.getElementById('btn-start-scheduler').addEventListener('click', startScheduler);
    document.getElementById('btn-stop-scheduler').addEventListener('click', stopScheduler);

    // Add schedule
    document.getElementById('btn-add-schedule').addEventListener('click', openAddModal);

    // Modal controls
    document.querySelector('.modal-close').addEventListener('click', closeModal);
    document.getElementById('btn-cancel-schedule').addEventListener('click', closeModal);
    document.getElementById('btn-save-schedule').addEventListener('click', saveSchedule);

    // Close modal on outside click
    document.getElementById('schedule-modal').addEventListener('click', (e) => {
        if (e.target.id === 'schedule-modal') {
            closeModal();
        }
    });
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

// Scheduler Status

async function loadSchedulerStatus() {
    try {
        const result = await apiCall('/scheduler/status');
        const status = result.data;

        const statusText = status.running ? 'Running' : 'Stopped';
        const statusEl = document.getElementById('scheduler-status');
        statusEl.textContent = statusText;
        statusEl.style.color = status.running ? '#4CAF50' : '#f44336';

        document.getElementById('active-schedules').textContent =
            `${status.enabled_schedules} / ${status.total_schedules}`;

        // Enable/disable buttons
        document.getElementById('btn-start-scheduler').disabled = status.running;
        document.getElementById('btn-stop-scheduler').disabled = !status.running;
    } catch (error) {
        document.getElementById('scheduler-status').textContent = 'Error';
    }
}

async function startScheduler() {
    try {
        await apiCall('/scheduler/start', 'POST');
        showToast('Scheduler started', 'success');
        setTimeout(loadSchedulerStatus, 1000);
    } catch (error) {
        // Error already shown
    }
}

async function stopScheduler() {
    try {
        await apiCall('/scheduler/stop', 'POST');
        showToast('Scheduler stopped', 'success');
        setTimeout(loadSchedulerStatus, 1000);
    } catch (error) {
        // Error already shown
    }
}

// Schedules Management

async function loadSchedules() {
    try {
        const result = await apiCall('/schedules');
        schedules = result.data;
        renderSchedules();
    } catch (error) {
        // Error already shown
    }
}

function renderSchedules() {
    const container = document.getElementById('schedules-list');

    if (schedules.length === 0) {
        container.innerHTML = `
            <div class="card">
                <div class="empty-state">
                    <h3>No schedules yet</h3>
                    <p>Create your first schedule to automate your AC</p>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = schedules.map(schedule => {
        const days = schedule.days.length > 0
            ? schedule.days.map(d => d.charAt(0).toUpperCase() + d.slice(1)).join(', ')
            : 'Every day';

        const actions = [];
        if (schedule.action.power !== undefined) {
            actions.push(`Power: ${schedule.action.power ? 'On' : 'Off'}`);
        }
        if (schedule.action.mode) {
            actions.push(`Mode: ${schedule.action.mode.charAt(0).toUpperCase() + schedule.action.mode.slice(1)}`);
        }
        if (schedule.action.temperature) {
            const unit = schedule.action.fahrenheit ? '°F' : '°C';
            actions.push(`Temp: ${schedule.action.temperature}${unit}`);
        }
        if (schedule.action.fan_speed) {
            const fanNames = { 20: 'Low', 40: 'Med-Low', 60: 'Med', 80: 'Med-High', 102: 'Auto' };
            actions.push(`Fan: ${fanNames[schedule.action.fan_speed]}`);
        }

        const lastRun = schedule.last_run
            ? `Last run: ${new Date(schedule.last_run).toLocaleString()}`
            : 'Never run';

        return `
            <div class="schedule-card ${schedule.enabled ? '' : 'disabled'}">
                <div class="schedule-info">
                    <div class="schedule-name">${schedule.name}</div>
                    <div class="schedule-details">
                        <div class="schedule-detail">⏰ ${formatTime(schedule.time)}</div>
                        <div class="schedule-detail">📅 ${days}</div>
                        <div class="schedule-detail">⚡ ${actions.join(', ')}</div>
                    </div>
                    <div class="schedule-details">
                        <div class="schedule-detail" style="font-size: 12px">${lastRun}</div>
                    </div>
                </div>
                <div class="schedule-actions">
                    <label class="toggle schedule-toggle">
                        <input type="checkbox" ${schedule.enabled ? 'checked' : ''}
                               onchange="toggleSchedule(${schedule.id}, this.checked)">
                        <span class="toggle-slider"></span>
                    </label>
                    <button class="btn btn-small" onclick="editSchedule(${schedule.id})">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteSchedule(${schedule.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

function formatTime(time24) {
    const [hours, minutes] = time24.split(':');
    const h = parseInt(hours);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 || 12;
    return `${h12}:${minutes} ${ampm}`;
}

async function toggleSchedule(id, enabled) {
    try {
        await apiCall(`/schedules/${id}`, 'PUT', { enabled });
        showToast(`Schedule ${enabled ? 'enabled' : 'disabled'}`, 'success');
        loadSchedules();
        loadSchedulerStatus();
    } catch (error) {
        loadSchedules(); // Revert on error
    }
}

async function deleteSchedule(id) {
    if (!confirm('Are you sure you want to delete this schedule?')) {
        return;
    }

    try {
        await apiCall(`/schedules/${id}`, 'DELETE');
        showToast('Schedule deleted', 'success');
        loadSchedules();
        loadSchedulerStatus();
    } catch (error) {
        // Error already shown
    }
}

// Modal Functions

function openAddModal() {
    currentEditingId = null;
    document.getElementById('modal-title').textContent = 'Add Schedule';
    clearForm();
    showModal();
}

function editSchedule(id) {
    currentEditingId = id;
    const schedule = schedules.find(s => s.id === id);

    if (!schedule) return;

    document.getElementById('modal-title').textContent = 'Edit Schedule';
    document.getElementById('schedule-name').value = schedule.name;
    document.getElementById('schedule-time').value = schedule.time;

    // Set days
    document.querySelectorAll('.day-checkbox input').forEach(cb => {
        cb.checked = schedule.days.includes(cb.value);
    });

    // Set actions
    if (schedule.action.power !== undefined) {
        document.getElementById('action-power').value = schedule.action.power ? 'on' : 'off';
    }
    if (schedule.action.mode) {
        document.getElementById('action-mode').value = schedule.action.mode;
    }
    if (schedule.action.temperature) {
        document.getElementById('action-temp').value = schedule.action.temperature;
    }
    if (schedule.action.fan_speed) {
        document.getElementById('action-fan').value = schedule.action.fan_speed;
    }

    showModal();
}

function showModal() {
    document.getElementById('schedule-modal').classList.add('show');
}

function closeModal() {
    document.getElementById('schedule-modal').classList.remove('show');
    clearForm();
}

function clearForm() {
    document.getElementById('schedule-name').value = '';
    document.getElementById('schedule-time').value = '';
    document.querySelectorAll('.day-checkbox input').forEach(cb => cb.checked = false);
    document.getElementById('action-power').value = '';
    document.getElementById('action-mode').value = '';
    document.getElementById('action-temp').value = '';
    document.getElementById('action-fan').value = '';
}

async function saveSchedule() {
    const name = document.getElementById('schedule-name').value.trim();
    const time = document.getElementById('schedule-time').value;

    if (!name) {
        showToast('Please enter a schedule name', 'error');
        return;
    }

    if (!time) {
        showToast('Please select a time', 'error');
        return;
    }

    // Get selected days
    const days = Array.from(document.querySelectorAll('.day-checkbox input:checked'))
        .map(cb => cb.value);

    // Build action
    const action = {};

    const power = document.getElementById('action-power').value;
    if (power) action.power = power === 'on';

    const mode = document.getElementById('action-mode').value;
    if (mode) action.mode = mode;

    const temp = document.getElementById('action-temp').value;
    if (temp) {
        action.temperature = parseInt(temp);
        action.fahrenheit = true;
    }

    const fan = document.getElementById('action-fan').value;
    if (fan) action.fan_speed = parseInt(fan);

    if (Object.keys(action).length === 0) {
        showToast('Please specify at least one action', 'error');
        return;
    }

    const scheduleData = {
        name,
        time,
        days,
        action,
        created_at: new Date().toISOString()
    };

    try {
        if (currentEditingId) {
            await apiCall(`/schedules/${currentEditingId}`, 'PUT', scheduleData);
            showToast('Schedule updated', 'success');
        } else {
            await apiCall('/schedules', 'POST', scheduleData);
            showToast('Schedule created', 'success');
        }

        closeModal();
        loadSchedules();
        loadSchedulerStatus();
    } catch (error) {
        // Error already shown
    }
}

// UI Helpers

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Make functions globally available for inline handlers
window.toggleSchedule = toggleSchedule;
window.editSchedule = editSchedule;
window.deleteSchedule = deleteSchedule;
