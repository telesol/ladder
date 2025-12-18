// Bitcoin Puzzle Ladder - Frontend JavaScript

let currentStatus = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadGPUStats();
    loadStatus();
    loadSystemHealth();  // Load health status
    loadProgressDashboard();  // Load progress & learning
    setupEventListeners();
    loadChatHistory();  // Load persistent chat history
    loadAvailableModels();  // Load model selector

    // Auto-refresh GPU stats every 5 seconds
    setInterval(loadGPUStats, 5000);
    // Auto-refresh health every 30 seconds
    setInterval(loadSystemHealth, 30000);
    // Auto-refresh progress every 60 seconds
    setInterval(loadProgressDashboard, 60000);
});

// Load available models for the selector
async function loadAvailableModels() {
    const modelSelect = document.getElementById('model-select');
    const modelStatus = document.getElementById('model-status');

    try {
        const response = await fetch('/api/models/available');
        const data = await response.json();

        if (data.success && data.models && data.models.length > 0) {
            modelSelect.innerHTML = data.models.map(model =>
                `<option value="${escapeHtml(model)}" ${model === data.current_model ? 'selected' : ''}>${escapeHtml(model)}</option>`
            ).join('');

            modelStatus.textContent = 'Connected';
            modelStatus.style.background = 'var(--success)';

            // Add change listener
            modelSelect.addEventListener('change', async (e) => {
                const selectedModel = e.target.value;
                modelStatus.textContent = 'Switching...';
                modelStatus.style.background = 'var(--secondary)';

                try {
                    const resp = await fetch('/api/models/select', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model: selectedModel })
                    });
                    const result = await resp.json();

                    if (result.success) {
                        modelStatus.textContent = 'Connected';
                        modelStatus.style.background = 'var(--success)';
                        displayChatMessage('assistant', `Model changed to **${selectedModel}**`);
                    } else {
                        modelStatus.textContent = 'Error';
                        modelStatus.style.background = 'var(--danger)';
                    }
                } catch (err) {
                    modelStatus.textContent = 'Error';
                    modelStatus.style.background = 'var(--danger)';
                }
            });
        } else {
            modelSelect.innerHTML = '<option value="">No models available</option>';
            modelStatus.textContent = 'No Models';
            modelStatus.style.background = 'var(--danger)';
        }
    } catch (error) {
        modelSelect.innerHTML = '<option value="">Connection failed</option>';
        modelStatus.textContent = 'Offline';
        modelStatus.style.background = 'var(--danger)';
    }
}

function setupEventListeners() {
    // Enter key on model search
    document.getElementById('model-search-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchModels();
    });

    // Enter key on chat input
    document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
}

// Load GPU statistics
async function loadGPUStats() {
    try {
        const response = await fetch('/api/gpu-stats');
        const data = await response.json();

        if (data.success || data.gpus) {
            displayGPUStats(data);
        } else {
            document.getElementById('gpu-stats').innerHTML =
                '<p>⚠️ GPU monitoring unavailable: ' + (data.error || 'Unknown error') + '</p>';
        }
    } catch (error) {
        document.getElementById('gpu-stats').innerHTML =
            '<p>⚠️ Error loading GPU stats</p>';
    }
}

// Display GPU statistics
function displayGPUStats(data) {
    const container = document.getElementById('gpu-stats');

    if (!data.gpus || data.gpus.length === 0) {
        container.innerHTML = '<p>No GPUs detected</p>';
        return;
    }

    let html = '<div class="gpu-grid" style="display: grid; gap: 1rem;">';

    data.gpus.forEach(gpu => {
        const memUsedPercent = (gpu.memory_total > 0) ? (gpu.memory_used / gpu.memory_total * 100).toFixed(1) : 0;
        const memFreeGB = (gpu.memory_free / 1024).toFixed(1);
        const isUnified = gpu.unified_memory || data.unified_memory;

        // Memory display
        let memoryDisplay = '';
        if (gpu.memory_total > 0) {
            // Format memory in GB
            let memUsedStr = (gpu.memory_used / 1024).toFixed(1) + ' GB';
            let memTotalStr = (gpu.memory_total / 1024).toFixed(1) + ' GB';
            let memFreeStr = (gpu.memory_free / 1024).toFixed(1) + ' GB';

            const memLabel = isUnified ? 'Unified Memory' : 'VRAM';
            const memColor = memUsedPercent > 80 ? 'var(--danger)' : memUsedPercent > 60 ? '#f0ad4e' : 'var(--primary)';

            memoryDisplay = `
                <div style="grid-column: span 2;">
                    <strong>${memLabel}:</strong> ${isUnified ? '<span class="badge" style="background: #17a2b8; color: white; font-size: 0.7rem; margin-left: 5px;">Shared with CPU</span>' : ''}
                    <div class="progress-bar" style="height: 24px; margin-top: 4px;">
                        <div class="progress-fill" style="width: ${memUsedPercent}%; background: ${memColor}"></div>
                        <span style="font-size: 0.85rem;">${memUsedStr} used / ${memTotalStr} total (${memFreeStr} free)</span>
                    </div>
                </div>`;
        } else {
            memoryDisplay = `
                <div style="grid-column: span 2;">
                    <strong>VRAM:</strong> <span class="badge" style="background: var(--secondary); color: white;">Monitoring N/A</span>
                </div>`;
        }

        // Power display (handle N/A case)
        let powerDisplay = '';
        if (gpu.power_limit > 0) {
            powerDisplay = `<strong>Power:</strong> ${gpu.power_draw.toFixed(1)}W / ${gpu.power_limit.toFixed(0)}W`;
        } else {
            powerDisplay = `<strong>Power:</strong> ${gpu.power_draw.toFixed(1)}W`;
        }

        html += `
            <div class="gpu-card" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--primary);">
                <h3 style="margin-bottom: 0.5rem;">GPU ${gpu.index}: ${gpu.name}</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; font-size: 0.9rem;">
                    ${memoryDisplay}
                    <div>
                        <strong>GPU Util:</strong>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${gpu.gpu_util}%; background: ${gpu.gpu_util > 80 ? 'var(--danger)' : 'var(--success)'}"></div>
                            <span>${gpu.gpu_util}%</span>
                        </div>
                    </div>
                    <div>
                        <strong>Temperature:</strong> <span class="badge ${gpu.temperature > 80 ? 'badge-error' : gpu.temperature > 60 ? 'badge-warning' : 'badge-success'}">${gpu.temperature}°C</span>
                    </div>
                    <div>
                        ${powerDisplay}
                    </div>
                    <div>
                        <strong>Free:</strong> <span class="badge" style="background: ${memFreeGB > 50 ? 'var(--success)' : memFreeGB > 20 ? '#f0ad4e' : 'var(--danger)'}; color: white;">${memFreeGB} GB available</span>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

// Load system status
async function loadStatus() {
    try {
        showLoading('status-content');

        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.success) {
            currentStatus = data;
            displayStatus(data);
            displayPuzzleGrid(data.database);
            displayCalibration(data.calibration, data.drift_stats);
        } else {
            showError('status-content', data.error);
        }
    } catch (error) {
        showError('status-content', error.message);
    }
}

// Display status overview
function displayStatus(data) {
    // Verification stats
    const verification = data.verification || {};
    const accuracy = verification.accuracy || 'N/A';
    const isPerfect = verification.perfect === true;
    const accuracyColor = isPerfect ? 'var(--success)' : 'var(--danger)';

    // Drift stats
    const driftStats = data.drift_stats || {};
    const lanes100 = driftStats.lanes_at_100pct || 0;

    const html = `
        <div class="stats">
            <div class="stat-box" style="border-left: 4px solid ${accuracyColor};">
                <h4>🎯 Verification Accuracy</h4>
                <div class="value" style="color: ${accuracyColor}; font-size: 1.5rem;">${accuracy}</div>
                <small>${isPerfect ? '✅ Perfect!' : '⚠️ Needs calibration'}</small>
            </div>
            <div class="stat-box">
                <h4>📊 Total Puzzles</h4>
                <div class="value">${data.database.total_puzzles}</div>
                <small>Solved in database</small>
            </div>
            <div class="stat-box">
                <h4>🔗 Consecutive</h4>
                <div class="value">${data.database.consecutive.length}</div>
                <small>Puzzles 1-70</small>
            </div>
            <div class="stat-box">
                <h4>🌉 Bridge Puzzles</h4>
                <div class="value">${data.database.bridges.length}</div>
                <small>${data.database.bridges.join(', ')}</small>
            </div>
            <div class="stat-box">
                <h4>❓ Unsolved Gaps</h4>
                <div class="value">${data.database.missing.length}</div>
                <small>71-74, 76-79, etc.</small>
            </div>
            <div class="stat-box" style="border-left: 4px solid ${lanes100 >= 7 ? 'var(--success)' : 'var(--secondary)'};">
                <h4>🔬 Drift Discovery</h4>
                <div class="value">${lanes100}/16</div>
                <small>Lanes at 100% C consistency</small>
            </div>
        </div>
    `;
    document.getElementById('status-content').innerHTML = html;
}

// Display puzzle grid visualization
function displayPuzzleGrid(database) {
    const grid = document.getElementById('puzzle-grid');
    const stats = document.getElementById('db-stats');

    let html = '';
    const solvedPuzzles = new Set(database.puzzles);  // Puzzles with actual keys
    const bridges = new Set(database.bridges);
    const consecutive = new Set(database.consecutive);
    const unsolved = new Set(database.unsolved || []);  // Puzzles with '0x?' placeholder

    // Show all 160 puzzles (the full Bitcoin Puzzle range)
    for (let i = 1; i <= 160; i++) {
        let cssClass = 'puzzle-cell';
        let title = `Puzzle ${i}`;

        if (solvedPuzzles.has(i)) {
            if (bridges.has(i)) {
                cssClass += ' bridge';
                title += ' (Bridge - SOLVED)';
            } else if (consecutive.has(i)) {
                cssClass += ' has-data';
                title += ' (SOLVED)';
            } else {
                cssClass += ' has-data';
                title += ' (SOLVED)';
            }
        } else {
            cssClass += ' missing';
            title += ' (UNSOLVED - target)';
        }

        html += `<div class="${cssClass}" title="${title}" onclick="showPuzzleDetails(${i})">${i}</div>`;
    }

    grid.innerHTML = html;

    // Count statistics
    const solvedCount = database.puzzles.length;
    const unsolvedCount = (database.unsolved || []).length;
    const missingCount = (database.missing || []).length;

    // Legend with counts
    stats.innerHTML = `
        <div style="display: flex; gap: 2rem; flex-wrap: wrap; align-items: center;">
            <div><span class="puzzle-cell has-data" style="display: inline-block; width: 20px; height: 20px;"></span> Solved Consecutive (${database.consecutive.length})</div>
            <div><span class="puzzle-cell bridge" style="display: inline-block; width: 20px; height: 20px;"></span> Solved Bridges (${database.bridges.length})</div>
            <div><span class="puzzle-cell missing" style="display: inline-block; width: 20px; height: 20px;"></span> Unsolved (${unsolvedCount})</div>
            <div style="margin-left: auto; font-weight: bold;">Total: ${solvedCount}/160 solved</div>
        </div>
    `;
}

// Display calibration status
function displayCalibration(calibration, driftStats) {
    const container = document.getElementById('calibration-status');

    // Get drift suggestions from the status if available
    const suggested = (driftStats && driftStats.suggested_drift) || {};

    // A matrix with drift analysis
    let aHtml = '<h3>A Matrix & Drift Analysis</h3><div class="calibration-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem;">';
    for (let i = 0; i < 16; i++) {
        const aValue = calibration.a_matrix[i.toString()];
        const cstarBlock0 = calibration.cstar['0'] || {};
        const cValue = cstarBlock0[i.toString()] || [0, 0];
        const currentC = Array.isArray(cValue) ? cValue[0] : cValue;

        // Get suggested drift
        const suggestedData = suggested[i.toString()] || {};
        const suggestedC = suggestedData.value !== undefined ? suggestedData.value : '?';
        const pct = suggestedData.percentage || '?';
        const isConsistent = pct === '100.0%';

        const bgColor = isConsistent ? 'rgba(40, 167, 69, 0.1)' : 'rgba(255, 193, 7, 0.1)';
        const borderColor = isConsistent ? 'var(--success)' : 'var(--secondary)';

        aHtml += `
            <div class="lane-info" style="background: ${bgColor}; border-left: 3px solid ${borderColor}; padding: 0.5rem;">
                <strong>Lane ${i}</strong><br>
                <small>A = ${aValue}</small><br>
                <small>C = ${currentC} ${isConsistent ? '✓' : ''}</small><br>
                <small style="color: #666;">Best: ${suggestedC} (${pct})</small>
            </div>`;
    }
    aHtml += '</div>';

    // Cstar summary
    let cstarHtml = `
        <h3 style="margin-top: 1rem;">Calibration Summary</h3>
        <p>Non-zero drifts in calibration: <span class="badge ${calibration.nonzero_drifts > 0 ? 'badge-success' : 'badge-warning'}">${calibration.nonzero_drifts} / 32</span></p>
        <p><small>💡 <em>Lanes 9-15 show 100% consistency with C=0. Lane 0 has variable C values (no single constant works).</em></small></p>
    `;

    container.innerHTML = aHtml + cstarHtml;
}

// Show puzzle details
async function showPuzzleDetails(puzzleNum) {
    try {
        const response = await fetch(`/api/puzzles/${puzzleNum}`);
        const data = await response.json();

        if (data.success) {
            const message = data.in_database
                ? `Puzzle ${data.bits}:\n${data.hex}`
                : `Puzzle ${puzzleNum} is NOT in the database (needs to be generated)`;
            alert(message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Run verification
async function runVerification() {
    const resultsDiv = document.getElementById('verify-results');
    resultsDiv.className = 'results show processing';
    resultsDiv.innerHTML = '<div class="loading">Running verification... This may take a moment.</div>';

    try {
        const response = await fetch('/api/verify', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            const isPerfect = data.verification_passed;
            const cssClass = isPerfect ? 'success' : 'error';

            resultsDiv.className = `results show ${cssClass}`;
            resultsDiv.innerHTML = `
                <h4>${isPerfect ? '✅ SUCCESS!' : '⚠️ Verification Failed'}</h4>
                ${data.forward_percentage !== null ? `
                    <div class="percentage ${isPerfect ? 'perfect' : 'imperfect'}">
                        Forward: ${data.forward_percentage}%<br>
                        Reverse: ${data.reverse_percentage}%
                    </div>
                ` : ''}
                <pre>${escapeHtml(data.output)}</pre>
                ${!isPerfect ? '<p><strong>Next step:</strong> Compute missing drift (Phase 2)</p>' : '<p><strong>Next step:</strong> Generate puzzle 71 (Phase 5)</p>'}
            `;
        } else {
            resultsDiv.className = 'results show error';
            resultsDiv.innerHTML = `<h4>❌ Error</h4><p>${escapeHtml(data.error)}</p>`;
        }
    } catch (error) {
        resultsDiv.className = 'results show error';
        resultsDiv.innerHTML = `<h4>❌ Error</h4><p>${escapeHtml(error.message)}</p>`;
    }
}

// Compute drift
async function computeDrift() {
    const resultsDiv = document.getElementById('drift-results');
    resultsDiv.className = 'results show processing';
    resultsDiv.innerHTML = '<div class="loading">Computing drift C[0][ℓ][0]... This may take a moment.</div>';

    try {
        const response = await fetch('/api/compute-drift', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            resultsDiv.className = 'results show success';
            let driftHtml = '';
            if (data.drift && data.drift.C0_0) {
                driftHtml = `
                    <h4>Computed Drift Values:</h4>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin: 1rem 0;">
                        ${data.drift.C0_0.map((v, i) => `<div class="lane-info">Lane ${i}: ${v}</div>`).join('')}
                    </div>
                `;
            }
            resultsDiv.innerHTML = `
                <h4>✅ Drift Computed Successfully!</h4>
                <p>HEX75: <code>${data.hex75}</code></p>
                <p>HEX80: <code>${data.hex80}</code></p>
                ${driftHtml}
                <pre>${escapeHtml(data.output)}</pre>
                <p><strong>Next step:</strong> Patch calibration (Phase 3)</p>
            `;
        } else {
            resultsDiv.className = 'results show error';
            resultsDiv.innerHTML = `<h4>❌ Error</h4><pre>${escapeHtml(data.output || data.error)}</pre>`;
        }
    } catch (error) {
        resultsDiv.className = 'results show error';
        resultsDiv.innerHTML = `<h4>❌ Error</h4><p>${escapeHtml(error.message)}</p>`;
    }
}

// Patch calibration
async function patchCalibration() {
    const resultsDiv = document.getElementById('patch-results');
    resultsDiv.className = 'results show processing';
    resultsDiv.innerHTML = '<div class="loading">Patching calibration file...</div>';

    try {
        const response = await fetch('/api/patch-calibration', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            resultsDiv.className = 'results show success';
            resultsDiv.innerHTML = `
                <h4>✅ Calibration Patched Successfully!</h4>
                <pre>${escapeHtml(data.output)}</pre>
                <p><strong>Next step:</strong> Re-verify to confirm 100% (Phase 4)</p>
            `;
            // Reload status
            loadStatus();
        } else {
            resultsDiv.className = 'results show error';
            resultsDiv.innerHTML = `<h4>❌ Error</h4><pre>${escapeHtml(data.output || data.error)}</pre>`;
        }
    } catch (error) {
        resultsDiv.className = 'results show error';
        resultsDiv.innerHTML = `<h4>❌ Error</h4><p>${escapeHtml(error.message)}</p>`;
    }
}

// Generate puzzle
async function generatePuzzle() {
    const resultsDiv = document.getElementById('generate-results');
    resultsDiv.className = 'results show processing';
    resultsDiv.innerHTML = '<div class="loading">Generating puzzle 71...</div>';

    try {
        const response = await fetch('/api/generate', { method: 'POST' });
        const data = await response.json();

        if (data.success && data.generated_hex) {
            resultsDiv.className = 'results show success';
            resultsDiv.innerHTML = `
                <h4>✅ Puzzle Generated!</h4>
                <p><strong>Generated Private Key (Puzzle 71):</strong></p>
                <pre>0x${data.generated_hex}</pre>
                <pre>${escapeHtml(data.output)}</pre>
                <button class="btn btn-primary" onclick="copyToClipboard('0x${data.generated_hex}')">📋 Copy Private Key</button>
                <p style="margin-top: 1rem;"><strong>Next step:</strong> Validate this address (Phase 6)</p>
            `;
            // Auto-fill the input
            document.getElementById('privkey-input').value = '0x' + data.generated_hex;
        } else {
            resultsDiv.className = 'results show error';
            resultsDiv.innerHTML = `<h4>❌ Error</h4><pre>${escapeHtml(data.output || data.error)}</pre>`;
        }
    } catch (error) {
        resultsDiv.className = 'results show error';
        resultsDiv.innerHTML = `<h4>❌ Error</h4><p>${escapeHtml(error.message)}</p>`;
    }
}

// Validate address
async function validateAddress() {
    const privkeyInput = document.getElementById('privkey-input');
    const puzzleNumInput = document.getElementById('puzzle-num-input');
    const resultsDiv = document.getElementById('validate-results');

    const privkeyHex = privkeyInput.value.trim();
    const puzzleNum = parseInt(puzzleNumInput.value);

    if (!privkeyHex) {
        alert('Please enter a private key');
        return;
    }

    resultsDiv.className = 'results show processing';
    resultsDiv.innerHTML = '<div class="loading">Validating address... Deriving Bitcoin address and comparing...</div>';

    try {
        const response = await fetch('/api/validate-address', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ privkey_hex: privkeyHex, puzzle_num: puzzleNum })
        });
        const data = await response.json();

        if (data.success) {
            const cssClass = data.validation_passed ? 'success' : 'error';
            resultsDiv.className = `results show ${cssClass}`;

            if (data.validation_passed) {
                resultsDiv.innerHTML = `
                    <h4>✅✅✅ MATCH! THE PRIVATE KEY IS CORRECT! ✅✅✅</h4>
                    <div style="text-align: center; font-size: 3rem; margin: 2rem 0;">🎉</div>
                    <p style="font-size: 1.2rem; text-align: center;"><strong>SUCCESS! You generated a correct unknown private key!</strong></p>
                    <p style="text-align: center;">The ladder mathematics is PROVEN for puzzle ${puzzleNum}!</p>
                    <pre>${escapeHtml(data.output)}</pre>
                `;
            } else {
                resultsDiv.innerHTML = `
                    <h4>❌ Address Mismatch</h4>
                    <p>The addresses do not match. Check the cryptographic rules:</p>
                    <ul>
                        <li>Big-endian byte order</li>
                        <li>Compressed public key (33 bytes)</li>
                        <li>SHA256 → RIPEMD160 hash sequence</li>
                        <li>Version byte 0x00</li>
                        <li>Base58Check encoding</li>
                    </ul>
                    <pre>${escapeHtml(data.output)}</pre>
                `;
            }
        } else {
            resultsDiv.className = 'results show error';
            resultsDiv.innerHTML = `<h4>❌ Error</h4><pre>${escapeHtml(data.output || data.error)}</pre>`;
        }
    } catch (error) {
        resultsDiv.className = 'results show error';
        resultsDiv.innerHTML = `<h4>❌ Error</h4><p>${escapeHtml(error.message)}</p>`;
    }
}

// Show documentation
async function showDoc(docName) {
    const docViewer = document.getElementById('doc-content');
    docViewer.innerHTML = '<div class="loading">Loading documentation...</div>';

    try {
        const response = await fetch(`/api/documentation/${docName}`);
        const data = await response.json();

        if (data.success) {
            // Simple markdown rendering (you could use a library like marked.js for better rendering)
            const html = data.content
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/^### (.+)$/gm, '<h4>$1</h4>')
                .replace(/^## (.+)$/gm, '<h3>$1</h3>')
                .replace(/^# (.+)$/gm, '<h2>$1</h2>')
                .replace(/```([^`]+)```/g, '<pre>$1</pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                .replace(/\n\n/g, '<br><br>');

            docViewer.innerHTML = html;
        } else {
            docViewer.innerHTML = `<p>Error: ${data.error}</p>`;
        }
    } catch (error) {
        docViewer.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}

// Helper functions
function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = '<div class="loading">Loading...</div>';
}

function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `<div class="error">Error: ${escapeHtml(message)}</div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        alert('Failed to copy: ' + err);
    });
}

// Search AI models
async function searchModels() {
    const searchInput = document.getElementById('model-search-input');
    const resultsDiv = document.getElementById('model-results');
    const query = searchInput.value.trim() || 'qwen';

    resultsDiv.innerHTML = '<div class="loading">Searching models...</div>';

    try {
        const response = await fetch(`/api/models/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.models) {
            let html = '<div class="model-list" style="margin-top: 1rem;">';

            if (data.models.length === 0) {
                html += '<p>No models found for "' + escapeHtml(query) + '"</p>';
            } else {
                data.models.forEach(model => {
                    html += `
                        <div class="model-card" style="background: var(--light); padding: 1rem; margin-bottom: 1rem; border-radius: 8px; border-left: 4px solid var(--secondary);">
                            <h4 style="margin-bottom: 0.5rem;">${escapeHtml(model.name)}</h4>
                            <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                                <span class="badge badge-success">${escapeHtml(model.size)}</span>
                                <span class="badge" style="background: var(--primary); color: white;">${escapeHtml(model.type)}</span>
                            </div>
                            <p style="margin-bottom: 0.5rem;">${escapeHtml(model.description)}</p>
                            <a href="${escapeHtml(model.url)}" target="_blank" class="btn btn-link">View on Hugging Face →</a>
                        </div>
                    `;
                });
            }

            html += '</div>';
            resultsDiv.innerHTML = html;
        } else {
            resultsDiv.innerHTML = '<p>Error searching models</p>';
        }
    } catch (error) {
        resultsDiv.innerHTML = '<p>Error: ' + escapeHtml(error.message) + '</p>';
    }
}

// Load chat history from persistent storage
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/history');
        const data = await response.json();

        if (data.history && data.history.length > 0) {
            // Clear the default welcome message
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.innerHTML = '';

            // Display each historical message
            data.history.forEach(msg => {
                displayChatMessage(msg.role, msg.content, msg.action, msg.data);
            });

            // Add a separator to show where history ends
            const separatorDiv = document.createElement('div');
            separatorDiv.className = 'chat-separator';
            separatorDiv.innerHTML = '<span>— Previous conversation restored —</span>';
            separatorDiv.style.cssText = 'text-align: center; color: #888; font-size: 0.8rem; margin: 1rem 0; border-top: 1px dashed #ccc; padding-top: 0.5rem;';
            messagesContainer.appendChild(separatorDiv);

            // Auto-scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    } catch (error) {
        console.log('Could not load chat history:', error);
    }
}

// Chat state
let currentAbortController = null;
let lastUserMessage = null;
let isGenerating = false;

// Chat functionality
async function sendChatMessage(retryMessage = null) {
    const chatInput = document.getElementById('chat-input');
    const message = retryMessage || chatInput.value.trim();
    const useRag = document.getElementById('use-rag')?.checked ?? true;

    if (!message) return;

    // Store last message for retry
    lastUserMessage = message;

    // Display user message (only if not retrying)
    if (!retryMessage) {
        displayChatMessage('user', message);
        chatInput.value = '';
    }

    // Show typing indicator and update buttons
    showTypingIndicator();
    setGeneratingState(true);

    // Create abort controller for this request
    currentAbortController = new AbortController();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, use_rag: useRag }),
            signal: currentAbortController.signal
        });

        const data = await response.json();

        // Hide typing indicator
        hideTypingIndicator();
        setGeneratingState(false);

        // Display assistant response
        if (data.message) {
            // Pass action and data for visibility
            displayChatMessage('assistant', data.message, data.action_taken || data.action_needed, data.data);

            // Handle special actions if needed
            if (data.action_needed) {
                handleChatAction(data);
            }
        } else if (data.error) {
            displayChatMessage('assistant', '❌ Error: ' + data.error);
        }
    } catch (error) {
        hideTypingIndicator();
        setGeneratingState(false);

        if (error.name === 'AbortError') {
            displayChatMessage('assistant', '⏹️ Generation stopped by user.');
        } else {
            displayChatMessage('assistant', '❌ Error connecting to chat agent: ' + error.message);
        }
    }

    currentAbortController = null;
}

// Stop current generation
function stopGeneration() {
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
    }
    hideTypingIndicator();
    setGeneratingState(false);
}

// Retry last message
function retryLastMessage() {
    if (!lastUserMessage) {
        alert('No previous message to retry');
        return;
    }

    // Remove the last assistant message from the UI
    const messagesContainer = document.getElementById('chat-messages');
    const messages = messagesContainer.querySelectorAll('.chat-message.assistant');
    if (messages.length > 0) {
        const lastAssistantMsg = messages[messages.length - 1];
        lastAssistantMsg.remove();
    }

    // Resend the last user message
    sendChatMessage(lastUserMessage);
}

// Update UI state during generation
function setGeneratingState(generating) {
    isGenerating = generating;
    const sendBtn = document.getElementById('send-btn');
    const stopBtn = document.getElementById('stop-btn');
    const retryBtn = document.getElementById('retry-btn');
    const chatInput = document.getElementById('chat-input');

    if (generating) {
        sendBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        retryBtn.style.display = 'none';
        chatInput.disabled = true;
    } else {
        sendBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        retryBtn.style.display = lastUserMessage ? 'inline-block' : 'none';
        chatInput.disabled = false;
        chatInput.focus();
    }
}

function displayChatMessage(role, content, action = null, data = null) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (role === 'user') {
        contentDiv.innerHTML = `<strong>You:</strong> ${escapeHtml(content)}`;
    } else {
        // For assistant messages, preserve formatting and markdown-like text
        const formattedContent = content
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        let actionBadge = '';
        if (action && action !== 'chat') {
            actionBadge = `<span class="action-badge" style="display: inline-block; background: #4a90d9; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; margin-left: 8px;">⚡ ${escapeHtml(action)}</span>`;
        }

        contentDiv.innerHTML = `<strong>Chattie:</strong>${actionBadge} ${formattedContent}`;

        // Show command output if present
        if (data && data.output) {
            const outputDiv = document.createElement('div');
            outputDiv.className = 'command-output';
            outputDiv.style.cssText = 'background: #1e1e1e; color: #0f0; font-family: monospace; font-size: 0.8rem; padding: 8px; margin-top: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; white-space: pre-wrap;';
            outputDiv.innerHTML = `<div style="color: #888; margin-bottom: 4px;">📟 Command Output:</div>${escapeHtml(data.output)}`;
            contentDiv.appendChild(outputDiv);
        }
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Auto-scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message assistant';
    typingDiv.id = 'typing-indicator';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    typingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(typingDiv);

    // Auto-scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function handleChatAction(data) {
    // Handle specific actions that the chat agent recommends
    if (data.action_needed === 'compute_drift') {
        // Could auto-trigger or just show a notification
        console.log('Agent suggests computing drift');
    } else if (data.action_needed === 'generate_puzzle') {
        console.log('Agent suggests generating puzzle');
    } else if (data.action_needed === 'search_models' && data.query) {
        // Auto-trigger model search
        document.getElementById('model-search-input').value = data.query;
        setTimeout(() => searchModels(), 500);
    }
}

// Quick action buttons - send predefined commands to chat
function quickAction(command) {
    const chatInput = document.getElementById('chat-input');
    chatInput.value = command;
    sendChatMessage();
}

// Load system health status
async function loadSystemHealth() {
    const container = document.getElementById('health-content');
    if (!container) return;

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.success) {
            displaySystemHealth(data.health);
        } else {
            container.innerHTML = '<p>Error loading health status</p>';
        }
    } catch (error) {
        container.innerHTML = '<p>Error: ' + escapeHtml(error.message) + '</p>';
    }
}

// Display system health status
function displaySystemHealth(health) {
    const container = document.getElementById('health-content');

    const daemonStatus = health.daemon || {};
    const ollamaStatus = health.ollama || {};
    const dbStatus = health.database || {};
    const memStatus = health.memory || {};

    const daemonColor = daemonStatus.active ? 'var(--success)' : 'var(--danger)';
    const ollamaColor = ollamaStatus.status === 'connected' ? 'var(--success)' : 'var(--danger)';
    const dbColor = dbStatus.status === 'healthy' ? 'var(--success)' : 'var(--danger)';
    const memColor = memStatus.status === 'healthy' ? 'var(--success)' : 'var(--danger)';

    container.innerHTML = `
        <div class="health-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div class="health-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid ${daemonColor};">
                <h4 style="margin: 0 0 0.5rem 0;">🤖 Autonomous Daemon</h4>
                <span class="badge" style="background: ${daemonColor}; color: white;">${daemonStatus.status || 'unknown'}</span>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">ladder.service</p>
            </div>
            <div class="health-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid ${ollamaColor};">
                <h4 style="margin: 0 0 0.5rem 0;">🦙 Ollama</h4>
                <span class="badge" style="background: ${ollamaColor}; color: white;">${ollamaStatus.status || 'unknown'}</span>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">${ollamaStatus.models || 0} models available</p>
            </div>
            <div class="health-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid ${dbColor};">
                <h4 style="margin: 0 0 0.5rem 0;">🗄️ Database</h4>
                <span class="badge" style="background: ${dbColor}; color: white;">${dbStatus.status || 'unknown'}</span>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">${dbStatus.puzzles || 0}/160 puzzles</p>
            </div>
            <div class="health-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid ${memColor};">
                <h4 style="margin: 0 0 0.5rem 0;">🧠 Memory System</h4>
                <span class="badge" style="background: ${memColor}; color: white;">${memStatus.status || 'unknown'}</span>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">${memStatus.discoveries || 0} discoveries, ${memStatus.learnings || 0} learnings</p>
            </div>
        </div>
    `;
}

// Load progress dashboard
async function loadProgressDashboard() {
    const container = document.getElementById('progress-content');
    if (!container) return;

    try {
        const response = await fetch('/api/progress');
        const data = await response.json();

        if (data.success) {
            displayProgressDashboard(data.progress);
        } else {
            container.innerHTML = '<p>Error loading progress data</p>';
        }
    } catch (error) {
        container.innerHTML = '<p>Error: ' + escapeHtml(error.message) + '</p>';
    }
}

// Display progress dashboard
function displayProgressDashboard(progress) {
    const container = document.getElementById('progress-content');

    const successRate = (progress.success_rate * 100).toFixed(1);
    const rateColor = progress.success_rate > 0.5 ? 'var(--success)' : progress.success_rate > 0.2 ? '#f0ad4e' : 'var(--danger)';
    const learningColor = progress.total_learnings > 0 ? 'var(--success)' : 'var(--secondary)';

    // Build learning topics display
    let topicsHtml = '';
    if (progress.learning_topics && Object.keys(progress.learning_topics).length > 0) {
        topicsHtml = '<div style="margin-top: 0.5rem; font-size: 0.85rem;">';
        for (const [topic, count] of Object.entries(progress.learning_topics)) {
            topicsHtml += `<span class="badge" style="background: var(--secondary); color: white; margin-right: 0.25rem; margin-bottom: 0.25rem; display: inline-block;">${escapeHtml(topic)}: ${count}</span>`;
        }
        topicsHtml += '</div>';
    }

    // Build recent learnings display
    let recentLearningsHtml = '';
    if (progress.recent_learnings && progress.recent_learnings.length > 0) {
        recentLearningsHtml = '<div style="margin-top: 1rem;"><h4 style="margin: 0 0 0.5rem 0;">Recent Learnings:</h4><ul style="margin: 0; padding-left: 1.5rem; font-size: 0.85rem;">';
        for (const learning of progress.recent_learnings.slice(0, 5)) {
            const confPercent = ((learning.confidence || 0) * 100).toFixed(0);
            recentLearningsHtml += `<li><strong>${escapeHtml(learning.topic || 'unknown')}:</strong> ${escapeHtml((learning.insight || '').slice(0, 100))}... <span style="color: #888;">(${confPercent}%)</span></li>`;
        }
        recentLearningsHtml += '</ul></div>';
    }

    container.innerHTML = `
        <div class="progress-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
            <div class="progress-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid ${rateColor};">
                <h4 style="margin: 0 0 0.5rem 0;">⚡ Success Rate</h4>
                <div style="font-size: 1.5rem; font-weight: bold; color: ${rateColor};">${successRate}%</div>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">${progress.successful_executions || 0}/${progress.strategy_executions || 0} strategies</p>
            </div>
            <div class="progress-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid ${learningColor};">
                <h4 style="margin: 0 0 0.5rem 0;">🎓 Learnings</h4>
                <div style="font-size: 1.5rem; font-weight: bold;">${progress.total_learnings || 0}</div>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">${progress.high_confidence_learnings || 0} high confidence</p>
            </div>
            <div class="progress-item" style="background: var(--light); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--primary);">
                <h4 style="margin: 0 0 0.5rem 0;">🔍 Discoveries</h4>
                <div style="font-size: 1.5rem; font-weight: bold;">${progress.total_discoveries || 0}</div>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">${progress.verified_discoveries || 0} verified</p>
            </div>
        </div>
        ${topicsHtml}
        ${recentLearningsHtml}
    `;
}
